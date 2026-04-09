"""
YouTube Shorts Video Generator API
Flask application for Leapcell.io deployment
Endpoints:
GET  /health                    - Health check
GET  /                          - API documentation
POST /create-video              - Images from URLs + Audio upload
POST /create-video-from-urls    - Images + Audio from URLs
"""
from flask import Flask, request, jsonify, send_file
import os, uuid, json, shutil, requests
from config import Config
from utils.video_builder import VideoBuilder
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB upload limit
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'aac', 'flac', 'ogg'}

def allowed_file(filename, extensions):
    """Check if file extension is allowed"""
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in extensions)

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
            "POST /create-video-from-urls": "Create video: image URLs + audio URL"
        },
        "usage": {
            "/create-video": {
                "method": "POST",
                "content_type": "multipart/form-data",
                "fields": {
                    "data": "JSON: {images: string[10], mode: 'simple'|'advanced', captions: string[10], effects: string[10]}",
                    "audio": "Audio file (mp3, wav, m4a, aac, flac, ogg)"
                },
                "example": "curl -X POST URL -F 'data={\"images\":[\"url1\",...]}' -F 'audio=@file.mp3'"
            },
            "/create-video-from-urls": {
                "method": "POST",
                "content_type": "application/json",
                "body": {
                    "images": ["url1", "url2", "..."],  # Exactly 10 URLs
                    "audio": "https://example.com/audio.mp3",
                    "mode": "simple",
                    "captions": ["text1", "text2", "..."],  # Optional, 10 strings
                    "effects": ["simple", "advanced", "..."]  # Optional, 10 effects
                }
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
        
        # Validate effects array (NEW)
        effects = params.get('effects', ['simple'] * 10)
        if not isinstance(effects, list) or len(effects) != 10:
            return jsonify({
                "error": "Exactly 10 effect types required in 'effects' array",
                "received": len(effects) if isinstance(effects, list) else "invalid type"
            }), 400
        
        # Validate each effect
        for i, effect in enumerate(effects):
            if effect not in Config.EFFECTS:
                return jsonify({
                    "error": f"Invalid effect '{effect}' at index {i}",
                    "allowed": list(Config.EFFECTS.keys())
                }), 400
        
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
        
        app.logger.info(f"Video generated successfully: job={job_id}, size={os.path.getsize(output_path)} bytes")
        
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

@app.route('/create-video-from-urls', methods=['POST'])
def create_video_from_urls():
    """
    Create YouTube Short from image URLs + audio URL (all from web)
    Request:
      Content-Type: application/json
      Body: {images: string[10], audio: string, mode: string, captions: string[10], effects: string[10]}

    Response:
      200: MP4 video file
      400: Validation error
      500: Processing error
    """
    temp_dir = None
    try:
        # === Parse JSON Request ===
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON request body required"}), 400
        
        # Validate images
        images = data.get('images', [])
        if not isinstance(images, list) or len(images) != 10:
            return jsonify({
                "error": "Exactly 10 image URLs required",
                "received": len(images) if isinstance(images, list) else "invalid type"
            }), 400
        
        for i, url in enumerate(images):
            if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
                return jsonify({
                    "error": f"Invalid image URL at index {i}",
                    "value": str(url)[:100]
                }), 400
        
        # Validate audio URL
        audio_url = data.get('audio')
        if not audio_url or not isinstance(audio_url, str):
            return jsonify({"error": "Audio URL is required"}), 400
        if not audio_url.startswith(('http://', 'https://')):
            return jsonify({"error": "Invalid audio URL format"}), 400
        
        # Get optional parameters
        mode = data.get('mode', 'simple')
        if mode not in ['simple', 'advanced']:
            mode = 'simple'
        
        captions = data.get('captions', [''] * 10)
        if not isinstance(captions, list):
            captions = [''] * 10
        captions = (list(captions) + [''] * 10)[:10]
        
        # Validate effects array (NEW)
        effects = data.get('effects', ['simple'] * 10)
        if not isinstance(effects, list) or len(effects) != 10:
            return jsonify({
                "error": "Exactly 10 effect types required in 'effects' array",
                "received": len(effects) if isinstance(effects, list) else "invalid type"
            }), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
