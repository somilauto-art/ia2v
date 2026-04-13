"""
File upload utilities for uploading generated videos to file.io
Bypasses response payload limits by streaming video to temporary file hosting
"""

import requests
import os
import time

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def upload_to_fileio(file_path, timeout=300, max_retries=3):
    """
    Upload video file to file.io and return download link.
    
    Args:
        file_path: Absolute path to MP4 file to upload
        timeout: Upload timeout in seconds (default 300s = 5 min)
        max_retries: Number of retry attempts on connection failure (default 3)
    
    Returns:
        tuple: (success: bool, response_data: dict)
        On success: (True, {"download_url": "https://file.io/...", "file_key": "..."})
        On failure: (False, {"error": "reason", "details": "..."})
    """
    
    if not os.path.exists(file_path):
        return False, {"error": "File not found", "path": file_path}
    
    file_size = os.path.getsize(file_path)
    
    # Check file size limit (file.io allows up to 5GB free, but be safe)
    MAX_FILEIO_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
    if file_size > MAX_FILEIO_SIZE:
        return False, {
            "error": "File exceeds file.io size limit",
            "file_size_mb": round(file_size / 1024 / 1024, 2),
            "limit_mb": round(MAX_FILEIO_SIZE / 1024 / 1024, 2)
        }
    
    attempt = 0
    while attempt < max_retries:
        try:
            # Simple approach: upload with minimal settings
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'expires': '14d'}  # Send expiry as form data, not URL param
                
                # Use newer session approach with verify=False at connection level
                response = requests.post(
                    'https://file.io/',
                    files=files,
                    data=data,
                    timeout=timeout,
                    verify=False  # Disable SSL certificate verification
                )
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success', False):
                attempt += 1
                if attempt < max_retries:
                    wait = 2 ** attempt
                    time.sleep(wait)
                    continue
                return False, {
                    "error": "file.io upload failed",
                    "details": result.get('status', 'Unknown error')
                }
            
            file_key = result.get('key', '')
            download_url = f"https://file.io/{file_key}"
            
            return True, {
                "download_url": download_url,
                "file_key": file_key,
                "file_size_mb": round(file_size / 1024 / 1024, 2),
                "expires_in_days": 14
            }
        
        except requests.exceptions.SSLError as e:
            # SSL error - retry with exponential backoff
            attempt += 1
            if attempt < max_retries:
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            return False, {
                "error": "SSL connection error with file.io",
                "details": str(e)[:300],
                "suggestion": "file.io service may be temporarily unavailable. Try again in a few minutes.",
                "attempts": attempt
            }
        
        except requests.exceptions.Timeout:
            attempt += 1
            if attempt < max_retries:
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            return False, {
                "error": "file.io upload timed out",
                "timeout_seconds": timeout,
                "details": "Connection took too long. Try a smaller video.",
                "attempts": attempt
            }
        
        except requests.exceptions.RequestException as e:
            attempt += 1
            if attempt < max_retries:
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            return False, {
                "error": "Network error uploading to file.io",
                "details": str(e)[:300],
                "attempts": attempt
            }
        
        except Exception as e:
            attempt += 1
            if attempt < max_retries:
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            return False, {
                "error": "Unexpected error",
                "details": str(e)[:300],
                "attempts": attempt
            }
    
    # Fallback if all retries failed
    return False, {
        "error": "file.io upload failed after all retry attempts",
        "attempts": max_retries,
        "suggestion": "file.io may be experiencing issues. Try uploading again later."
    }
