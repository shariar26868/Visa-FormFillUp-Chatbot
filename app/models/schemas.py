"""
Pydantic Schemas
"""

from typing import Optional, Dict, List
from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    state: str
    is_form_ready: bool
    matched_form: Optional[Dict] = None
    multiple_forms: Optional[List[Dict]] = None

class FormUploadResponse(BaseModel):
    success: bool
    message: str
    form_id: Optional[str] = None
    extracted_fields: Optional[int] = None

class SummaryResponse(BaseModel):
    session_id: str
    form_title: str
    visa_type: str
    country: str
    personal_info: Dict
    answers: Dict
    completion_status: str