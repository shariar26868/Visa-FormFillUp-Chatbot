

# # ============================================
# # FILE: app/api/forms.py (FIXED VERSION)
# # ============================================
# """
# Forms Upload API - FIXED ASYNC
# """

# import os
# import uuid
# from fastapi import APIRouter, UploadFile, File, HTTPException
# from app.models.schemas import FormUploadResponse
# from app.services.s3_service import upload_pdf_to_s3, download_pdf_from_s3
# from app.services.ocr_service import analyze_form_with_vision
# from app.core.storage import save_form_to_db, save_pdf_document

# router = APIRouter()

# @router.post("/upload-form", response_model=FormUploadResponse)
# async def upload_form(file: UploadFile = File(...)):
#     """Upload PDF form → S3 → OCR → MongoDB"""
    
#     if not file.filename.endswith('.pdf'):
#         raise HTTPException(400, "Only PDF files allowed")
    
#     try:
#         # 1. Upload to S3
#         print(f"📤 Uploading {file.filename} to S3...")
#         s3_data = upload_pdf_to_s3(file.file, file.filename)
        
#         # 2. Save PDF metadata (✅ FIXED: Added await)
#         pdf_doc_id = await save_pdf_document({
#             "filename": file.filename,
#             "s3_key": s3_data["s3_key"],
#             "s3_url": s3_data["s3_url"]
#         })
        
#         print(f"✅ PDF metadata saved: {pdf_doc_id}")
        
#         # 3. Download from S3 for OCR
#         temp_path = f"/tmp/{uuid.uuid4()}.pdf"
#         download_success = download_pdf_from_s3(s3_data["s3_key"], temp_path)
        
#         if not download_success:
#             raise Exception("Failed to download PDF from S3")
        
#         print(f"✅ Downloaded from S3 to: {temp_path}")
        
#         # 4. OCR with Vision
#         print(f"🔍 Running OCR on {file.filename}...")
#         form_data = await analyze_form_with_vision(temp_path, file.filename)
        
#         # 5. Generate form_id
#         form_data["form_id"] = str(uuid.uuid4())
#         form_data["pdf_doc_id"] = pdf_doc_id
#         form_data["s3_key"] = s3_data["s3_key"]
        
#         # 6. Save to MongoDB (✅ FIXED: Added await)
#         await save_form_to_db(form_data)
        
#         # 7. Cleanup
#         if os.path.exists(temp_path):
#             os.remove(temp_path)
#             print(f"✅ Cleaned up temp file")
        
#         print(f"✅ Form uploaded & processed: {form_data['form_id']}")
#         print(f"📊 Extracted fields: {len(form_data.get('fields', []))}")
        
#         return FormUploadResponse(
#             success=True,
#             message="Form uploaded & processed successfully",
#             form_id=form_data["form_id"],
#             extracted_fields=len(form_data.get("fields", []))
#         )
    
#     except Exception as e:
#         print(f"❌ Upload failed: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(500, str(e))

# @router.get("/forms")
# async def list_forms():
#     """List all uploaded forms"""
#     from app.core.storage import load_forms_db
    
#     # ✅ FIXED: Added await
#     forms = await load_forms_db()
    
#     return {
#         "forms": forms,
#         "count": len(forms),
#         "status": "success"
#     }




"""
Forms Upload API - FIXED ASYNC + MULTIPLE PDF SUPPORT
"""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.models.schemas import FormUploadResponse
from app.services.s3_service import upload_pdf_to_s3, download_pdf_from_s3
from app.services.ocr_service import analyze_form_with_vision
from app.core.storage import save_form_to_db, save_pdf_document

router = APIRouter()

@router.post("/upload-form", response_model=FormUploadResponse)
async def upload_form(file: UploadFile = File(...)):
    """Upload single PDF form → S3 → OCR → MongoDB"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    try:
        # 1. Upload to S3
        print(f"Uploading {file.filename} to S3...")
        s3_data = upload_pdf_to_s3(file.file, file.filename)
        
        # 2. Save PDF metadata
        pdf_doc_id = await save_pdf_document({
            "filename": file.filename,
            "s3_key": s3_data["s3_key"],
            "s3_url": s3_data["s3_url"]
        })
        
        print(f"PDF metadata saved: {pdf_doc_id}")
        
        # 3. Download from S3 for OCR
        temp_path = f"/tmp/{uuid.uuid4()}.pdf"
        download_success = download_pdf_from_s3(s3_data["s3_key"], temp_path)
        
        if not download_success:
            raise Exception("Failed to download PDF from S3")
        
        print(f"Downloaded from S3 to: {temp_path}")
        
        # 4. OCR with Vision
        print(f"Running OCR on {file.filename}...")
        form_data = await analyze_form_with_vision(temp_path, file.filename)
        
        # 5. Generate form_id
        form_data["form_id"] = str(uuid.uuid4())
        form_data["pdf_doc_id"] = pdf_doc_id
        form_data["s3_key"] = s3_data["s3_key"]
        
        # 6. Save to MongoDB
        await save_form_to_db(form_data)
        
        # 7. Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Cleaned up temp file")
        
        print(f"Form uploaded & processed: {form_data['form_id']}")
        print(f"Extracted fields: {len(form_data.get('fields', []))}")
        
        return FormUploadResponse(
            success=True,
            message="Form uploaded & processed successfully",
            form_id=form_data["form_id"],
            extracted_fields=len(form_data.get("fields", []))
        )
    
    except Exception as e:
        print(f"Upload failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.post("/upload-forms-bulk")
async def upload_multiple_forms(files: List[UploadFile] = File(...)):
    """
    Upload multiple PDF forms at once
    Returns list of results for each file
    """
    
    if not files:
        raise HTTPException(400, "No files provided")
    
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        try:
            # Validate PDF
            if not file.filename.endswith('.pdf'):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "Only PDF files allowed"
                })
                failed += 1
                continue
            
            print(f"Processing {file.filename}...")
            
            # 1. Upload to S3
            s3_data = upload_pdf_to_s3(file.file, file.filename)
            
            # 2. Save PDF metadata
            pdf_doc_id = await save_pdf_document({
                "filename": file.filename,
                "s3_key": s3_data["s3_key"],
                "s3_url": s3_data["s3_url"]
            })
            
            # 3. Download from S3 for OCR
            temp_path = f"/tmp/{uuid.uuid4()}.pdf"
            download_success = download_pdf_from_s3(s3_data["s3_key"], temp_path)
            
            if not download_success:
                raise Exception("Failed to download PDF from S3")
            
            # 4. OCR with Vision
            form_data = await analyze_form_with_vision(temp_path, file.filename)
            
            # 5. Generate form_id
            form_data["form_id"] = str(uuid.uuid4())
            form_data["pdf_doc_id"] = pdf_doc_id
            form_data["s3_key"] = s3_data["s3_key"]
            
            # 6. Save to MongoDB
            await save_form_to_db(form_data)
            
            # 7. Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Success
            results.append({
                "filename": file.filename,
                "success": True,
                "form_id": form_data["form_id"],
                "extracted_fields": len(form_data.get("fields", []))
            })
            successful += 1
            
            print(f"Successfully processed: {file.filename}")
        
        except Exception as e:
            print(f"Failed to process {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
            failed += 1
    
    return {
        "total_files": len(files),
        "successful": successful,
        "failed": failed,
        "results": results
    }


@router.get("/forms")
async def list_forms():
    """List all uploaded forms"""
    from app.core.storage import load_forms_db
    
    forms = await load_forms_db()
    
    return {
        "forms": forms,
        "count": len(forms),
        "status": "success"
    }