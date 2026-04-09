"""
YouTube Shorts Video Generator - Configuration
Optimized for Leapcell.io serverless deployment
"""
import os

class Config:
    # 🎯 YouTube Shorts Specifications
    OUTPUT_WIDTH = 1080           # Vertical width
    OUTPUT_HEIGHT = 1920          # Vertical height (9:16 aspect ratio)
    FPS = 30                      # Standard YouTube frame rate
    
    # 🎬 Video Quality Settings
    VIDEO_CODEC = 'libx264'
    AUDIO_CODEC = 'aac'
    CRF = 23                      # 18=best, 23=good balance, 28=smaller
    PRESET = 'fast'               # 'fast' for speed, 'medium' for quality
    PIXEL_FORMAT = 'yuv420p'      # Required for YouTube compatibility
    AUDIO_BITRATE = '128k'
    AUDIO_SAMPLE_RATE = 48000
    
    # 🎨 Ken Burns Effect Settings
    ZOOM_MIN = 1.0                # Start zoom level
    ZOOM_MAX = 1.15               # End zoom level (subtle for vertical)
    
    # 📁 Paths (Leapcell uses /tmp for writable storage)
    UPLOAD_FOLDER = '/tmp/uploads'
    OUTPUT_FOLDER = '/tmp/output'
    
    # Create directories on startup
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # ⏱️ Processing Limits
    MAX_AUDIO_DURATION = 600      # 10 minutes max (adjust as needed)
    FFPROBE_TIMEOUT = 30          # Seconds to wait for audio probe
    FFMPEG_TIMEOUT_BASE = 180     # Base timeout + 3s per second of video