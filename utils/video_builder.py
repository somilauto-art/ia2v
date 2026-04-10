"""
Video Builder Utility for YouTube Shorts Generator
Handles FFmpeg command construction for video generation
"""

import os
from config import Config
import subprocess
import json

class VideoBuilder:
    @staticmethod
    def build_simple_command(image_paths, audio_path, output_path, captions=None):
        """Build FFmpeg command for simple slideshow (no effects)"""
        # Ensure all images are scaled to 1080x1920 (9:16)
        cmd = [
            'ffmpeg',
            '-y',
            '-i', audio_path,
            '-loop', '1',
            '-i', image_paths[0],
            '-filter_complex',
            f"scale=w={Config.OUTPUT_WIDTH}:h={Config.OUTPUT_HEIGHT}:force_original_aspect_ratio=decrease,pad=w={Config.OUTPUT_WIDTH}:h={Config.OUTPUT_HEIGHT}:x=(ow-iw)/2:y=(oh-ih)/2:color=black",
            '-c:v', 'libx264',
            '-preset', Config.PRESET,
            '-crf', str(Config.CRF),
            '-c:a', Config.AUDIO_CODEC,
            '-b:a', Config.AUDIO_BITRATE,
            '-shortest',
            output_path
        ]
        
        # Calculate duration based on audio
        duration = VideoBuilder._get_audio_duration(audio_path)
        return cmd, duration

    @staticmethod
    def build_advanced_command(image_paths, audio_path, output_path, captions=None):
        """Build FFmpeg command for advanced Ken Burns effect"""
        # Calculate total frames based on duration and FPS
        duration = VideoBuilder._get_audio_duration(audio_path)
        fps = Config.FPS
        total_frames = int(duration * fps)
        
        # Correct zoompan expression using lerp()
        zoompan_filter = (
            f"zoompan=z='lerp({Config.ZOOM_MIN},{Config.ZOOM_MAX},on/{total_frames})'"
            f":d={total_frames}:s={Config.OUTPUT_WIDTH}x{Config.OUTPUT_HEIGHT}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        )
        
        # Build command with Ken Burns effect
        cmd = [
            'ffmpeg',
            '-y',
            '-i', audio_path,
            '-loop', '1',
            '-i', image_paths[0],
            '-filter_complex', zoompan_filter,
            '-c:v', 'libx264',
            '-preset', Config.PRESET,
            '-crf', str(Config.CRF),
            '-c:a', Config.AUDIO_CODEC,
            '-b:a', Config.AUDIO_BITRATE,
            '-shortest',
            output_path
        ]
        
        return cmd, duration

    @staticmethod
    def build_multi_effect_command(image_paths, audio_path, output_path, captions, effects):
        """Build FFmpeg command where each effect key controls visual preset + transition + idle style."""
        if not image_paths:
            raise ValueError("At least one image is required")
        if len(image_paths) != len(effects) or len(image_paths) != len(captions):
            raise ValueError("Lengths of image_paths, effects, and captions must be equal")

        duration = VideoBuilder._get_audio_duration(audio_path)
        image_count = len(image_paths)
        transition_duration = 0.6

        profiles = []
        weights = []
        for effect in effects:
            if isinstance(effect, dict):
                profile = effect
            else:
                profile = Config.resolve_effect_profile(str(effect))
            if not profile:
                raise ValueError(f"Unsupported effect key: {effect}")
            effect_name = profile.get('effect_name')
            effect_config = Config.EFFECTS.get(effect_name)
            if not effect_config:
                raise ValueError(f"Unsupported effect preset: {effect_name}")
            profiles.append(profile)
            weights.append(max(float(effect_config.get("duration_multiplier", 1.0)), 0.1))
        total_weight = sum(weights)

        # xfade overlaps neighboring clips by transition_duration, so allocate extra base time.
        effective_total = duration + transition_duration * max(image_count - 1, 0)
        segment_durations = [max(effective_total * (w / total_weight), 0.2) for w in weights]

        cmd = [
            'ffmpeg',
            '-y',
            '-i', audio_path,
        ]

        for img_path, segment_duration in zip(image_paths, segment_durations):
            cmd.extend([
                '-loop', '1',
                '-t', f"{segment_duration:.3f}",
                '-i', img_path,
            ])

        default_filter = (
            f"scale=w={Config.OUTPUT_WIDTH}:h={Config.OUTPUT_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad=w={Config.OUTPUT_WIDTH}:h={Config.OUTPUT_HEIGHT}:x=(ow-iw)/2:y=(oh-ih)/2:color=black"
        )

        filter_parts = []
        for i in range(image_count):
            in_label = f"[{i + 1}:v]"
            out_label = f"[v{i}]"
            # Preserve original image colors: only normalize canvas + motion.
            profile = profiles[i]
            effect_filter = default_filter
            idle = profile.get('idle', {})
            zoom_w = int(idle.get('zoom_w', Config.OUTPUT_WIDTH + 108))
            zoom_h = int(idle.get('zoom_h', Config.OUTPUT_HEIGHT + 192))
            if zoom_w <= Config.OUTPUT_WIDTH:
                zoom_w = Config.OUTPUT_WIDTH + zoom_w
            if zoom_h <= Config.OUTPUT_HEIGHT:
                zoom_h = Config.OUTPUT_HEIGHT + zoom_h
            pan_x = float(idle.get('pan_x', 18))
            pan_y = float(idle.get('pan_y', 14))
            period_x = float(idle.get('period_x', 6.0))
            period_y = float(idle.get('period_y', 7.0))
            phase = i * 0.73
            filter_parts.append(
                f"{in_label}{effect_filter},"
                f"scale={zoom_w}:{zoom_h},"
                f"crop={Config.OUTPUT_WIDTH}:{Config.OUTPUT_HEIGHT}:"
                f"x='(in_w-out_w)/2+{pan_x:.2f}*sin(2*PI*t/{period_x:.2f}+{phase:.2f})':"
                f"y='(in_h-out_h)/2+{pan_y:.2f}*cos(2*PI*t/{period_y:.2f}+{phase:.2f})',"
                f"fps={Config.FPS},format={Config.PIXEL_FORMAT},setsar=1,"
                f"trim=duration={segment_durations[i]:.3f},setpts=PTS-STARTPTS"
                f"{out_label}"
            )

        if image_count == 1:
            filter_parts.append("[v0]copy[vout]")
        else:
            current_label = "[v0]"
            current_offset = max(segment_durations[0] - transition_duration, 0.0)

            for i in range(1, image_count):
                transition_name = profiles[i - 1].get('transition', 'fade')
                next_label = f"[v{i}]"
                out_label = f"[x{i}]"
                filter_parts.append(
                    f"{current_label}{next_label}xfade=transition={transition_name}:"
                    f"duration={transition_duration:.3f}:offset={current_offset:.3f}{out_label}"
                )
                current_label = out_label
                if i < image_count - 1:
                    current_offset += max(segment_durations[i] - transition_duration, 0.0)

            # Keep final output color-neutral.
            filter_parts.append(
                f"{current_label}"
                f"format={Config.PIXEL_FORMAT}[vout]"
            )

        filter_complex = ';'.join(filter_parts)

        cmd.extend([
            '-filter_complex', filter_complex,
            '-map', '[vout]',
            '-map', '0:a:0',
            '-c:v', Config.VIDEO_CODEC,
            '-preset', Config.PRESET,
            '-crf', str(Config.CRF),
            '-pix_fmt', Config.PIXEL_FORMAT,
            '-c:a', Config.AUDIO_CODEC,
            '-b:a', Config.AUDIO_BITRATE,
            '-ar', str(Config.AUDIO_SAMPLE_RATE),
            '-shortest',
            output_path,
        ])

        return cmd, duration

    @staticmethod
    def _get_audio_duration(audio_path):
        """Get duration of audio file using ffprobe"""
        import subprocess
        import json
        
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = float(json.loads(result.stdout)['format']['duration'])
            return duration
        except Exception as e:
            # Fallback to 5 seconds if duration can't be determined
            return 5.0

    @staticmethod
    def run_command(cmd, timeout=300):
        """Execute FFmpeg command with timeout"""
        try:
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                text=True
            )
            if process.returncode == 0:
                return True, "Success"
            else:
                return False, f"FFmpeg error: {process.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return False, "FFmpeg timed out"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    def compress_to_target_size(input_path, output_path, target_bytes, timeout=240):
        """Re-encode video with lower bitrates until it fits target payload size."""
        if not os.path.exists(input_path):
            return False, "Input video does not exist"

        best_path = None
        best_size = None

        for video_bitrate in Config.FALLBACK_VIDEO_BITRATES:
            for audio_bitrate in Config.FALLBACK_AUDIO_BITRATES:
                cmd = [
                    'ffmpeg',
                    '-y',
                    '-i', input_path,
                    '-c:v', Config.VIDEO_CODEC,
                    '-preset', 'veryfast',
                    '-b:v', video_bitrate,
                    '-maxrate', video_bitrate,
                    '-bufsize', '2M',
                    '-pix_fmt', Config.PIXEL_FORMAT,
                    '-c:a', Config.AUDIO_CODEC,
                    '-b:a', audio_bitrate,
                    '-ar', str(Config.AUDIO_SAMPLE_RATE),
                    '-movflags', '+faststart',
                    output_path,
                ]

                ok, message = VideoBuilder.run_command(cmd, timeout=timeout)
                if not ok:
                    continue

                size = os.path.getsize(output_path)
                if best_size is None or size < best_size:
                    best_size = size
                    best_path = output_path

                if size <= target_bytes:
                    return True, "Success"

        if best_path is not None:
            return False, f"Compressed video still exceeds payload limit ({best_size} bytes)"

        return False, "Failed to compress output video"