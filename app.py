"""
YouTube Shorts Video Generator API
Flask application for Leapcell.io deployment
Endpoints:
GET  /health                    - Health check
GET  /                          - API documentation
POST /create-video              - Images from URLs + Audio upload
"""
from flask import Flask, request, jsonify, send_file, url_for
import os, uuid, json, shutil, requests, time
from config import Config
from utils.video_builder import VideoBuilder
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB upload limit
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'aac', 'flac', 'ogg'}
GENERATED_VIDEOS = {}

def allowed_file(filename, extensions):
    """Check if file extension is allowed"""
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in extensions)

def parse_bool(value, default=False):
    """Parse flexible boolean values from JSON/form fields."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'true', 'yes', 'y', 'on'}
    return default

def normalize_effects(effects_input, required_count=10):
    """Normalize effects payload to exactly required_count resolved effect profiles."""
    if effects_input is None:
        raw_effects = ['effect_key_00'] * required_count
    elif isinstance(effects_input, str):
        # Single key: apply same look + transition mapping across all segments.
        raw_effects = [effects_input] * required_count
    elif isinstance(effects_input, list):
        if len(effects_input) == 1:
            raw_effects = effects_input * required_count
        elif len(effects_input) == required_count:
            raw_effects = effects_input
        else:
            return None, {
                "error": f"Provide either 1 or {required_count} effect keys in 'effects'",
                "received": len(effects_input)
            }
    else:
        return None, {
            "error": "'effects' must be a string key, a 1-item list, or a 10-item list"
        }

    resolved = []
    for i, effect in enumerate(raw_effects):
        profile = Config.resolve_effect_profile(effect)
        if profile is None:
            return None, {
                "error": f"Invalid effect '{effect}' at index {i}",
                "allowed": Config.allowed_effect_inputs()
            }
        resolved.append(profile)

    return resolved, None

def cleanup_expired_videos(now_ts):
    """Remove expired generated videos from temp storage and in-memory index."""
    expired_ids = [
        job_id for job_id, meta in GENERATED_VIDEOS.items()
        if now_ts - meta.get('created_at', 0) > Config.GENERATED_URL_TTL_SECONDS
    ]
    for job_id in expired_ids:
        meta = GENERATED_VIDEOS.pop(job_id, None)
        if not meta:
            continue
        temp_dir = meta.get('temp_dir')
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "service": "video-api",
        "version": "1.0.0"
    }), 200

@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint"""
    return jsonify({
        "service": "YouTube Shorts Video Generator",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /": "This documentation",
            "POST /create-video": "Create video: image URLs + audio upload",
            "GET /videos/<job_id>": "Download generated video when return_url=true"
        },
        "usage": {
            "/create-video": {
                "method": "POST",
                "content_type": "multipart/form-data",
                "fields": {
                    "data": "JSON: {images: string[10], mode: 'simple'|'advanced', captions: string[10], effects: string|string[1]|string[10], return_url: boolean}",
                    "audio": "Audio file (mp3, wav, m4a, aac, flac, ogg)"
                },
                "example": "curl -X POST URL -F 'data={\"images\":[\"url1\",...],\"effects\":\"effect_key_00\"}' -F 'audio=@file.mp3'"
            }
        }
    }), 200

@app.route('/create-video', methods=['POST'])
def create_video():
    """
    Create YouTube Short from image URLs + uploaded audio file
    Request:
      Content-Type: multipart/form-data
      Fields:
        - data: JSON string with {images, mode, captions, effects}
        - audio: Audio file upload

    Response:
      200: MP4 video file
      400: Validation error
      500: Processing error
    """
    temp_dir = None
    try:
        # === Validate Audio Upload ===
        if 'audio' not in request.files:
            return jsonify({"error": "Audio file is required"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No audio file selected"}), 400
        
        if not allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
            return jsonify({
                "error": f"Invalid audio format. Allowed: {sorted(ALLOWED_AUDIO_EXTENSIONS)}"
            }), 400
        
        # === Parse JSON Parameters ===
        data_raw = request.form.get('data', '{}')
        try:
            params = json.loads(data_raw)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON in 'data' field"}), 400
        
        # If true, endpoint returns JSON with downloadable URL instead of binary payload.
        return_url = parse_bool(params.get('return_url'), default=False)

        # Validate images array
        images = params.get('images', [])
        if not isinstance(images, list) or len(images) != 10:
            return jsonify({
                "error": "Exactly 10 image URLs required in 'images' array",
                "received": len(images) if isinstance(images, list) else "invalid type"
            }), 400
        
        # Validate each URL
        for i, url in enumerate(images):
            if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
                return jsonify({
                    "error": f"Invalid URL at index {i}",
                    "value": str(url)[:100] if isinstance(url, str) else "not a string"
                }), 400
        
        # Get optional parameters
        mode = params.get('mode', 'simple')
        if mode not in ['simple', 'advanced']:
            mode = 'simple'
        
        captions = params.get('captions', [''] * 10)
        if not isinstance(captions, list):
            captions = [''] * 10
        captions = (list(captions) + [''] * 10)[:10]  # Ensure exactly 10
        
        effects, effects_error = normalize_effects(params.get('effects'), required_count=10)
        if effects_error:
            return jsonify(effects_error), 400
        
        # === Setup Working Directory ===
        job_id = str(uuid.uuid4())
        temp_dir = os.path.join(Config.OUTPUT_FOLDER, job_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        #  === Download Images from URLs ===
        image_paths = []
        for i, img_url in enumerate(images):
            try:
                resp = requests.get(img_url, timeout=30)
                resp.raise_for_status()
                
                # Determine file extension
                ext = 'jpg'  # default
                content_type = resp.headers.get('Content-Type', '').lower()
                if 'png' in img_url.lower() or 'image/png' in content_type:
                    ext = 'png'
                elif 'webp' in img_url.lower() or 'image/webp' in content_type:
                    ext = 'webp'
                
                img_path = os.path.join(temp_dir, f'image_{i+1}.{ext}')
                with open(img_path, 'wb') as f:
                    f.write(resp.content)
                
                # Verify download succeeded
                if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
                    raise ValueError("Downloaded file is empty")
                
                image_paths.append(img_path)
                
            except Exception as e:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return jsonify({
                    "error": f"Failed to download image {i+1}",
                    "url": img_url[:100] if isinstance(img_url, str) else "invalid",
                    "details": str(e)[:200]
                }), 400
        
        # === Save Uploaded Audio ===
        audio_ext = audio_file.filename.rsplit('.', 1)[1].lower()
        audio_path = os.path.join(temp_dir, f'audio.{audio_ext}')
        audio_file.save(audio_path)
        
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify({"error": "Failed to save audio file"}), 500
        
        # === Generate Video ===
        output_path = os.path.join(temp_dir, 'output.mp4')
        
        # Choose builder method based on effects
        cmd, duration = VideoBuilder.build_multi_effect_command(
            image_paths, audio_path, output_path, captions, effects
        )
        
        # Calculate timeout: base + 3s per second of video
        timeout = Config.FFMPEG_TIMEOUT_BASE + int(duration * 3)
        
        app.logger.info(f"Starting video generation: job={job_id}, duration={duration:.1f}s, timeout={timeout}s")
        
        success, message = VideoBuilder.run_command(cmd, timeout=timeout)
        
        if not success:
            shutil.rmtree(temp_dir, ignore_errors=True)
            app.logger.error(f"Video generation failed: {message}")
            return jsonify({
                "error": "Video generation failed",
                "details": message[:500]
            }), 500
        
        # Verify output was created
        if not os.path.exists(output_path):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify({"error": "Video file was not created"}), 500

        # Keep response size below hosted gateway limit.
        output_size = os.path.getsize(output_path)
        if output_size > Config.MAX_RESPONSE_BYTES:
            compressed_path = os.path.join(temp_dir, 'output_compressed.mp4')
            app.logger.info(
                f"Output exceeds payload limit ({output_size} bytes). Attempting compression to <= {Config.MAX_RESPONSE_BYTES} bytes"
            )
            ok, compress_msg = VideoBuilder.compress_to_target_size(
                output_path,
                compressed_path,
                Config.MAX_RESPONSE_BYTES,
            )
            if ok and os.path.exists(compressed_path):
                output_path = compressed_path
                output_size = os.path.getsize(output_path)
                app.logger.info(f"Compression succeeded: {output_size} bytes")
            else:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return jsonify({
                    "error": "Generated video exceeds hosted response payload limit",
                    "details": compress_msg,
                    "suggestion": "Use shorter audio, fewer images, or upload output to object storage and return a URL"
                }), 413
        
        app.logger.info(f"Video generated successfully: job={job_id}, size={output_size} bytes")

        now_ts = int(time.time())
        cleanup_expired_videos(now_ts)
        GENERATED_VIDEOS[job_id] = {
            "path": output_path,
            "temp_dir": temp_dir,
            "created_at": now_ts,
            "size": output_size,
        }

        if return_url:
            download_url = request.host_url.rstrip('/') + url_for('download_video', job_id=job_id)
            return jsonify({
                "status": "success",
                "job_id": job_id,
                "download_url": download_url,
                "size_bytes": output_size,
                "expires_in_seconds": Config.GENERATED_URL_TTL_SECONDS,
            }), 200
        
        # === Send Video File ===
        return send_file(
            output_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f'short_{job_id}.mp4',
            max_age=3600  # Cache response for 1 hour
        )
        
    except Exception as e:
        app.logger.error(f"Unhandled error in create_video: {str(e)}", exc_info=True)
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        return jsonify({
            "error": "Internal server error",
            "details": str(e)[:300]
        }), 500

@app.route('/videos/<job_id>', methods=['GET'])
def download_video(job_id):
    """Download previously generated video when using return_url mode."""
    now_ts = int(time.time())
    cleanup_expired_videos(now_ts)
    meta = GENERATED_VIDEOS.get(job_id)
    if not meta:
        return jsonify({"error": "Video URL expired or not found"}), 404

    output_path = meta.get('path')
    if not output_path or not os.path.exists(output_path):
        GENERATED_VIDEOS.pop(job_id, None)
        return jsonify({"error": "Video file not found"}), 404

    return send_file(
        output_path,
        mimetype='video/mp4',
        as_attachment=True,
        download_name=f'short_{job_id}.mp4',
        max_age=3600,
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
