# File.io Download Guide

## Overview
Your video API now automatically uploads all generated videos to **file.io** and returns a direct download link. This bypasses Leapcell's response payload limits.

## How It Works

1. **Request:** Send images + audio to `/create-video`
2. **Processing:** Leapcell generates the video locally
3. **Upload:** Video is uploaded to file.io (happens automatically)
4. **Response:** You get a small JSON with a download link (always <1KB payload)
5. **Download:** Download from file.io link (works with any file size)

## Example Request & Response

### Request
```bash
curl -X POST http://localhost:5000/create-video \
  -F 'data={"images":["https://example.com/img1.jpg",...,"https://example.com/img10.jpg"],"effects":"effect_key_00"}' \
  -F 'audio=@your_audio.mp3'
```

### Response (Success)
```json
{
  "status": "success",
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "download_url": "https://file.io/ab1cde2fg3hi",
  "file_key": "ab1cde2fg3hi",
  "size_mb": 8.5,
  "expires_in_days": 14,
  "message": "Download via file.io link. Valid for 14 days."
}
```

## Downloading Videos (Any Size)

### Method 1: Direct Browser Download
Simply click the `download_url`:
```
https://file.io/ab1cde2fg3hi
```

### Method 2: Command Line (curl)
```bash
curl -L https://file.io/ab1cde2fg3hi -o MyVideo.mp4
```

### Method 3: Python
```python
import requests

download_url = "https://file.io/ab1cde2fg3hi"
response = requests.get(download_url, stream=True)

with open("video.mp4", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
```

### Method 4: JavaScript/Node.js
```javascript
const fetch = require('node-fetch');
const fs = require('fs');

const downloadUrl = 'https://file.io/ab1cde2fg3hi';
const response = await fetch(downloadUrl);
const buffer = await response.buffer();
fs.writeFileSync('video.mp4', buffer);
```

## File Size Limitations

- **file.io free tier:** Up to 5GB per file ✅
- **Your API:** Videos typically 5-10MB (well within limits)
- **Compression:** If video still exceeds 5GB, increase CRF or reduce audio bitrate in `config.py`

## Data Retention

- **Expiry:** 14 days (files auto-deleted)
- **Download limit:** 1 download after which file expires (security feature)
- **Recommendation:** Download immediately after receiving the link

## Troubleshooting

### "file.io upload failed" (5xx error)
- Video file is too large (unlikely, but check if > 5GB)
- Network timeout during upload (try again, usually transient)
- file.io service is down (rare; check https://status.file.io)

### "File expired or not found" on download
- 14-day retention passed
- Already downloaded once (file.io auto-deletes after 1 download)
- **Solution:** Request a new video generation from the API

### Video downloads but won't play
- Ensure Content-Length header is correct (usually is with file.io)
- Try opening in VLC Media Player
- Check that file is not corrupted during download (`ls -lh video.mp4`)

## Performance Notes

- **Upload to file.io:** 10-30s depending on video size and network
- **Total API response time:** ~150-200s (generation + upload)
- **Download speed:** Depends on your connection (file.io is global CDN)

## Migration from Old API

If you had code using the old `return_url` parameter:
- **Old:** `{"return_url": true}` → returned local Leapcell URL
- **New:** Always returns file.io URL (no parameter needed anymore)

Just use the `download_url` from the response—it now always points to file.io!
