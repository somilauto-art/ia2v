"""
Video Builder Utility for YouTube Shorts Generator
Handles FFmpeg command construction for video generation
"""

import os
from config import Config

class VideoBuilder:
    @staticmethod
    def build_simple_command(image_paths, audio_path, output_path):
        """Build FFmpeg command for simple slideshow (no zoom effect)"""
        # Ensure all images are scaled to 1080x1920 (9:16)
        cmd = [
            'ffmpeg',
            '-y',
            '-i', audio_path,
            '-loop', '1',
            '-i', image_paths[0],
            '-filter_complex',
            f"scale={Config.OUTPUT_WIDTH}:{Config.OUTPUT_HEIGHT}:force_original_aspect_ratio=decrease,Pad={Config.OUTPUT_WIDTH}:{Config.OUTPUT_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
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
    def build_advanced_command(image_paths, audio_path, output_path, captions):
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
            '-filter_complex',
            f"{zoompan_filter}",
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
        import subprocess
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