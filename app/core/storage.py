# # ============================================
# # FILE: app/core/storage.py (FIXED VERSION)
# # ============================================




# """
# MongoDB Storage Operations - ASYNC FIXED
# """

# import json
# import os
# from typing import Dict, List, Optional
# from datetime import datetime
# from bson import ObjectId
# from app.core.database import (
#     get_conversations_collection,
#     get_forms_collection,
#     get_pdf_documents_collection,
#     get_summaries_collection
# )

# LOCAL_STORAGE_DIR = "storage"
# os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)

# # ========== CONVERSATION STORAGE ==========

# async def load_conversation(session_id: str) -> Dict:
#     """Load conversation from MongoDB (ASYNC)"""
#     try:
#         collection = get_conversations_collection()
#         doc = await collection.find_one({"session_id": session_id})
        
#         if doc:
#             doc.pop("_id", None)
#             return doc
#         else:
#             return {
#                 "session_id": session_id,
#                 "state": "chatting",
#                 "history": [],
#                 "matched_form_id": None,
#                 "current_field_index": 0,
#                 "answers": {},
#                 "created_at": datetime.utcnow().isoformat()
#             }
#     except Exception as e:
#         print(f"⚠️  MongoDB read failed: {e}")
#         return _load_local_conversation(session_id)

# async def save_conversation(session_id: str, data: Dict) -> bool:
#     """Save conversation to MongoDB (ASYNC)"""
#     try:
#         collection = get_conversations_collection()
#         data["session_id"] = session_id
#         data["updated_at"] = datetime.utcnow().isoformat()
        
#         await collection.update_one(
#             {"session_id": session_id},
#             {"$set": data},
#             upsert=True
#         )
#         return True
#     except Exception as e:
#         print(f"⚠️  MongoDB write failed: {e}")
#         return _save_local_conversation(session_id, data)

# def _load_local_conversation(session_id: str) -> Dict:
#     """Fallback: Load from local file"""
#     filepath = os.path.join(LOCAL_STORAGE_DIR, f"{session_id}.json")
#     if os.path.exists(filepath):
#         with open(filepath, 'r') as f:
#             return json.load(f)
#     return {
#         "session_id": session_id,
#         "state": "chatting",
#         "history": [],
#         "matched_form_id": None,
#         "current_field_index": 0,
#         "answers": {}
#     }

# def _save_local_conversation(session_id: str, data: Dict) -> bool:
#     """Fallback: Save to local file"""
#     filepath = os.path.join(LOCAL_STORAGE_DIR, f"{session_id}.json")
#     with open(filepath, 'w') as f:
#         json.dump(data, f, indent=2)
#     return True

# # ========== FORMS STORAGE ==========

# async def load_forms_db() -> List[Dict]:
#     """Load all forms from MongoDB (ASYNC)"""
#     try:
#         collection = get_forms_collection()
#         forms = await collection.find({}).to_list(length=None)
#         for form in forms:
#             form.pop("_id", None)
#         return forms
#     except Exception as e:
#         print(f"⚠️  Forms load failed: {e}")
#         return []

# async def get_form_by_id(form_id: str) -> Optional[Dict]:
#     """Get single form by form_id (ASYNC)"""
#     try:
#         collection = get_forms_collection()
#         form = await collection.find_one({"form_id": form_id})
#         if form:
#             form.pop("_id", None)
#             return form
#         return None
#     except Exception as e:
#         print(f"⚠️  Form fetch failed: {e}")
#         return None

# async def save_form_to_db(form_data: Dict) -> bool:
#     """Save or update form in MongoDB (ASYNC)"""
#     try:
#         collection = get_forms_collection()
#         form_id = form_data.get("form_id")
#         if not form_id:
#             return False
        
#         form_data["updated_at"] = datetime.utcnow().isoformat()
#         await collection.update_one(
#             {"form_id": form_id},
#             {"$set": form_data},
#             upsert=True
#         )
#         print(f"✅ Form saved: {form_id}")
#         return True
#     except Exception as e:
#         print(f"❌ Form save failed: {e}")
#         return False

# # ========== PDF DOCUMENTS STORAGE (FIXED!) ==========

# async def save_pdf_document(doc_data: Dict) -> str:
#     """Save PDF document metadata (ASYNC - FIXED!)"""
#     try:
#         collection = get_pdf_documents_collection()
#         doc_data["uploaded_at"] = datetime.utcnow().isoformat()
        
#         # ✅ FIX: Add await here!
#         result = await collection.insert_one(doc_data)
#         return str(result.inserted_id)
#     except Exception as e:
#         print(f"❌ PDF save failed: {e}")
#         return None

# async def get_pdf_document(doc_id: str) -> Optional[Dict]:
#     """Get PDF document by ID (ASYNC)"""
#     try:
#         collection = get_pdf_documents_collection()
#         doc = await collection.find_one({"_id": ObjectId(doc_id)})
#         if doc:
#             doc["_id"] = str(doc["_id"])
#             return doc
#         return None
#     except Exception as e:
#         return None

# # ========== SUMMARY STORAGE ==========

# async def save_summary(session_id: str, summary_data: Dict) -> bool:
#     """Save final summary (ASYNC)"""
#     try:
#         collection = get_summaries_collection()
#         summary_data["session_id"] = session_id
#         summary_data["created_at"] = datetime.utcnow().isoformat()
#         await collection.update_one(
#             {"session_id": session_id},
#             {"$set": summary_data},
#             upsert=True
#         )
#         return True
#     except Exception as e:
#         return False

# async def get_summary(session_id: str) -> Optional[Dict]:
#     """Get summary by session_id (ASYNC)"""
#     try:
#         collection = get_summaries_collection()
#         summary = await collection.find_one({"session_id": session_id})
#         if summary:
#             summary.pop("_id", None)
#             return summary
#         return None
#     except Exception as e:
#         return None






"""
MongoDB Storage Operations - UPDATED with PDF management
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId
from app.core.database import (
    get_conversations_collection,
    get_forms_collection,
    get_pdf_documents_collection,
    get_summaries_collection
)

LOCAL_STORAGE_DIR = "storage"
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)

# ========== CONVERSATION STORAGE ==========

async def load_conversation(session_id: str) -> Dict:
    """Load conversation from MongoDB (ASYNC)"""
    try:
        collection = get_conversations_collection()
        doc = await collection.find_one({"session_id": session_id})
        
        if doc:
            doc.pop("_id", None)
            return doc
        else:
            return {
                "session_id": session_id,
                "state": "chatting",
                "history": [],
                "matched_form_id": None,
                "current_field_index": 0,
                "answers": {},
                "created_at": datetime.utcnow().isoformat()
            }
    except Exception as e:
        print(f"⚠️  MongoDB read failed: {e}")
        return _load_local_conversation(session_id)

async def save_conversation(session_id: str, data: Dict) -> bool:
    """Save conversation to MongoDB (ASYNC)"""
    try:
        collection = get_conversations_collection()
        data["session_id"] = session_id
        data["updated_at"] = datetime.utcnow().isoformat()
        
        await collection.update_one(
            {"session_id": session_id},
            {"$set": data},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"⚠️  MongoDB write failed: {e}")
        return _save_local_conversation(session_id, data)

def _load_local_conversation(session_id: str) -> Dict:
    """Fallback: Load from local file"""
    filepath = os.path.join(LOCAL_STORAGE_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {
        "session_id": session_id,
        "state": "chatting",
        "history": [],
        "matched_form_id": None,
        "current_field_index": 0,
        "answers": {}
    }

def _save_local_conversation(session_id: str, data: Dict) -> bool:
    """Fallback: Save to local file"""
    filepath = os.path.join(LOCAL_STORAGE_DIR, f"{session_id}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    return True

# ========== FORMS STORAGE ==========

async def load_forms_db() -> List[Dict]:
    """Load all forms from MongoDB (ASYNC)"""
    try:
        collection = get_forms_collection()
        forms = await collection.find({}).to_list(length=None)
        for form in forms:
            form.pop("_id", None)
        return forms
    except Exception as e:
        print(f"⚠️  Forms load failed: {e}")
        return []

async def get_form_by_id(form_id: str) -> Optional[Dict]:
    """Get single form by form_id (ASYNC)"""
    try:
        collection = get_forms_collection()
        form = await collection.find_one({"form_id": form_id})
        if form:
            form.pop("_id", None)
            return form
        return None
    except Exception as e:
        print(f"⚠️  Form fetch failed: {e}")
        return None

async def save_form_to_db(form_data: Dict) -> bool:
    """Save or update form in MongoDB (ASYNC)"""
    try:
        collection = get_forms_collection()
        form_id = form_data.get("form_id")
        if not form_id:
            return False
        
        form_data["updated_at"] = datetime.utcnow().isoformat()
        await collection.update_one(
            {"form_id": form_id},
            {"$set": form_data},
            upsert=True
        )
        print(f"✅ Form saved: {form_id}")
        return True
    except Exception as e:
        print(f"❌ Form save failed: {e}")
        return False

# ========== PDF DOCUMENTS STORAGE ==========

async def save_pdf_document(doc_data: Dict) -> str:
    """Save PDF document metadata (ASYNC)"""
    try:
        collection = get_pdf_documents_collection()
        doc_data["uploaded_at"] = datetime.utcnow().isoformat()
        
        result = await collection.insert_one(doc_data)
        return str(result.inserted_id)
    except Exception as e:
        print(f"❌ PDF save failed: {e}")
        return None

async def get_pdf_document(doc_id: str) -> Optional[Dict]:
    """Get PDF document by ID (ASYNC)"""
    try:
        collection = get_pdf_documents_collection()
        doc = await collection.find_one({"_id": ObjectId(doc_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
            return doc
        return None
    except Exception as e:
        return None

# ✅ NEW: Get all PDF documents
async def get_all_pdf_documents() -> List[Dict]:
    """Get all PDF documents with form info (ASYNC)"""
    try:
        pdf_collection = get_pdf_documents_collection()
        forms_collection = get_forms_collection()
        
        # Get all PDFs
        pdfs = await pdf_collection.find({}).to_list(length=None)
        
        result = []
        for pdf in pdfs:
            pdf_data = {
                "pdf_doc_id": str(pdf["_id"]),
                "filename": pdf.get("filename", "Unknown"),
                "s3_key": pdf.get("s3_key", ""),
                "s3_url": pdf.get("s3_url", ""),
                "uploaded_at": pdf.get("uploaded_at", ""),
                "form_id": None,
                "form_title": None
            }
            
            # Find associated form
            form = await forms_collection.find_one({"pdf_doc_id": str(pdf["_id"])})
            if form:
                pdf_data["form_id"] = form.get("form_id")
                pdf_data["form_title"] = form.get("title")
            
            result.append(pdf_data)
        
        # Sort by upload date (newest first)
        result.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
        
        return result
    except Exception as e:
        print(f"❌ Get all PDFs failed: {e}")
        return []

# ✅ NEW: Delete PDF document
async def delete_pdf_document(doc_id: str) -> bool:
    """Delete PDF document metadata (ASYNC)"""
    try:
        collection = get_pdf_documents_collection()
        result = await collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"❌ PDF delete failed: {e}")
        return False

# ✅ NEW: Delete form by pdf_doc_id
async def delete_form_by_pdf_doc_id(pdf_doc_id: str) -> bool:
    """Delete form associated with PDF (ASYNC)"""
    try:
        collection = get_forms_collection()
        result = await collection.delete_one({"pdf_doc_id": pdf_doc_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"❌ Form delete failed: {e}")
        return False

# ========== SUMMARY STORAGE ==========

async def save_summary(session_id: str, summary_data: Dict) -> bool:
    """Save final summary (ASYNC)"""
    try:
        collection = get_summaries_collection()
        summary_data["session_id"] = session_id
        summary_data["created_at"] = datetime.utcnow().isoformat()
        await collection.update_one(
            {"session_id": session_id},
            {"$set": summary_data},
            upsert=True
        )
        return True
    except Exception as e:
        return False

async def get_summary(session_id: str) -> Optional[Dict]:
    """Get summary by session_id (ASYNC)"""
    try:
        collection = get_summaries_collection()
        summary = await collection.find_one({"session_id": session_id})
        if summary:
            summary.pop("_id", None)
            return summary
        return None
    except Exception as e:
        return None