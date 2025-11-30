"""
Debug S3 Access - Run this to find the problem
"""

from app.core.aws_config import get_s3_client
from app.core.config import settings
from botocore.exceptions import ClientError

def test_s3_access():
    """Test S3 access and permissions"""
    
    print("\n=== S3 Configuration ===")
    print(f"Bucket: {settings.S3_BUCKET_NAME}")
    print(f"Region: {settings.AWS_REGION}")
    
    try:
        s3 = get_s3_client()
        print("✅ S3 client created")
        
        # Test 1: List bucket (basic access)
        print("\n=== Test 1: List Bucket ===")
        try:
            response = s3.list_objects_v2(
                Bucket=settings.S3_BUCKET_NAME,
                MaxKeys=5
            )
            print(f"✅ Can list bucket - found {response.get('KeyCount', 0)} objects")
        except ClientError as e:
            print(f"❌ Cannot list bucket: {e.response['Error']['Code']}")
            print(f"   Message: {e.response['Error']['Message']}")
        
        # Test 2: Check if a specific file exists
        print("\n=== Test 2: Check File Access ===")
        # Replace this with an actual s3_key from your database
        test_key = "uploads/test.pdf"  # Change this to real key
        
        try:
            s3.head_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=test_key
            )
            print(f"✅ Can access file: {test_key}")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"⚠️  File not found (normal if you don't have this file)")
            else:
                print(f"❌ Cannot access file: {e.response['Error']['Code']}")
        
        # Test 3: Generate presigned URL
        print("\n=== Test 3: Generate Presigned URL ===")
        try:
            url = s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.S3_BUCKET_NAME,
                    'Key': test_key
                },
                ExpiresIn=300
            )
            print("✅ Presigned URL generated successfully!")
            print(f"URL: {url[:100]}...")
            
        except ClientError as e:
            print(f"❌ Presigned URL failed: {e.response['Error']['Code']}")
            print(f"   Message: {e.response['Error']['Message']}")
        
        # Test 4: Check AWS credentials
        print("\n=== Test 4: AWS Credentials ===")
        try:
            sts = get_s3_client()._client_config.__dict__
            print("✅ Credentials loaded")
            
            # Try to get caller identity
            import boto3
            sts_client = boto3.client('sts')
            identity = sts_client.get_caller_identity()
            print(f"✅ AWS Account: {identity['Account']}")
            print(f"✅ User ARN: {identity['Arn']}")
            
        except Exception as e:
            print(f"❌ Credential check failed: {str(e)}")
        
        print("\n=== Summary ===")
        print("If all tests passed ✅, the problem is with the specific S3 key")
        print("If Test 3 failed ❌, check IAM permissions for s3:GetObject")
        print("If Test 1 failed ❌, check bucket name and region settings")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_s3_access()