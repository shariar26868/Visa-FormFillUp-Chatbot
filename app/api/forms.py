"""
Forms Upload API - FIXED with Presigned URLs
"""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.models.schemas import (
    FormUploadResponse, 
    PDFListResponse, 
    DeletePDFsRequest, 
    DeletePDFsResponse
)
from app.services.s3_service import (
    upload_pdf_to_s3, 
    download_pdf_from_s3,
    delete_pdf_from_s3,
    delete_multiple_pdfs_from_s3,
    generate_presigned_url  # ✅ Added this import
)
from app.services.ocr_service import analyze_form_with_vision
from app.core.storage import (
    save_form_to_db, 
    save_pdf_document,
    get_all_pdf_documents,
    get_pdf_document,
    delete_pdf_document,
    delete_form_by_pdf_doc_id
)

router = APIRouter()


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
            
            print(f"✅ Successfully processed: {file.filename}")
        
        except Exception as e:
            print(f"❌ Failed to process {file.filename}: {e}")
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


# ✅ FIXED: Get all uploaded PDFs with PRESIGNED URLs
@router.get("/pdfs", response_model=PDFListResponse)
async def list_all_pdfs():
    """
    Get list of all uploaded PDFs with form information
    Usage: GET /api/pdfs
    """
    try:
        pdfs = await get_all_pdf_documents()
        
        # ✅ Generate presigned URLs for each PDF
        for pdf in pdfs:
            s3_key = pdf.get("s3_key")
            if s3_key:
                try:
                    # Generate fresh presigned URL (2 hours validity)
                    pdf["s3_url"] = generate_presigned_url(s3_key, expiration=7200)
                except Exception as e:
                    print(f"⚠️  Failed to generate presigned URL for {s3_key}: {e}")
                    pdf["s3_url"] = None
        
        return PDFListResponse(
            success=True,
            total_pdfs=len(pdfs),
            pdfs=pdfs
        )
    
    except Exception as e:
        print(f"❌ Error listing PDFs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ✅ NEW: Delete multiple PDFs
@router.post("/delete-pdfs", response_model=DeletePDFsResponse)
async def delete_multiple_pdfs(request: DeletePDFsRequest):
    """
    Delete multiple PDFs and their associated forms
    
    Request body:
    {
        "pdf_doc_ids": ["id1", "id2", "id3"]
    }
    """
    
    if not request.pdf_doc_ids:
        raise HTTPException(400, "No PDF IDs provided")
    
    try:
        deleted_count = 0
        failed_count = 0
        details = []
        s3_keys_to_delete = []
        
        # Process each PDF
        for pdf_doc_id in request.pdf_doc_ids:
            try:
                # Get PDF info
                pdf_doc = await get_pdf_document(pdf_doc_id)
                
                if not pdf_doc:
                    details.append({
                        "pdf_doc_id": pdf_doc_id,
                        "success": False,
                        "error": "PDF not found"
                    })
                    failed_count += 1
                    continue
                
                s3_key = pdf_doc.get("s3_key")
                filename = pdf_doc.get("filename", "Unknown")
                
                # Delete from MongoDB
                deleted_pdf = await delete_pdf_document(pdf_doc_id)
                deleted_form = await delete_form_by_pdf_doc_id(pdf_doc_id)
                
                if deleted_pdf:
                    # Add to S3 delete list
                    if s3_key:
                        s3_keys_to_delete.append(s3_key)
                    
                    details.append({
                        "pdf_doc_id": pdf_doc_id,
                        "filename": filename,
                        "success": True,
                        "deleted_form": deleted_form,
                        "message": "Deleted successfully"
                    })
                    deleted_count += 1
                else:
                    details.append({
                        "pdf_doc_id": pdf_doc_id,
                        "filename": filename,
                        "success": False,
                        "error": "Failed to delete from database"
                    })
                    failed_count += 1
            
            except Exception as e:
                details.append({
                    "pdf_doc_id": pdf_doc_id,
                    "success": False,
                    "error": str(e)
                })
                failed_count += 1
        
        # Delete from S3 in batch
        if s3_keys_to_delete:
            s3_result = delete_multiple_pdfs_from_s3(s3_keys_to_delete)
            print(f"S3 deletion: {s3_result['deleted_count']} deleted, {s3_result['failed_count']} failed")
        
        message = f"Successfully deleted {deleted_count} PDF(s)"
        if failed_count > 0:
            message += f", {failed_count} failed"
        
        return DeletePDFsResponse(
            success=deleted_count > 0,
            deleted_count=deleted_count,
            failed_count=failed_count,
            details=details,
            message=message
        )
    
    except Exception as e:
        print(f"❌ Bulk delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ✅ NEW: Delete single PDF (convenience endpoint)
@router.delete("/pdf/{pdf_doc_id}")
async def delete_single_pdf(pdf_doc_id: str):
    """
    Delete a single PDF and its associated form
    Usage: DELETE /api/pdf/{pdf_doc_id}
    """
    try:
        # Get PDF info
        pdf_doc = await get_pdf_document(pdf_doc_id)
        
        if not pdf_doc:
            raise HTTPException(404, "PDF not found")
        
        s3_key = pdf_doc.get("s3_key")
        filename = pdf_doc.get("filename", "Unknown")
        
        # Delete from MongoDB
        deleted_pdf = await delete_pdf_document(pdf_doc_id)
        deleted_form = await delete_form_by_pdf_doc_id(pdf_doc_id)
        
        # Delete from S3
        if s3_key:
            delete_pdf_from_s3(s3_key)
        
        if deleted_pdf:
            return {
                "success": True,
                "message": f"Successfully deleted {filename}",
                "pdf_doc_id": pdf_doc_id,
                "deleted_form": deleted_form
            }
        else:
            raise HTTPException(500, "Failed to delete PDF")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Delete error: {e}")
        raise HTTPException(500, str(e))