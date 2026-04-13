"""S3-compatible object storage uploader for generated videos."""

import os

import boto3
from botocore.config import Config as BotoConfig


def upload_to_object_storage(file_path, object_key=None):
    """Upload local file to S3-compatible storage and return a download URL."""
    if not os.path.exists(file_path):
        return False, {"error": "File not found", "details": file_path}

    endpoint_url = os.getenv("OBJECT_STORAGE_ENDPOINT", "").strip()
    bucket = os.getenv("OBJECT_STORAGE_BUCKET", "").strip()
    access_key = os.getenv("OBJECT_STORAGE_ACCESS_KEY_ID", "").strip()
    secret_key = os.getenv("OBJECT_STORAGE_SECRET_ACCESS_KEY", "").strip()
    public_base_url = os.getenv("OBJECT_STORAGE_PUBLIC_BASE_URL", "").strip()

    missing = []
    if not endpoint_url:
        missing.append("OBJECT_STORAGE_ENDPOINT")
    if not bucket:
        missing.append("OBJECT_STORAGE_BUCKET")
    if not access_key:
        missing.append("OBJECT_STORAGE_ACCESS_KEY_ID")
    if not secret_key:
        missing.append("OBJECT_STORAGE_SECRET_ACCESS_KEY")
    if not public_base_url:
        missing.append("OBJECT_STORAGE_PUBLIC_BASE_URL")

    if missing:
        return False, {
            "error": "Missing required object storage environment variables",
            "details": ", ".join(missing),
        }

    key = object_key or os.path.basename(file_path)

    try:
        s3 = boto3.client(
            "s3",
            region_name="us-east-1",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=BotoConfig(signature_version="s3v4"),
        )

        with open(file_path, "rb") as fh:
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=fh,
                ContentType="video/mp4",
            )

        base = public_base_url.rstrip("/")
        download_url = f"{base}/{bucket}/{key}"
        file_size_mb = round(os.path.getsize(file_path) / 1024 / 1024, 2)

        return True, {
            "download_url": download_url,
            "object_key": key,
            "file_size_mb": file_size_mb,
        }
    except Exception as exc:
        return False, {
            "error": "Object storage upload failed",
            "details": str(exc)[:700],
        }
