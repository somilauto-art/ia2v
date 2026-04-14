"""S3-compatible object storage uploader for generated videos."""

import os
from datetime import datetime, timedelta

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
        # Support either form:
        # 1) https://host
        # 2) https://host/<bucket>
        if base.endswith(f"/{bucket}"):
            download_url = f"{base}/{key}"
        else:
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


def cleanup_old_videos(bucket, prefix="videos/", hours_old=24):
    """
    Optional manual cleanup of videos older than N hours.
    Best practice: Enable S3 lifecycle rules instead (set expiration to 1 day in bucket config).
    
    This function is for auditing/verification only.
    
    Args:
        bucket: S3 bucket name
        prefix: object prefix to scan
        hours_old: delete objects older than this many hours
    
    Returns:
        dict with cleanup stats
    """
    endpoint_url = os.getenv("OBJECT_STORAGE_ENDPOINT", "").strip()
    access_key = os.getenv("OBJECT_STORAGE_ACCESS_KEY_ID", "").strip()
    secret_key = os.getenv("OBJECT_STORAGE_SECRET_ACCESS_KEY", "").strip()

    if not all([endpoint_url, access_key, secret_key]):
        return {
            "error": "Missing credentials",
            "deleted_count": 0,
        }

    try:
        s3 = boto3.client(
            "s3",
            region_name="us-east-1",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=BotoConfig(signature_version="s3v4"),
        )

        threshold = datetime.utcnow() - timedelta(hours=hours_old)
        to_delete = []

        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

        for page in pages:
            if "Contents" not in page:
                continue
            for obj in page["Contents"]:
                if obj["LastModified"].replace(tzinfo=None) < threshold:
                    to_delete.append({"Key": obj["Key"]})

        if to_delete:
            s3.delete_objects(Bucket=bucket, Delete={"Objects": to_delete})

        return {
            "deleted_count": len(to_delete),
            "threshold_before": threshold.isoformat(),
            "prefix": prefix,
        }

    except Exception as exc:
        return {
            "error": "Cleanup failed",
            "details": str(exc)[:500],
            "deleted_count": 0,
        }
