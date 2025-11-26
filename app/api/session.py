"""
Session Management API
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import SummaryResponse
from app.core.storage import get_summary, load_conversation, get_form_by_id

router = APIRouter()

@router.get("/summary/{session_id}", response_model=SummaryResponse)
async def get_session_summary(session_id: str):
    """Get final summary"""
    
    # ✅ await যোগ করুন
    summary = await get_summary(session_id)
    if summary:
        return summary
    
    # Generate from conversation
    # ✅ await যোগ করুন
    conv = await load_conversation(session_id)
    
    # ✅ await যোগ করুন
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