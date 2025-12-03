"""
Pydantic Schemas - UPDATED with new endpoints
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

# ✅ NEW: PDF Link Response
class PDFLinkResponse(BaseModel):
    success: bool
    form_id: str
    title: str
    visa_type: str
    country: str
    pdf_url: Optional[str] = None
    s3_key: Optional[str] = None
    filename: str
    message: str

# ✅ NEW: PDF List Item
class PDFListItem(BaseModel):
    pdf_doc_id: str
    filename: str
    s3_key: str
    s3_url: str
    uploaded_at: str
    form_id: Optional[str] = None
    form_title: Optional[str] = None

# ✅ NEW: PDF List Response
class PDFListResponse(BaseModel):
    success: bool
    total_pdfs: int
    pdfs: List[PDFListItem]

# ✅ NEW: Delete Request
class DeletePDFsRequest(BaseModel):
    pdf_doc_ids: List[str]

# ✅ NEW: Delete Response
class DeletePDFsResponse(BaseModel):
    success: bool
    deleted_count: int
    failed_count: int
    details: List[Dict]
    message: str

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatHistoryResponse(BaseModel):
    success: bool
    session_id: str
    state: str
    total_messages: int
    history: List[ChatMessage]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    message: Optional[str] = None