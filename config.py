"""
YouTube Shorts Video Generator - Configuration
Optimized for Leapcell.io serverless deployment
"""
import os
from typing import Dict, List, Any

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

    # ⏱️ Processing Limits
    MAX_AUDIO_DURATION = 600      # 10 minutes max
    FFPROBE_TIMEOUT = 30          # Seconds to wait for audio probe
    FFMPEG_TIMEOUT_BASE = 180     # Base timeout before scaling by duration
    
    # ===== EFFECT CONFIGURATION =====
    # 50 distinct FFmpeg-safe presets for vertical slideshow rendering.
    EFFECTS: Dict[str, Dict[str, Any]] = {
        "simple_fit": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black",
            "description": "Centered fit with black padding",
            "duration_multiplier": 1.0,
        },
        "warm_grade": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=contrast=1.05:brightness=0.02:saturation=1.20:gamma=1.05",
            "description": "Warm color grade",
            "duration_multiplier": 1.0,
        },
        "cool_grade": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=contrast=1.05:brightness=0.00:saturation=0.90:gamma=1.00",
            "description": "Cool color grade",
            "duration_multiplier": 1.0,
        },
        "high_contrast": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=contrast=1.35:brightness=0.02:saturation=1.10",
            "description": "High contrast look",
            "duration_multiplier": 1.0,
        },
        "soft_contrast": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=contrast=0.95:brightness=0.03:saturation=1.05",
            "description": "Soft contrast look",
            "duration_multiplier": 1.0,
        },
        "grayscale_soft": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,hue=s=0",
            "description": "Soft grayscale",
            "duration_multiplier": 1.0,
        },
        "grayscale_contrast": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,hue=s=0,eq=contrast=1.20:brightness=0.00",
            "description": "Grayscale with extra contrast",
            "duration_multiplier": 1.0,
        },
        "sepia_soft": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
            "description": "Soft sepia tone",
            "duration_multiplier": 1.0,
        },
        "sepia_deep": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,colorchannelmixer=.35:.70:.16:0:.30:.60:.10:0:.22:.45:.12",
            "description": "Deep sepia tone",
            "duration_multiplier": 1.0,
        },
        "negative": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,negate",
            "description": "Inverted colors",
            "duration_multiplier": 1.0,
        },
        "mirror_h": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,hflip",
            "description": "Horizontal mirror",
            "duration_multiplier": 1.0,
        },
        "mirror_v": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,vflip",
            "description": "Vertical flip",
            "duration_multiplier": 1.0,
        },
        "rotate_cw": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,transpose=1",
            "description": "Rotate 90 degrees clockwise",
            "duration_multiplier": 1.0,
        },
        "rotate_ccw": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,transpose=2",
            "description": "Rotate 90 degrees counter-clockwise",
            "duration_multiplier": 1.0,
        },
        "rotate_180": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,hflip,vflip",
            "description": "Rotate 180 degrees",
            "duration_multiplier": 1.0,
        },
        "rotate_soft": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,rotate=0.04:fillcolor=black",
            "description": "Slight rotation",
            "duration_multiplier": 1.0,
        },
        "blur_soft": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,boxblur=2:1",
            "description": "Light blur",
            "duration_multiplier": 1.0,
        },
        "blur_medium": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,boxblur=4:2",
            "description": "Medium blur",
            "duration_multiplier": 1.0,
        },
        "blur_strong": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,boxblur=8:4",
            "description": "Strong blur",
            "duration_multiplier": 1.0,
        },
        "sharpen_soft": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,unsharp=5:5:0.8:5:5:0.0",
            "description": "Light sharpening",
            "duration_multiplier": 1.0,
        },
        "sharpen_strong": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,unsharp=7:7:1.5:7:7:0.0",
            "description": "Strong sharpening",
            "duration_multiplier": 1.0,
        },
        "vignette_soft": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,vignette=0.3",
            "description": "Soft vignette",
            "duration_multiplier": 1.0,
        },
        "vignette_medium": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,vignette=0.5",
            "description": "Medium vignette",
            "duration_multiplier": 1.0,
        },
        "vignette_hard": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,vignette=0.7",
            "description": "Strong vignette",
            "duration_multiplier": 1.0,
        },
        "edge_detect": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,edgedetect=low=0.1:high=0.4",
            "description": "Edge detection",
            "duration_multiplier": 1.0,
        },
        "edge_detect_strong": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,edgedetect=low=0.05:high=0.20",
            "description": "Stronger edge detection",
            "duration_multiplier": 1.0,
        },
        "noise_soft": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,noise=alls=5:allf=t+u",
            "description": "Light film noise",
            "duration_multiplier": 1.0,
        },
        "noise_medium": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,noise=alls=10:allf=t+u",
            "description": "Medium film noise",
            "duration_multiplier": 1.0,
        },
        "noise_strong": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,noise=alls=20:allf=t+u",
            "description": "Strong film noise",
            "duration_multiplier": 1.0,
        },
        "hue_shift_warm": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,hue=h=15:s=1.05",
            "description": "Warm hue shift",
            "duration_multiplier": 1.0,
        },
        "hue_shift_cool": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,hue=h=-20:s=1.10",
            "description": "Cool hue shift",
            "duration_multiplier": 1.0,
        },
        "saturation_boost": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=saturation=1.5",
            "description": "Higher saturation",
            "duration_multiplier": 1.0,
        },
        "saturation_reduce": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=saturation=0.75",
            "description": "Lower saturation",
            "duration_multiplier": 1.0,
        },
        "brightness_boost": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=brightness=0.08",
            "description": "Brighter image",
            "duration_multiplier": 1.0,
        },
        "brightness_reduce": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=brightness=-0.08",
            "description": "Darker image",
            "duration_multiplier": 1.0,
        },
        "gamma_warm": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=gamma=1.2",
            "description": "Gamma lift",
            "duration_multiplier": 1.0,
        },
        "gamma_cool": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=gamma=0.85",
            "description": "Gamma reduction",
            "duration_multiplier": 1.0,
        },
        "drawgrid": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,drawgrid=w=iw/12:h=ih/12:t=2:c=white@0.15",
            "description": "Subtle grid overlay",
            "duration_multiplier": 1.0,
        },
        "film_grain": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,noise=alls=12:allf=t+u,eq=contrast=1.08:saturation=1.08",
            "description": "Grainy film look",
            "duration_multiplier": 1.0,
        },
        "cinematic": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=contrast=1.18:brightness=-0.02:saturation=1.15,vignette=0.45",
            "description": "Cinematic grade",
            "duration_multiplier": 1.0,
        },
        "portrait_pop": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=contrast=1.15:brightness=0.04:saturation=1.25",
            "description": "Vibrant portrait look",
            "duration_multiplier": 1.0,
        },
        "soft_pastel": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=contrast=0.92:brightness=0.03:saturation=0.85",
            "description": "Soft pastel look",
            "duration_multiplier": 1.0,
        },
        "teal_orange": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,colorbalance=rs=0.06:gs=-0.02:bs=-0.04:rh=-0.04:gh=0.03:bh=0.06",
            "description": "Teal and orange grade",
            "duration_multiplier": 1.0,
        },
        "retro_tint": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,colorbalance=rs=0.03:gs=0.00:bs=0.05",
            "description": "Retro tint",
            "duration_multiplier": 1.0,
        },
        "magenta_tint": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,colorbalance=rm=0.08:gm=0.00:bm=0.05",
            "description": "Magenta tint",
            "duration_multiplier": 1.0,
        },
        "crop_zoom": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,crop=iw*0.92:ih*0.92,scale=1080:1920",
            "description": "Slight crop zoom",
            "duration_multiplier": 1.0,
        },
        "inner_frame": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,crop=iw*0.90:ih*0.90,scale=1080:1920",
            "description": "Inset framed crop",
            "duration_multiplier": 1.0,
        },
        "border_soft": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,drawbox=x=20:y=20:w=iw-40:h=ih-40:color=white@0.25:t=10",
            "description": "Soft border frame",
            "duration_multiplier": 1.0,
        },
        "border_dark": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,drawbox=x=40:y=40:w=iw-80:h=ih-80:color=black@0.35:t=12",
            "description": "Dark border frame",
            "duration_multiplier": 1.0,
        },
        "clarity": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,unsharp=7:7:1.0:7:7:0.0,eq=contrast=1.12:saturation=1.08",
            "description": "Sharpened clarity look",
            "duration_multiplier": 1.0,
        },
    }
    
    # Validate effect configurations
    @classmethod
    def validate_effects(cls):
        """Validate all effect configurations"""
        if len(cls.EFFECTS) != 50:
            raise ValueError(f"Expected exactly 50 effects, but found {len(cls.EFFECTS)}")
        for effect_name, effect_config in cls.EFFECTS.items():
            if "filter" not in effect_config:
                raise ValueError(f"Effect '{effect_name}' is missing required 'filter' parameter")
            if "description" not in effect_config:
                raise ValueError(f"Effect '{effect_name}' is missing required 'description' parameter")
            if "duration_multiplier" not in effect_config:
                raise ValueError(f"Effect '{effect_name}' is missing required 'duration_multiplier' parameter")