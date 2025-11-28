# """
# S3 Upload/Download Service
# """

# import os
# import uuid
# from datetime import datetime
# from typing import BinaryIO
# from botocore.exceptions import ClientError
# from app.core.config import settings
# from app.core.aws_config import get_s3_client

# def upload_pdf_to_s3(file: BinaryIO, filename: str) -> dict:
#     try:
#         s3 = get_s3_client()
#         timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
#         unique_id = str(uuid.uuid4())[:8]
#         s3_key = f"uploads/{timestamp}_{unique_id}_{filename}"
        
#         s3.upload_fileobj(
#             file,
#             settings.S3_BUCKET_NAME,
#             s3_key,
#             ExtraArgs={'ContentType': 'application/pdf'}
#         )
        
#         s3_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
#         print(f"✅ Uploaded: {s3_key}")
        
#         return {
#             "s3_key": s3_key,
#             "s3_url": s3_url,
#             "filename": filename,
#             "bucket": settings.S3_BUCKET_NAME
#         }
#     except ClientError as e:
#         raise Exception(f"S3 upload failed: {str(e)}")

# def download_pdf_from_s3(s3_key: str, local_path: str) -> bool:
#     try:
#         s3 = get_s3_client()
#         os.makedirs(os.path.dirname(local_path), exist_ok=True)
#         s3.download_file(settings.S3_BUCKET_NAME, s3_key, local_path)
#         print(f"✅ Downloaded: {s3_key}")
#         return True
#     except ClientError as e:
#         print(f"❌ Download failed: {e}")
#         return False




"""
S3 Upload/Download/Delete Service - UPDATED
"""

import os
import uuid
from datetime import datetime
from typing import BinaryIO
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.aws_config import get_s3_client

def upload_pdf_to_s3(file: BinaryIO, filename: str) -> dict:
    try:
        s3 = get_s3_client()
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        s3_key = f"uploads/{timestamp}_{unique_id}_{filename}"
        
        s3.upload_fileobj(
            file,
            settings.S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={'ContentType': 'application/pdf'}
        )
        
        s3_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        print(f"✅ Uploaded: {s3_key}")
        
        return {
            "s3_key": s3_key,
            "s3_url": s3_url,
            "filename": filename,
            "bucket": settings.S3_BUCKET_NAME
        }
    except ClientError as e:
        raise Exception(f"S3 upload failed: {str(e)}")

def download_pdf_from_s3(s3_key: str, local_path: str) -> bool:
    try:
        s3 = get_s3_client()
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        s3.download_file(settings.S3_BUCKET_NAME, s3_key, local_path)
        print(f"✅ Downloaded: {s3_key}")
        return True
    except ClientError as e:
        print(f"❌ Download failed: {e}")
        return False

# ✅ NEW: Delete PDF from S3
def delete_pdf_from_s3(s3_key: str) -> bool:
    """Delete PDF file from S3 bucket"""
    try:
        s3 = get_s3_client()
        s3.delete_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key
        )
        print(f"✅ Deleted from S3: {s3_key}")
        return True
    except ClientError as e:
        print(f"❌ S3 delete failed: {e}")
        return False

# ✅ NEW: Delete multiple PDFs from S3
def delete_multiple_pdfs_from_s3(s3_keys: list) -> dict:
    """Delete multiple PDF files from S3"""
    try:
        s3 = get_s3_client()
        
        # Prepare delete request
        objects = [{"Key": key} for key in s3_keys]
        
        response = s3.delete_objects(
            Bucket=settings.S3_BUCKET_NAME,
            Delete={'Objects': objects}
        )
        
        deleted = response.get('Deleted', [])
        errors = response.get('Errors', [])
        
        print(f"✅ Deleted {len(deleted)} files from S3")
        if errors:
            print(f"⚠️  {len(errors)} files failed to delete")
        
        return {
            "deleted_count": len(deleted),
            "failed_count": len(errors),
            "deleted": deleted,
            "errors": errors
        }
    except ClientError as e:
        print(f"❌ Bulk S3 delete failed: {e}")
        return {
            "deleted_count": 0,
            "failed_count": len(s3_keys),
            "deleted": [],
            "errors": [{"Key": key, "Message": str(e)} for key in s3_keys]
        }