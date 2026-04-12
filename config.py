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

    # 📦 Hosted response payload guard (tuned lower for Leapcell download gateway limits)
    MAX_RESPONSE_BYTES = 4_900_000
    FALLBACK_VIDEO_BITRATES = ['380k', '300k', '240k', '200k']
    FALLBACK_AUDIO_BITRATES = ['80k', '64k', '48k']
    
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
    FFMPEG_TIMEOUT_CAP = 240      # Keep below common platform gunicorn timeout (300s)
    GENERATED_URL_TTL_SECONDS = 3600
    
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
        "dream_glow": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,gblur=sigma=1.2,eq=brightness=0.03:contrast=0.96:saturation=1.08",
            "description": "Soft dreamy glow",
            "duration_multiplier": 1.0,
        },
        "noir_film": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,hue=s=0,eq=contrast=1.28:brightness=-0.02,noise=alls=4:allf=t+u",
            "description": "Noir monochrome film",
            "duration_multiplier": 1.0,
        },
        "sunset_pop": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,colorbalance=rs=0.08:gs=0.02:bs=-0.06,eq=saturation=1.18:contrast=1.06",
            "description": "Warm sunset pop",
            "duration_multiplier": 1.0,
        },
        "arctic_pop": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,colorbalance=rs=-0.05:gs=0.01:bs=0.08,eq=saturation=1.08:contrast=1.05",
            "description": "Cool arctic color pop",
            "duration_multiplier": 1.0,
        },
        "vhs_soft": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,noise=alls=9:allf=t+u,eq=contrast=1.03:saturation=0.92,unsharp=3:3:0.2:3:3:0.0",
            "description": "Soft VHS nostalgia",
            "duration_multiplier": 1.0,
        },
        "fade_matte": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=contrast=0.90:brightness=0.02:saturation=0.82",
            "description": "Matte faded grade",
            "duration_multiplier": 1.0,
        },
        "clean_commercial": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,unsharp=5:5:0.6:5:5:0.0,eq=contrast=1.10:brightness=0.02:saturation=1.04",
            "description": "Clean commercial look",
            "duration_multiplier": 1.0,
        },
        "pastel_wash": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=contrast=0.93:brightness=0.04:saturation=0.88:gamma=1.03",
            "description": "Pastel washed tones",
            "duration_multiplier": 1.0,
        },
        "bold_magazine": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,eq=contrast=1.22:brightness=0.01:saturation=1.22,unsharp=5:5:0.7:5:5:0.0",
            "description": "Bold magazine punch",
            "duration_multiplier": 1.0,
        },
        "soft_skin": {
            "filter": "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,gblur=sigma=0.7,eq=brightness=0.02:contrast=0.98:saturation=1.02",
            "description": "Gentle soft-skin smoothing",
            "duration_multiplier": 1.0,
        },
    }

    # 50 transition modes for effect_key_00..effect_key_49.
    TRANSITION_TYPES: List[str] = [
        'fade', 'fadeblack', 'fadewhite', 'fadegrays',
        'wipeleft', 'wiperight', 'wipeup', 'wipedown',
        'slideleft', 'slideright', 'slideup', 'slidedown',
        'smoothleft', 'smoothright', 'smoothup', 'smoothdown',
        'circlecrop', 'rectcrop', 'circleopen', 'circleclose',
        'vertopen', 'vertclose', 'horzopen', 'horzclose',
        'dissolve', 'pixelize', 'radial', 'distance',
        'diagtl', 'diagtr', 'diagbl', 'diagbr',
        'hlslice', 'hrslice', 'vuslice', 'vdslice',
        'hblur', 'zoomin', 'fadefast', 'fadeslow',
        'hlwind', 'hrwind', 'vuwind', 'vdwind',
        'coverleft', 'coverright', 'coverup', 'coverdown',
        'revealleft', 'revealright'
    ]

    # Exactly 50 internal visual presets used by public keys effect_key_00..effect_key_49.
    EFFECT_KEY_EFFECTS: List[str] = [
        'simple_fit', 'warm_grade', 'cool_grade', 'high_contrast', 'soft_contrast',
        'grayscale_soft', 'grayscale_contrast', 'sepia_soft', 'sepia_deep', 'negative',
        'mirror_h', 'rotate_cw', 'rotate_ccw', 'rotate_soft', 'blur_soft',
        'blur_medium', 'blur_strong', 'sharpen_soft', 'sharpen_strong', 'vignette_soft',
        'vignette_medium', 'vignette_hard', 'noise_soft', 'noise_medium', 'hue_shift_warm',
        'hue_shift_cool', 'saturation_boost', 'saturation_reduce', 'brightness_boost', 'brightness_reduce',
        'gamma_warm', 'gamma_cool', 'film_grain', 'cinematic', 'portrait_pop',
        'soft_pastel', 'teal_orange', 'retro_tint', 'magenta_tint', 'clarity',
        'dream_glow', 'noir_film', 'sunset_pop', 'arctic_pop', 'vhs_soft',
        'fade_matte', 'clean_commercial', 'pastel_wash', 'bold_magazine', 'soft_skin'
    ]

    # 50 unique idle/post-transition style names, one for each key.
    IDLE_STYLE_ORDER: List[str] = [f'idle_{i:02d}' for i in range(50)]

    IDLE_POST_VARIANTS: List[str] = [
        'eq=contrast=1.01:saturation=1.02',
        'eq=contrast=1.03:saturation=1.05:brightness=0.01',
        'eq=contrast=1.02:saturation=0.98',
        'eq=contrast=1.06:saturation=1.08,unsharp=3:3:0.25:3:3:0.0',
        'eq=contrast=0.99:saturation=1.00',
        'eq=contrast=1.00:saturation=1.03:gamma=1.01',
        'eq=contrast=1.04:saturation=1.00:brightness=0.005',
        'eq=contrast=0.98:saturation=0.96,unsharp=3:3:0.15:3:3:0.0',
        'eq=contrast=1.05:saturation=1.07:brightness=0.008',
        'eq=contrast=1.00:saturation=0.99:gamma=0.99',
    ]

    @classmethod
    def resolve_idle_style(cls, idle_name: str):
        """Resolve idle_00..idle_49 to a unique motion/polish style."""
        if not isinstance(idle_name, str) or not idle_name.startswith('idle_'):
            return None
        suffix = idle_name[len('idle_'):]
        if not suffix.isdigit():
            return None
        idx = int(suffix)
        if not (0 <= idx < 50):
            return None

        # Keep zoom deltas positive and safely above output size after renderer expansion.
        zoom_w = 88 + (idx % 10) * 6 + (idx // 10)
        zoom_h = 160 + (idx % 10) * 11 + (idx // 10) * 2
        pan_x = 9 + (idx % 7) * 1.5
        pan_y = 7 + (idx % 6) * 1.3
        period_x = 5.0 + (idx % 9) * 0.35
        period_y = 5.8 + (idx % 8) * 0.4
        post = cls.IDLE_POST_VARIANTS[idx % len(cls.IDLE_POST_VARIANTS)]

        return {
            'zoom_w': round(zoom_w, 2),
            'zoom_h': round(zoom_h, 2),
            'pan_x': round(pan_x, 2),
            'pan_y': round(pan_y, 2),
            'period_x': round(period_x, 2),
            'period_y': round(period_y, 2),
            'post': post,
        }

    @classmethod
    def _parse_effect_index(cls, effect: str):
        if not isinstance(effect, str) or not effect.startswith('effect_key_'):
            return None
        suffix = effect[len('effect_key_'):]
        if not suffix.isdigit():
            return None
        idx = int(suffix)
        if 0 <= idx < 50:
            return idx
        return None

    @classmethod
    def canonical_effect_key(cls, idx: int):
        return f"effect_key_{idx:02d}"

    @classmethod
    def resolve_effect_profile(cls, effect: str):
        """Resolve a public effect key or direct effect name to a full rendering profile."""
        idx = cls._parse_effect_index(effect)
        if idx is None:
            if effect not in cls.EFFECTS:
                return None
            # Backward-compat: direct effect names map to their first indexed key when available.
            try:
                idx = cls.EFFECT_KEY_EFFECTS.index(effect)
            except ValueError:
                idx = 0

        effect_name = cls.EFFECT_KEY_EFFECTS[idx]
        idle_name = cls.IDLE_STYLE_ORDER[idx]
        idle_style = cls.resolve_idle_style(idle_name)
        return {
            'key': cls.canonical_effect_key(idx),
            'effect_name': effect_name,
            'transition': cls.TRANSITION_TYPES[idx % len(cls.TRANSITION_TYPES)],
            'idle_name': idle_name,
            'idle': idle_style,
        }

    @classmethod
    def resolve_effect_key(cls, effect: str):
        profile = cls.resolve_effect_profile(effect)
        return profile['effect_name'] if profile else None

    @classmethod
    def allowed_effect_inputs(cls):
        return [cls.canonical_effect_key(i) for i in range(50)] + list(cls.EFFECTS.keys())
    
    # Validate effect configurations
    @classmethod
    def validate_effects(cls):
        """Validate all effect configurations"""
        if len(cls.EFFECTS) < 50:
            raise ValueError(f"Expected at least 50 effects, but found {len(cls.EFFECTS)}")
        if len(cls.TRANSITION_TYPES) != 50:
            raise ValueError(f"Expected exactly 50 transitions, but found {len(cls.TRANSITION_TYPES)}")
        if len(cls.EFFECT_KEY_EFFECTS) != 50:
            raise ValueError(f"Expected exactly 50 effect-key presets, but found {len(cls.EFFECT_KEY_EFFECTS)}")
        if len(cls.IDLE_STYLE_ORDER) != 50:
            raise ValueError(f"Expected exactly 50 idle style names, but found {len(cls.IDLE_STYLE_ORDER)}")
        for effect_name, effect_config in cls.EFFECTS.items():
            if "filter" not in effect_config:
                raise ValueError(f"Effect '{effect_name}' is missing required 'filter' parameter")
            if "description" not in effect_config:
                raise ValueError(f"Effect '{effect_name}' is missing required 'description' parameter")
            if "duration_multiplier" not in effect_config:
                raise ValueError(f"Effect '{effect_name}' is missing required 'duration_multiplier' parameter")
        for mapped_effect in cls.EFFECT_KEY_EFFECTS:
            if mapped_effect not in cls.EFFECTS:
                raise ValueError(f"Effect key maps to unknown effect '{mapped_effect}'")
        for idle_name in cls.IDLE_STYLE_ORDER:
            if cls.resolve_idle_style(idle_name) is None:
                raise ValueError(f"Idle style '{idle_name}' cannot be resolved")