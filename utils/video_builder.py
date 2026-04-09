import subprocess
import os
import math
from config import Config

class VideoBuilder:
    """Build YouTube Shorts from 10 images + audio with vertical effects"""
    
    @staticmethod
    def get_vertical_pan_params(index, total_images):
        """Generate Ken Burns params optimized for 9:16 vertical framing"""
        # Alternate zoom direction for visual rhythm
        zoom_start = Config.ZOOM_START if index % 2 == 0 else Config.ZOOM_END
        zoom_end = Config.ZOOM_END if index % 2 == 0 else Config.ZOOM_START
        
        # Cycle through vertical-friendly pan positions
        pan_pos = Config.PAN_VARIATIONS[index % len(Config.PAN_VARIATIONS)]
        
        # Vertical-aware coordinate expressions
        if pan_pos == 'center':
            x_expr = '(iw-iw/zoom)/2'
            y_expr = '(ih-ih/zoom)/2'
        elif pan_pos == 'top-center':
            x_expr = '(iw-iw/zoom)/2'
            y_expr = '0'
        elif pan_pos == 'bottom-center':
            x_expr = '(iw-iw/zoom)/2'
            y_expr = 'ih-ih/zoom'
        elif pan_pos == 'center-left':
            x_expr = '0'
            y_expr = '(ih-ih/zoom)/2'
        else:  # center-right
            x_expr = 'iw-iw/zoom'
            y_expr = '(ih-ih/zoom)/2'
        
        return zoom_start, zoom_end, x_expr, y_expr
    
    @staticmethod
    def build_shorts_command(image_paths, audio_path, output_path, captions=None):
        """
        Build FFmpeg command for YouTube Shorts:
        ✅ 1080x1920 vertical (9:16)
        ✅ ≤60 seconds total duration
        ✅ Ken Burns effects on each image
        ✅ Smooth crossfade transitions
        ✅ YouTube-optimized H.264 encoding
        ✅ Optional text captions per image
        """
        num_images = len(image_paths)
        transition = Config.TRANSITION_DURATION
        display_time = Config.IMAGE_DISPLAY_TIME
        total_duration = (display_time * num_images) + transition  # ~58s
        
        # Build input arguments and filter chain
        input_args = []
        filter_parts = []
        
        # Process each image with vertical scaling + Ken Burns
        for i, img_path in enumerate(image_paths):
            input_args.extend(['-loop', '1', '-i', img_path])
            
            zoom_start, zoom_end, x_expr, y_expr = VideoBuilder.get_vertical_pan_params(i, num_images)
            duration_frames = int(Config.FPS * (display_time + transition if i < num_images-1 else display_time))
            
            # Scale image to fill vertical frame (cover mode), then apply Ken Burns
            filter_parts.append(
                f"[{i}:v]scale={Config.OUTPUT_WIDTH}:{Config.OUTPUT_HEIGHT}:force_original_aspect_ratio=increase,"
                f"crop={Config.OUTPUT_WIDTH}:{Config.OUTPUT_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
                f"zoompan=z='linear({zoom_start},{zoom_end},{duration_frames})':"
                f"x='{x_expr}':y='{y_expr}':d={duration_frames}:fps={Config.FPS}[img{i}]"
            )
            
            # Optional: Add caption text overlay
            if captions and i < len(captions) and captions[i]:
                # Escape special characters for FFmpeg drawtext
                safe_text = captions[i].replace("'", r"\'").replace(":", r"\:")
                filter_parts.append(
                    f"[img{i}]drawtext=text='{safe_text}':fontfile={Config.CAPTION_FONT}:"
                    f"fontsize={Config.CAPTION_SIZE}:fontcolor={Config.CAPTION_COLOR}:"
                    f"box=1:boxcolor={Config.CAPTION_BOX_COLOR}:boxborderw=10:"
                    f"x=(w-text_w)/2:y=h-text_h-50[img{i}]"
                )
        
        # Add audio input
        input_args.extend(['-i', audio_path])
        audio_idx = num_images
        
        # Chain images with xfade transitions (Shorts-friendly fast cuts)
        current_label = "[img0]"
        for i in range(1, num_images):
            offset = (display_time + transition) * i - transition
            filter_parts.append(
                f"{current_label}[img{i}]xfade=transition=fade:duration={transition}:offset={offset}[x{i}]"
            )
            current_label = f"[x{i}]"
        
        final_video = current_label
        
        # Audio processing: trim to exact duration + fade in/out (critical for Shorts)
        filter_parts.append(
            f"[{audio_idx}:a]atrim=0:{total_duration},"
            f"afade=t=in:st=0:d={Config.AUDIO_FADE_IN},"
            f"afade=t=out:st={total_duration-Config.AUDIO_FADE_OUT}:d={Config.AUDIO_FADE_OUT},"
            f"aresample=48000[aout]"
        )
        
        filter_complex = ";".join(filter_parts)
        
        # 🎯 YouTube-optimized FFmpeg command
        cmd = [
            'ffmpeg', '-y',
            *input_args,
            '-filter_complex', filter_complex,
            '-map', final_video,
            '-map', '[aout]',
            
            # Video encoding (YouTube Shorts specs)
            '-c:v', Config.VIDEO_CODEC,
            '-preset', Config.PRESET,
            '-crf', str(Config.CRF),
            '-pix_fmt', 'yuv420p',      # Required for YouTube compatibility
            '-r', str(Config.FPS),
            '-maxrate', '10M',           # Prevent bitrate spikes
            '-bufsize', '20M',           # VBV buffer
            
            # Audio encoding
            '-c:a', Config.AUDIO_CODEC,
            '-b:a', Config.AUDIO_BITRATE,
            '-ar', Config.AUDIO_SAMPLE_RATE,
            '-movflags', '+faststart',   # Enable progressive streaming
            
            output_path
        ]
        
        return cmd, total_duration
    
    @staticmethod
    def build_simple_shorts_command(image_paths, audio_path, output_path):
        """
        Simpler version: sequential images without complex xfade chain
        More reliable for debugging or resource-constrained environments
        """
        num_images = len(image_paths)
        display_time = Config.IMAGE_DISPLAY_TIME
        total_duration = display_time * num_images
        
        input_args = []
        filter_parts = []
        
        for i, img_path in enumerate(image_paths):
            input_args.extend(['-loop', '1', '-t', str(display_time), '-i', img_path])
            zoom_start, zoom_end, x_expr, y_expr = VideoBuilder.get_vertical_pan_params(i, num_images)
            duration_frames = int(Config.FPS * display_time)
            
            filter_parts.append(
                f"[{i}:v]scale={Config.OUTPUT_WIDTH}:{Config.OUTPUT_HEIGHT}:force_original_aspect_ratio=increase,"
                f"crop={Config.OUTPUT_WIDTH}:{Config.OUTPUT_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
                f"zoompan=z='linear({zoom_start},{zoom_end},{duration_frames})':"
                f"x='{x_expr}':y='{y_expr}':d={duration_frames}:fps={Config.FPS}[v{i}]"
            )
        
        # Concatenate all processed clips
        concat_labels = "".join([f"[v{i}]" for i in range(num_images)])
        filter_parts.append(f"{concat_labels}concat=n={num_images}:v=1:a=0[video]")
        
        # Audio input + processing
        input_args.extend(['-i', audio_path])
        audio_idx = num_images
        filter_parts.append(
            f"[{audio_idx}:a]atrim=0:{total_duration},"
            f"afade=t=in:st=0:d={Config.AUDIO_FADE_IN},"
            f"afade=t=out:st={total_duration-Config.AUDIO_FADE_OUT}:d={Config.AUDIO_FADE_OUT},"
            f"aresample=48000[aout]"
        )
        
        filter_complex = ";".join(filter_parts)
        
        cmd = [
            'ffmpeg', '-y',
            *input_args,
            '-filter_complex', filter_complex,
            '-map', '[video]',
            '-map', '[aout]',
            '-c:v', Config.VIDEO_CODEC,
            '-preset', Config.PRESET,
            '-crf', str(Config.CRF),
            '-pix_fmt', 'yuv420p',
            '-r', str(Config.FPS),
            '-c:a', Config.AUDIO_CODEC,
            '-b:a', Config.AUDIO_BITRATE,
            '-ar', Config.AUDIO_SAMPLE_RATE,
            '-movflags', '+faststart',
            output_path
        ]
        
        return cmd, total_duration
    
    @staticmethod
    def run_command(cmd, timeout=120):
        """Execute FFmpeg with Shorts-appropriate timeout"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout  # Shorts render faster (~30-90s)
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"FFmpeg error: {e.stderr}"
        except subprocess.TimeoutExpired:
            return False, f"FFmpeg timed out after {timeout}s"
        except Exception as e:
            return False, f"Error: {str(e)}"