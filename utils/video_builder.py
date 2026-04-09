"""
YouTube Shorts Video Builder - FFmpeg Command Generator
Simplified for maximum reliability on serverless platforms
"""
import subprocess
import json
import os
from config import Config


class VideoBuilder:
    """Build videos from images + audio with Ken Burns effects"""
    
    @staticmethod
    def _get_audio_duration(audio_path):
        """Get audio duration in seconds using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_entries', 'format=duration', '-i', audio_path
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, 
                timeout=Config.FFPROBE_TIMEOUT, check=True
            )
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except Exception:
            # Fallback: estimate from number of images
            return Config.IMAGE_DISPLAY_TIME * 10 if hasattr(Config, 'IMAGE_DISPLAY_TIME') else 60.0
    
    @staticmethod
    def _get_ken_burns_filter(index, total_images, duration_frames):
        """Generate Ken Burns zoompan filter for one image"""
        # Alternate zoom direction for visual interest
        if index % 2 == 0:
            zoom_start, zoom_end = Config.ZOOM_MIN, Config.ZOOM_MAX
        else:
            zoom_start, zoom_end = Config.ZOOM_MAX, Config.ZOOM_MIN
        
        # Simple center pan (works reliably)
        x_expr = '(iw-iw/zoom)/2'
        y_expr = '(ih-ih/zoom)/2'
        
        return (
            f"zoompan=z='linear({zoom_start},{zoom_end},{duration_frames})':"
            f"x='{x_expr}':y='{y_expr}':d={duration_frames}:fps={Config.FPS}"
        )
    
    @staticmethod
    def build_simple_command(image_paths, audio_path, output_path):
        """
        Build a RELIABLE FFmpeg command:
        ✅ Sequential images with Ken Burns
        ✅ Audio trimmed to match total video duration
        ✅ YouTube-compatible encoding
        ✅ Memory-efficient for serverless
        """
        num_images = len(image_paths)
        audio_duration = VideoBuilder._get_audio_duration(audio_path)
        
        # Cap duration if needed
        if audio_duration > Config.MAX_AUDIO_DURATION:
            audio_duration = Config.MAX_AUDIO_DURATION
        
        # Calculate display time per image
        display_time = audio_duration / num_images
        duration_frames = int(Config.FPS * display_time)
        
        input_args = []
        filter_parts = []
        
        # Process each image: download → scale → crop → Ken Burns
        for i, img_path in enumerate(image_paths):
            # Input: loop image for display_time seconds
            input_args.extend(['-loop', '1', '-t', str(display_time), '-i', img_path])
            
            # Filter chain for this image
            ken_burns = VideoBuilder._get_ken_burns_filter(i, num_images, duration_frames)
            filter_parts.append(
                f"[{i}:v]scale={Config.OUTPUT_WIDTH}:{Config.OUTPUT_HEIGHT}:"
                f"force_original_aspect_ratio=increase,"
                f"crop={Config.OUTPUT_WIDTH}:{Config.OUTPUT_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
                f"{ken_burns}[v{i}]"
            )
        
        # Concatenate all processed images (simple, reliable method)
        concat_inputs = "".join([f"[v{i}]" for i in range(num_images)])
        filter_parts.append(f"{concat_inputs}concat=n={num_images}:v=1:a=0[video]")
        
        # Add audio input
        input_args.extend(['-i', audio_path])
        audio_idx = num_images
        
        # Audio processing: trim + fade in/out
        fade_out_start = max(0, audio_duration - 2)
        filter_parts.append(
            f"[{audio_idx}:a]atrim=0:{audio_duration},"
            f"afade=t=in:st=0:d=1,"
            f"afade=t=out:st={fade_out_start}:d=2,"
            f"aresample={Config.AUDIO_SAMPLE_RATE}[aout]"
        )
        
        # Combine all filters
        filter_complex = ";".join(filter_parts)
        
        # Build FFmpeg command with YouTube-compatible settings
        cmd = [
            'ffmpeg', '-y', '-loglevel', 'error',
            *input_args,
            '-filter_complex', filter_complex,
            '-map', '[video]',
            '-map', '[aout]',
            # Video encoding
            '-c:v', Config.VIDEO_CODEC,
            '-preset', Config.PRESET,
            '-crf', str(Config.CRF),
            '-pix_fmt', Config.PIXEL_FORMAT,
            '-r', str(Config.FPS),
            '-movflags', '+faststart',  # Enable web streaming
            # Audio encoding
            '-c:a', Config.AUDIO_CODEC,
            '-b:a', Config.AUDIO_BITRATE,
            '-ar', str(Config.AUDIO_SAMPLE_RATE),
            output_path
        ]
        
        return cmd, audio_duration
    
    @staticmethod
    def build_advanced_command(image_paths, audio_path, output_path, captions=None):
        """
        Advanced mode with crossfade transitions.
        Note: Falls back to simple mode if xfade causes issues.
        """
        # For maximum reliability, use simple mode
        # xfade chains are fragile on serverless environments
        return VideoBuilder.build_simple_command(image_paths, audio_path, output_path)
    
    @staticmethod
    def run_command(cmd, timeout=None):
        """
        Execute FFmpeg command with error handling.
        Returns: (success: bool, message: str)
        """
        if timeout is None:
            # Dynamic timeout: base + 3 seconds per second of expected video
            timeout = Config.FFMPEG_TIMEOUT_BASE
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout
            )
            return True, "Video generated successfully"
            
        except subprocess.CalledProcessError as e:
            error = e.stderr or str(e)
            # Truncate long errors but keep useful info
            if len(error) > 1000:
                error = error[:500] + "\n...[truncated]...\n" + error[-500:]
            return False, f"FFmpeg error: {error}"
            
        except subprocess.TimeoutExpired:
            return False, f"FFmpeg timed out after {timeout} seconds. Try shorter audio or simpler mode."
            
        except FileNotFoundError:
            return False, "FFmpeg not installed on server. Contact support."
            
        except Exception as e:
            return False, f"Unexpected error: {str(e)[:500]}"