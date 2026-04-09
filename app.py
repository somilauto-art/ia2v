from flask import Flask, request, jsonify, send_file
import os, uuid, json, shutil, requests
from config import Config
from utils.video_builder import VideoBuilder

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB audio limit

ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'aac', 'flac', 'ogg'}

def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "video-api", "version": "1.0.0"}), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "Video Generator API",
        "endpoints": {
            "GET /health": "Health check",
            "POST /create-video": "Images from URLs + Audio Upload (any duration)",
            "POST /create-video-from-urls": "Images + Audio from URLs (any duration)"
        }
    }), 200

@app.route('/create-video', methods=['POST'])
def create_video():
    """
    Create video from image URLs + uploaded audio
    Duration is determined by audio length (no 60s limit)
    """
    try:
        # 1. Validate audio upload
        if 'audio' not in request.files:
            return jsonify({"error": "Audio file required"}), 400
        
        audio_file = request.files['audio']
        if not allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
            return jsonify({"error": f"Invalid audio format. Allowed: {ALLOWED_AUDIO_EXTENSIONS}"}), 400

        # 2. Parse JSON data for images/settings
        data_raw = request.form.get('data', '{}')
        try:
            params = json.loads(data_raw)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON in 'data' field"}), 400

        images = params.get('images', [])
        if not isinstance(images, list) or len(images) != 10:
            return jsonify({"error": "Exactly 10 image URLs required"}), 400
        
        for i, url in enumerate(images):
            if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
                return jsonify({"error": f"Invalid URL at index {i}"}), 400

        mode = params.get('mode', 'simple')
        captions = params.get('captions', [''] * 10)[:10]

        # 3. Setup temp directory
        job_id = str(uuid.uuid4())
        temp_dir = os.path.join(Config.OUTPUT_FOLDER, job_id)
        os.makedirs(temp_dir, exist_ok=True)

        # 4. Download images
        image_paths = []
        for i, img_url in enumerate(images):
            try:
                resp = requests.get(img_url, timeout=30)
                resp.raise_for_status()
                ext = 'png' if 'png' in img_url.lower() else 'jpg'
                path = os.path.join(temp_dir, f'image_{i+1}.{ext}')
                with open(path, 'wb') as f:
                    f.write(resp.content)
                if os.path.getsize(path) == 0:
                    raise ValueError("Empty download")
                image_paths.append(path)
            except Exception as e:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return jsonify({"error": f"Failed to download image {i+1}", "details": str(e)}), 400

        # 5. Save audio
        audio_ext = audio_file.filename.rsplit('.', 1)[1].lower()
        audio_path = os.path.join(temp_dir, f'audio.{audio_ext}')
        audio_file.save(audio_path)

        # 6. Generate video (duration based on audio length)
        output_path = os.path.join(temp_dir, 'output.mp4')
        
        # Use simple mode for longer videos (more reliable)
        if mode == 'advanced':
            cmd, duration = VideoBuilder.build_shorts_command(
                image_paths, audio_path, output_path, captions
            )
        else:
            cmd, duration = VideoBuilder.build_simple_shorts_command(
                image_paths, audio_path, output_path
            )
        
        # Increase timeout for longer videos (3min per minute of video)
        timeout = max(180, int(duration * 3))
        success, msg = VideoBuilder.run_command(cmd, timeout=timeout)

        if not success:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify({"error": "FFmpeg failed", "details": msg}), 500

        return send_file(
            output_path, 
            mimetype='video/mp4', 
            as_attachment=True, 
            download_name=f'video_{job_id}.mp4'
        )

    except Exception as e:
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
        app.logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal error", "details": str(e)}), 500

@app.route('/create-video-from-urls', methods=['POST'])
def create_video_from_urls():
    """
    Create video from image URLs + audio URL
    Duration is determined by audio length (no 60s limit)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body required"}), 400

        images = data.get('images', [])
        if not isinstance(images, list) or len(images) != 10:
            return jsonify({"error": "Exactly 10 image URLs required"}), 400

        audio_url = data.get('audio')
        if not audio_url or not isinstance(audio_url, str):
            return jsonify({"error": "Audio URL required"}), 400

        mode = data.get('mode', 'simple')
        captions = data.get('captions', [''] * 10)[:10]

        job_id = str(uuid.uuid4())
        temp_dir = os.path.join(Config.OUTPUT_FOLDER, job_id)
        os.makedirs(temp_dir, exist_ok=True)

        # Download images
        image_paths = []
        for i, img_url in enumerate(images):
            try:
                resp = requests.get(img_url, timeout=30)
                resp.raise_for_status()
                ext = 'png' if 'png' in img_url.lower() else 'jpg'
                path = os.path.join(temp_dir, f'image_{i+1}.{ext}')
                with open(path, 'wb') as f:
                    f.write(resp.content)
                image_paths.append(path)
            except Exception as e:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return jsonify({"error": f"Image {i+1} download failed", "details": str(e)}), 400

        # Download audio
        try:
            resp = requests.get(audio_url, timeout=300)  # 5min for large audio
            resp.raise_for_status()
            ext = 'm4a' if 'm4a' in audio_url.lower() else 'mp3'
            audio_path = os.path.join(temp_dir, f'audio.{ext}')
            with open(audio_path, 'wb') as f:
                f.write(resp.content)
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify({"error": "Audio download failed", "details": str(e)}), 400

        # Generate video
        output_path = os.path.join(temp_dir, 'output.mp4')
        
        if mode == 'advanced':
            cmd, duration = VideoBuilder.build_shorts_command(
                image_paths, audio_path, output_path, captions
            )
        else:
            cmd, duration = VideoBuilder.build_simple_shorts_command(
                image_paths, audio_path, output_path
            )
        
        # Dynamic timeout based on duration
        timeout = max(180, int(duration * 3))
        success, msg = VideoBuilder.run_command(cmd, timeout=timeout)

        if not success:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify({"error": "FFmpeg failed", "details": msg}), 500

        return send_file(
            output_path, 
            mimetype='video/mp4', 
            as_attachment=True, 
            download_name=f'video_{job_id}.mp4'
        )

    except Exception as e:
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
        app.logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal error", "details": str(e)}), 500

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large", "max_size": "200MB"}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)