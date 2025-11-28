# """
# Session Management API
# """

# from fastapi import APIRouter, HTTPException
# from app.models.schemas import SummaryResponse
# from app.core.storage import get_summary, load_conversation, get_form_by_id

# router = APIRouter()

# @router.get("/summary/{session_id}", response_model=SummaryResponse)
# async def get_session_summary(session_id: str):
#     """Get final summary"""
    
#     # ✅ await যোগ করুন
#     summary = await get_summary(session_id)
#     if summary:
#         return summary
    
#     # Generate from conversation
#     # ✅ await যোগ করুন
#     conv = await load_conversation(session_id)
    
#     # ✅ await যোগ করুন
#     form = await get_form_by_id(conv.get("matched_form_id"))
    
#     if not form:
#         raise HTTPException(status_code=404, detail="Summary not found")
    
#     return SummaryResponse(
#         session_id=session_id,
#         form_title=form.get("title", ""),
#         visa_type=form.get("visa_type", ""),
#         country=form.get("country", ""),
#         personal_info={},
#         answers=conv.get("answers", {}),
#         completion_status=conv.get("state", "")
#     )





"""
Session Management API - UPDATED with PDF link endpoint
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import SummaryResponse, PDFLinkResponse
from app.core.storage import get_summary, load_conversation, get_form_by_id
from app.services.s3_service import download_pdf_from_s3

router = APIRouter()

@router.get("/summary/{session_id}", response_model=SummaryResponse)
async def get_session_summary(session_id: str):
    """Get final summary"""
    
    summary = await get_summary(session_id)
    if summary:
        return summary
    
    # Generate from conversation
    conv = await load_conversation(session_id)
    form = await get_form_by_id(conv.get("matched_form_id"))
    
    if not form:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    return SummaryResponse(
        session_id=session_id,
        form_title=form.get("title", ""),
        visa_type=form.get("visa_type", ""),
        country=form.get("country", ""),
        personal_info={},
        answers=conv.get("answers", {}),
        completion_status=conv.get("state", "")
    )


# ✅ NEW: Get PDF link for matched form
@router.get("/form-pdf/{session_id}", response_model=PDFLinkResponse)
async def get_form_pdf_link(session_id: str):
    """
    Get PDF download link for the matched form in current session
    Usage: /api/form-pdf/{session_id}
    """
    
    try:
        # Load conversation
        conv = await load_conversation(session_id)
        
        # Get matched form ID
        form_id = conv.get("matched_form_id")
        
        if not form_id:
            raise HTTPException(
                status_code=404, 
                detail="No form matched yet in this session"
            )
        
        # Get form details
        form = await get_form_by_id(form_id)
        
        if not form:
            raise HTTPException(
                status_code=404,
                detail="Form not found"
            )
        
        # Get S3 info
        s3_key = form.get("s3_key")
        
        if not s3_key:
            return PDFLinkResponse(
                success=False,
                form_id=form_id,
                title=form.get("title", ""),
                visa_type=form.get("visa_type", ""),
                country=form.get("country", "Unknown"),
                pdf_url=None,
                s3_key=None,
                filename="",
                message="PDF file not available for this form"
            )
        
        # Generate S3 URL
        from app.core.config import settings
        pdf_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        
        # Extract filename
        filename = s3_key.split('/')[-1] if '/' in s3_key else s3_key
        
        return PDFLinkResponse(
            success=True,
            form_id=form_id,
            title=form.get("title", ""),
            visa_type=form.get("visa_type", ""),
            country=form.get("country", "Unknown"),
            pdf_url=pdf_url,
            s3_key=s3_key,
            filename=filename,
            message="PDF link retrieved successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting PDF link: {e}")
        raise HTTPException(status_code=500, detail=str(e))