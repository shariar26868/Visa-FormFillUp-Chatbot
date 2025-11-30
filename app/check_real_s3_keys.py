"""
Check what S3 keys are actually stored in your database
"""

from app.core.storage import get_form_by_id, load_conversation
from app.core.aws_config import get_s3_client
from app.core.config import settings
from botocore.exceptions import ClientError

async def check_database_s3_keys(session_id: str):
    """Check if the S3 key in database actually exists in S3"""
    
    print(f"\n=== Checking Session: {session_id} ===")
    
    # Get conversation
    conv = await load_conversation(session_id)
    form_id = conv.get("matched_form_id")
    
    if not form_id:
        print("❌ No form matched in this session")
        return
    
    print(f"✅ Form ID: {form_id}")
    
    # Get form
    form = await get_form_by_id(form_id)
    
    if not form:
        print("❌ Form not found in database")
        return
    
    s3_key = form.get("s3_key")
    print(f"📄 S3 Key in DB: {s3_key}")
    
    if not s3_key:
        print("❌ No S3 key stored in database!")
        return
    
    # Check if file exists in S3
    s3 = get_s3_client()
    
    try:
        response = s3.head_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key
        )
        print(f"✅ File EXISTS in S3!")
        print(f"   Size: {response['ContentLength']} bytes")
        print(f"   Last Modified: {response['LastModified']}")
        
        # Try to generate presigned URL
        url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=300
        )
        print(f"✅ Presigned URL generated successfully!")
        print(f"   URL: {url[:80]}...")
        print(f"\n🔗 Try this URL in browser: {url}")
        
        return {
            "success": True,
            "s3_key": s3_key,
            "url": url,
            "file_exists": True
        }
        
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"❌ FILE NOT FOUND in S3!")
            print(f"   The s3_key '{s3_key}' doesn't exist in bucket")
            print(f"\n💡 Solution: Re-upload the PDF or fix the s3_key in database")
        else:
            print(f"❌ Error: {e.response['Error']['Code']}")
            print(f"   Message: {e.response['Error']['Message']}")
        
        return {
            "success": False,
            "s3_key": s3_key,
            "error": str(e),
            "file_exists": False
        }


async def list_all_s3_files():
    """List all files currently in S3 bucket"""
    
    print(f"\n=== Files in S3 Bucket: {settings.S3_BUCKET_NAME} ===")
    
    s3 = get_s3_client()
    
    try:
        response = s3.list_objects_v2(
            Bucket=settings.S3_BUCKET_NAME,
            MaxKeys=100
        )
        
        if 'Contents' not in response:
            print("📭 Bucket is empty")
            return []
        
        files = []
        for obj in response['Contents']:
            key = obj['Key']
            size = obj['Size']
            modified = obj['LastModified']
            files.append(key)
            print(f"📄 {key}")
            print(f"   Size: {size} bytes | Modified: {modified}")
        
        print(f"\n✅ Total files: {len(files)}")
        return files
        
    except ClientError as e:
        print(f"❌ Error listing files: {e}")
        return []


# Add this endpoint to session.py
"""
@router.get("/check-s3/{session_id}")
async def check_s3_key(session_id: str):
    from app.check_real_s3_keys import check_database_s3_keys
    result = await check_database_s3_keys(session_id)
    return result

@router.get("/list-s3-files")
async def list_s3_files():
    from app.check_real_s3_keys import list_all_s3_files
    files = await list_all_s3_files()
    return {"files": files, "count": len(files)}
"""