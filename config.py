import os

class Config:
    # 🎯 YouTube Shorts Specifications
    OUTPUT_WIDTH = 1080          # Vertical width
    OUTPUT_HEIGHT = 1920         # Vertical height (9:16 aspect ratio)
    FPS = 30                     # YouTube recommended: 30 or 60fps
    VIDEO_CODEC = 'libx264'
    AUDIO_CODEC = 'aac'
    
    # 🎬 Quality Settings for YouTube
    CRF = 20                     # 18-23 range (20 = excellent quality/size balance)
    PRESET = 'medium'            # 'slow' for better compression, 'medium' for speed
    VIDEO_BITRATE = '8M'         # YouTube Shorts target bitrate
    AUDIO_BITRATE = '192k'
    AUDIO_SAMPLE_RATE = '48000'  # YouTube standard
    
    # ⏱️ Timing for 10 images in ≤60 seconds
    MAX_DURATION = 58            # Leave 2s buffer under 60s limit
    NUM_IMAGES = 10
    TRANSITION_DURATION = 0.8    # Shorter transitions for fast-paced Shorts
    IMAGE_DISPLAY_TIME = (MAX_DURATION - TRANSITION_DURATION) / NUM_IMAGES  # ~5.7s each
    
    # 🎨 Ken Burns Effect (Vertical-Optimized)
    ZOOM_START = 1.0
    ZOOM_END = 1.25              # Subtler zoom for vertical framing
    PAN_VARIATIONS = [
        'center',
        'top-center', 
        'bottom-center',
        'center-left',
        'center-right'
    ]
    
    # 🎵 Audio Handling
    AUDIO_FADE_IN = 1.0          # 1-second fade in
    AUDIO_FADE_OUT = 2.0         # 2-second fade out (critical for Shorts)
    
    # 📁 Paths (Leapcell /tmp is writable)
    UPLOAD_FOLDER = '/tmp/uploads'
    OUTPUT_FOLDER = '/tmp/output'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # 🏷️ Optional: Default caption styling (for text overlay feature)
    CAPTION_FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    CAPTION_SIZE = 48
    CAPTION_COLOR = 'white'
    CAPTION_BOX_COLOR = 'black@0.6'  # Semi-transparent black background