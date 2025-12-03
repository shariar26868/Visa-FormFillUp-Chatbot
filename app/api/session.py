"""
Session Management API - UPDATED with PDF link and chat history endpoints
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import SummaryResponse, PDFLinkResponse, ChatHistoryResponse, ChatMessage
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



# # ✅ Get PDF link for matched form
# @router.get("/form-pdf/{session_id}", response_model=PDFLinkResponse)
# async def get_form_pdf_link(session_id: str):
#     """
#     Get PDF download link for the matched form in current session
#     Usage: /api/form-pdf/{session_id}
#     """
    
#     try:
#         # Load conversation
#         conv = await load_conversation(session_id)
        
#         # Get matched form ID
#         form_id = conv.get("matched_form_id")
        
#         if not form_id:
#             raise HTTPException(
#                 status_code=404, 
#                 detail="No form matched yet in this session"
#             )
        
#         # Get form details
#         form = await get_form_by_id(form_id)
        
#         if not form:
#             raise HTTPException(
#                 status_code=404,
#                 detail="Form not found"
#             )
        
#         # Get S3 info
#         s3_key = form.get("s3_key")
        
#         if not s3_key:
#             return PDFLinkResponse(
#                 success=False,
#                 form_id=form_id,
#                 title=form.get("title", ""),
#                 visa_type=form.get("visa_type", ""),
#                 country=form.get("country", "Unknown"),
#                 pdf_url=None,
#                 s3_key=None,
#                 filename="",
#                 message="PDF file not available for this form"
#             )
        
#         # Generate S3 URL
#         from app.core.config import settings
#         pdf_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        
#         # Extract filename
#         filename = s3_key.split('/')[-1] if '/' in s3_key else s3_key
        
#         return PDFLinkResponse(
#             success=True,
#             form_id=form_id,
#             title=form.get("title", ""),
#             visa_type=form.get("visa_type", ""),
#             country=form.get("country", "Unknown"),
#             pdf_url=pdf_url,
#             s3_key=s3_key,
#             filename=filename,
#             message="PDF link retrieved successfully"
#         )
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"Error getting PDF link: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
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
        
        # ✅ UPDATED: Generate presigned URL (secure, works even with private bucket)
        from app.services.s3_service import generate_presigned_url
        pdf_url = generate_presigned_url(s3_key, expiration=7200)  # 2 hours validity
        
        # Extract filename
        filename = s3_key.split('/')[-1] if '/' in s3_key else s3_key
        
        return PDFLinkResponse(
            success=True,
            form_id=form_id,
            title=form.get("title", ""),
            visa_type=form.get("visa_type", ""),
            country=form.get("country", "Unknown"),
            pdf_url=pdf_url,  # ✅ Now using presigned URL
            s3_key=s3_key,
            filename=filename,
            message="PDF link retrieved successfully (valid for 2 hours)"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting PDF link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ NEW: Get chat history
@router.get("/chat-history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get full chat history for a session
    Usage: GET /api/chat-history/{session_id}
    """
    try:
        conv = await load_conversation(session_id)
        
        if not conv or not conv.get("history"):
            return {
                "success": False,
                "session_id": session_id,
                "state": "chatting",
                "total_messages": 0,
                "history": [],
                "message": "No chat history found"
            }
        
        history = conv.get("history", [])
        state = conv.get("state", "chatting")
        
        # Format history nicely
        formatted_history = []
        for msg in history:
            formatted_history.append({
                "role": msg.get("role"),
                "content": msg.get("content"),
                "timestamp": msg.get("timestamp", None)
            })
        
        return {
            "success": True,
            "session_id": session_id,
            "state": state,
            "total_messages": len(history),
            "history": formatted_history,
            "created_at": conv.get("created_at"),
            "updated_at": conv.get("updated_at")
        }
    
    except Exception as e:
        print(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ✅ NEW: Clear chat history
@router.delete("/chat-history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear/reset chat history for a session
    Usage: DELETE /api/chat-history/{session_id}
    """
    try:
        from app.services.conversation_manager import ConversationManager
        
        await ConversationManager.reset_session(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Chat history cleared successfully"
        }
    
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#############
@router.get("/check-s3/{session_id}")
async def check_s3_key(session_id: str):
    """Check if S3 file exists for this session"""
    from app.check_real_s3_keys import check_database_s3_keys
    result = await check_database_s3_keys(session_id)
    return result

@router.get("/list-s3-files")
async def list_s3_files():
    """List all files in S3 bucket"""
    from app.check_real_s3_keys import list_all_s3_files
    files = await list_all_s3_files()
    return {"files": files, "count": len(files)}