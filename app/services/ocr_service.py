"""
OCR service using PyMuPDF + OpenAI Vision
UNLIMITED FIELDS VERSION - No field limit!
"""

import json
import re
import base64
from io import BytesIO
from typing import List, Dict
import fitz  # PyMuPDF
from PIL import Image

from app.core.config import settings
from app.services.ai_service import call_openai_with_image, call_openai_chat

def encode_image(image: Image.Image) -> str:
    """Convert PIL image to base64"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

async def extract_data_from_pdf(pdf_path: str, max_pages: int = None) -> List[Dict]:
    """
    Extract data from PDF using PyMuPDF + OpenAI Vision
    
    Args:
        pdf_path: Path to PDF file
        max_pages: Max pages to process (None = all pages)
    
    Returns:
        List of extracted data per page
    """
    
    # ✅ CHANGE: Allow unlimited pages if max_pages is None
    if max_pages is None:
        max_pages = 999  # Process all pages
    
    print(f"📄 Converting PDF to images: {pdf_path}")
    
    try:
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(pdf_path)
        total_pages = min(len(pdf_document), max_pages)
        
        print(f"✅ Found {total_pages} page(s) - Processing ALL pages")
        
        all_extracted_data = []
        
        for page_num in range(total_pages):
            print(f"\n🔍 Processing page {page_num + 1}/{total_pages}...")
            
            try:
                # Get page
                page = pdf_document[page_num]
                
                # Convert page to image at high DPI
                zoom = settings.IMAGE_ZOOM
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Encode to base64
                base64_image = encode_image(img)
                
                if not base64_image:
                    print(f"❌ Page {page_num + 1}: Failed to encode")
                    continue
                
                # IMPROVED OCR PROMPT - Extract ALL fields
                ocr_prompt = """Extract ALL form fields from this visa application form image.

IMPORTANT: Extract EVERY field label you see, even if empty.

Look for:
- Field labels ending with "–" or ":"
- Questions that need answers
- Sections with bullet points
- Input fields (text boxes, date fields, checkboxes)

For EACH field found, extract:
1. The complete field label/question
2. The field type (text/date/email/select)

Return JSON format:
{
  "fields": [
    {"label": "Full Name", "type": "text"},
    {"label": "Date of Birth", "type": "date"},
    {"label": "Email Address", "type": "email"}
  ]
}

Extract EVERY field you see. Don't skip any!"""
                
                content = await call_openai_with_image(
                    text_prompt=ocr_prompt,
                    base64_image=base64_image,
                    temperature=0.1,
                    max_tokens=settings.OCR_MAX_TOKENS
                )
                
                # Parse JSON response
                try:
                    # Remove markdown code blocks
                    if "```json" in content:
                        json_str = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        json_str = content.split("```")[1].split("```")[0].strip()
                    else:
                        json_str = content
                    
                    page_data = json.loads(json_str)
                    page_data['page_number'] = page_num + 1
                    all_extracted_data.append(page_data)
                    
                    field_count = len(page_data.get('fields', []))
                    print(f"✅ Page {page_num + 1} extracted: {field_count} fields")
                
                except json.JSONDecodeError as e:
                    print(f"⚠️  Page {page_num + 1}: JSON parse failed - {e}")
                    # Try to extract fields manually from text
                    fields = extract_fields_from_text(content)
                    all_extracted_data.append({
                        'page_number': page_num + 1,
                        'fields': fields,
                        'raw_response': content[:500]
                    })
            
            except Exception as e:
                print(f"❌ Page {page_num + 1}: Error - {e}")
                all_extracted_data.append({
                    'page_number': page_num + 1,
                    'error': str(e),
                    'fields': []
                })
        
        pdf_document.close()
        
        print(f"📊 Total pages processed: {len(all_extracted_data)}")
        return all_extracted_data
    
    except Exception as e:
        print(f"❌ PDF processing failed: {e}")
        import traceback
        traceback.print_exc()
        return []


def extract_fields_from_text(text: str) -> List[Dict]:
    """
    Fallback: Extract fields from raw text if JSON parsing fails
    """
    fields = []
    
    # Pattern: Lines ending with "–" or ":"
    patterns = [
        r'^(.+?)\s*–\s*$',
        r'^(.+?)\s*:\s*$',
        r'^\•\s*(.+?)\s*–\s*$'
    ]
    
    lines = text.split('\n')
    field_id = 1
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 3:
            continue
        
        for pattern in patterns:
            match = re.match(pattern, line, re.MULTILINE)
            if match:
                label = match.group(1).strip()
                
                # Determine type
                field_type = "text"
                label_lower = label.lower()
                
                if any(kw in label_lower for kw in ['date', 'birth', 'expiry', 'issued']):
                    field_type = "date"
                elif any(kw in label_lower for kw in ['email', 'e-mail']):
                    field_type = "email"
                elif any(kw in label_lower for kw in ['yes/no', 'yes or no']):
                    field_type = "select"
                
                fields.append({
                    "label": label,
                    "type": field_type
                })
                break
    
    return fields


def merge_all_fields(pages_data: List[Dict]) -> List[Dict]:
    """
    Merge fields from all pages into a single list
    Remove duplicates and clean up
    ✅ NO LIMIT - Extract all unique fields
    """
    all_fields = []
    seen_labels = set()
    field_id = 1
    
    for page in pages_data:
        if 'error' in page:
            continue
        
        page_fields = page.get('fields', [])
        
        for field in page_fields:
            label = field.get('label', '').strip()
            
            if not label or len(label) < 2:
                continue
            
            # Clean label
            label = re.sub(r'^\d+\.?\s*', '', label)  # Remove numbering
            label = re.sub(r'\s*–\s*$', '', label)    # Remove trailing dash
            label = re.sub(r'\s*:\s*$', '', label)    # Remove trailing colon
            label = label.strip()
            
            # Skip if already seen (case insensitive)
            label_lower = label.lower()
            if label_lower in seen_labels:
                continue
            
            seen_labels.add(label_lower)
            
            # Determine field type
            field_type = field.get('type', 'text')
            
            all_fields.append({
                "id": str(field_id),
                "label": label,
                "type": field_type
            })
            field_id += 1
    
    print(f"📋 Total unique fields extracted: {len(all_fields)}")
    return all_fields


async def analyze_form_with_vision(pdf_path: str, filename: str) -> Dict:
    """
    Complete form analysis: OCR + metadata extraction
    ✅ UNLIMITED FIELDS - No restrictions!
    """
    
    print(f"🔍 Analyzing form: {filename}")
    
    # Extract all pages (no page limit)
    pages_data = await extract_data_from_pdf(pdf_path, max_pages=None)
    
    if not pages_data:
        raise Exception("Failed to extract any data from PDF")
    
    # Merge all fields from all pages (no field limit)
    all_fields = merge_all_fields(pages_data)
    
    # If too few fields extracted, try alternative extraction
    if len(all_fields) < 5:
        print("⚠️  Too few fields extracted, trying alternative method...")
        all_fields = await extract_fields_with_ai_full_context(pages_data)
    
    print(f"📊 Final field count: {len(all_fields)}")
    
    # ✅ REMOVED: No field limit anymore!
    # Before: if len(all_fields) > settings.MAX_FIELDS_PER_FORM:
    # Now: Accept ALL fields
    
    # Extract metadata with AI
    metadata = await extract_form_metadata(pages_data, filename)
    
    # Build final form data
    form_data = {
        "title": metadata.get("title", filename.replace('.pdf', '').title()),
        "visa_type": metadata.get("visa_type", "General"),
        "purpose_keywords": metadata.get("purpose_keywords", ["visa"]),
        "country": metadata.get("country", "Unknown"),
        "fields": all_fields,  # ✅ ALL fields, no limit
        "pages_data": pages_data,
        "total_pages": len(pages_data),
        "extraction_method": "pymupdf_vision_ocr_unlimited",
        "total_fields_extracted": len(all_fields)
    }
    
    print(f"✅ Form analysis complete!")
    print(f"   Title: {form_data['title']}")
    print(f"   Country: {form_data['country']}")
    print(f"   Visa Type: {form_data['visa_type']}")
    print(f"   Fields: {len(all_fields)} (UNLIMITED)")
    
    return form_data


async def extract_fields_with_ai_full_context(pages_data: List[Dict]) -> List[Dict]:
    """
    Use AI to extract fields from full form context
    Fallback method if initial extraction fails
    ✅ NO LIMIT on extracted fields
    """
    
    # Collect all text
    all_text = []
    for page in pages_data:
        if 'raw_response' in page:
            all_text.append(page['raw_response'])
    
    # ✅ CHANGE: Increased text limit for more context
    combined_text = "\n".join(all_text[:5000])  # 5000 chars instead of 3000
    
    fields_prompt = f"""Extract ALL form fields from this visa application form.

Form content:
{combined_text}

Extract EVERY field that needs to be filled. Look for:
- Labels ending with "–" or ":"
- Questions
- Input fields

Return JSON array of fields:
{{
  "fields": [
    {{"label": "Given Name", "type": "text"}},
    {{"label": "Date of Birth", "type": "date"}},
    {{"label": "Email Address", "type": "email"}}
  ]
}}

Extract as many fields as you can find. Return ONLY JSON:"""
    
    try:
        response = await call_openai_chat(
            messages=[{"role": "user", "content": fields_prompt}],
            system_prompt="Extract all form fields. Return only JSON.",
            temperature=0.5,
            max_tokens=4000  # ✅ Increased from 2000 to 4000
        )
        
        # Parse response
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response)
        fields = result.get('fields', [])
        
        # Add IDs
        for i, field in enumerate(fields):
            field['id'] = str(i + 1)
        
        print(f"✅ AI fallback extracted {len(fields)} fields")
        return fields
    
    except Exception as e:
        print(f"❌ AI fallback failed: {e}")
        return []


async def extract_form_metadata(pages_data: List[Dict], filename: str) -> Dict:
    """
    Extract form metadata (title, visa type, country) using AI
    """
    
    # Get first page text for metadata
    first_page_text = ""
    if pages_data and len(pages_data) > 0:
        first_page = pages_data[0]
        if 'raw_response' in first_page:
            first_page_text = first_page['raw_response'][:1000]
    
    metadata_prompt = f"""Extract metadata from this visa form.

Filename: {filename}
Content: {first_page_text}

Return JSON:
{{
  "title": "Form title",
  "visa_type": "Tourist/Student/Work/Business/Family",
  "country": "Country name",
  "purpose_keywords": ["keyword1", "keyword2"]
}}

Return ONLY JSON:"""
    
    try:
        response = await call_openai_chat(
            messages=[{"role": "user", "content": metadata_prompt}],
            system_prompt="Extract form metadata. Return only JSON.",
            temperature=0.5,
            max_tokens=300
        )
        
        # Parse
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        metadata = json.loads(response)
        return metadata
    
    except Exception as e:
        print(f"⚠️  Metadata extraction failed: {e}")
        return {
            "title": filename.replace('.pdf', '').replace('_', ' ').title(),
            "visa_type": "General",
            "purpose_keywords": ["visa"],
            "country": "Unknown"
        }
