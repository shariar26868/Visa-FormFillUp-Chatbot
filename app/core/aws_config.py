"""
AWS S3 Configuration
"""

import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

def verify_s3_connection() -> bool:
    try:
        s3 = get_s3_client()
        s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        print(f"✅ S3 bucket accessible: {settings.S3_BUCKET_NAME}")
        return True
    except ClientError as e:
        print(f"❌ S3 connection failed: {e}")
        return False
