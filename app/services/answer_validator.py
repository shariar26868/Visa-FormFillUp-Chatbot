"""
Answer Validation Service
✅ IMPROVED: Hybrid validation (Rules + AI)
"""
from typing import Tuple, Dict
from datetime import datetime
import re
from app.services.ai_service import call_openai_chat


async def validate_answer(field: Dict, answer: str) -> Tuple[bool, str]:
    """
    Validate user's answer for a form field
    
    Returns:
        Tuple[bool, str]: (is_valid, feedback_message)
    """
    label = field.get("label", "")
    field_type = field.get("type", "text")
    description = field.get("description", "")
    
    # ✅ Quick validation: Check if answer is not empty
    if not answer or len(answer.strip()) < 2:
        return False, f"Please provide a valid {label}. The answer seems too short."
    
    # ✅ RULE-BASED VALIDATION for specific field types
    # This runs BEFORE AI validation for accuracy
    
    # DATE fields - use rule-based validation
    if field_type.lower() == "date" or any(word in label.lower() for word in ["date", "birth", "issue", "expiry"]):
        return validate_date_field(answer, label)
    
    # EMAIL fields
    if field_type.lower() == "email" or "email" in label.lower():
        return validate_email_field(answer)
    
    # PHONE fields
    if field_type.lower() == "phone" or "phone" in label.lower():
        return validate_phone_field(answer)
    
    # NUMBER fields
    if field_type.lower() == "number":
        return validate_number_field(answer, label)
    
    # ✅ For other fields, use AI validation
    return await validate_with_ai(field, answer)


# ========== RULE-BASED VALIDATORS ==========

def validate_date_field(answer: str, field_label: str) -> Tuple[bool, str]:
    """
    Validate date fields with proper format checking
    """
    answer = answer.strip()
    
    # Try multiple date formats
    formats_to_try = [
        ("%d/%m/%Y", "DD/MM/YYYY"),  # 12/09/2024 → Dec 9, 2024
        ("%m/%d/%Y", "MM/DD/YYYY"),  # 09/12/2024 → Sep 12, 2024
        ("%Y-%m-%d", "YYYY-MM-DD"),  # 2024-09-12
        ("%d-%m-%Y", "DD-MM-YYYY"),  # 12-09-2024
    ]
    
    parsed_date = None
    used_format = None
    
    for fmt, fmt_name in formats_to_try:
        try:
            parsed_date = datetime.strptime(answer, fmt)
            used_format = fmt_name
            break
        except ValueError:
            continue
    
    if not parsed_date:
        return False, "Please provide a valid date format (e.g., 12/09/2024 or 2024-09-12)"
    
    now = datetime.now()
    field_lower = field_label.lower()
    
    # ✅ Context-aware validation
    
    # Birth dates - must be in the past, reasonable age
    if "birth" in field_lower:
        if parsed_date > now:
            return False, "Date of birth cannot be in the future."
        
        age_years = (now - parsed_date).days / 365.25
        if age_years > 120:
            return False, "Please check the birth date - it seems too far in the past."
        if age_years < 0:
            return False, "Date of birth must be in the past."
        
        return True, ""
    
    # Issue/Expiry dates - must be in reasonable range
    if "issue" in field_lower or "issued" in field_lower:
        if parsed_date > now:
            return False, "Date of issue cannot be in the future. Please provide a past date."
        
        years_ago = (now - parsed_date).days / 365.25
        if years_ago > 50:
            return False, "Issue date seems too far in the past. Please verify."
        
        return True, ""
    
    if "expiry" in field_lower or "expire" in field_lower:
        # Expiry can be in future
        if parsed_date < now:
            return False, "Expiry date should be in the future."
        
        years_future = (parsed_date - now).days / 365.25
        if years_future > 20:
            return False, "Expiry date seems too far in the future."
        
        return True, ""
    
    # Travel dates - can be in future
    if any(word in field_lower for word in ["travel", "departure", "arrival", "planned"]):
        years_future = (parsed_date - now).days / 365.25
        if years_future > 2:
            return False, "Travel date seems too far in the future (max 2 years)."
        
        # Allow up to 1 year in the past for travel history
        years_past = (now - parsed_date).days / 365.25
        if years_past > 1:
            return False, "Travel date seems too far in the past."
        
        return True, ""
    
    # Default: reasonable range check
    min_date = datetime(now.year - 100, 1, 1)
    max_date = datetime(now.year + 10, 12, 31)
    
    if parsed_date < min_date:
        return False, "Date seems too far in the past."
    if parsed_date > max_date:
        return False, "Date seems too far in the future."
    
    return True, ""


def validate_email_field(answer: str) -> Tuple[bool, str]:
    """Validate email format"""
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    if not re.match(email_pattern, answer.strip()):
        return False, "Please provide a valid email address (e.g., name@example.com)"
    return True, ""


def validate_phone_field(answer: str) -> Tuple[bool, str]:
    """Validate phone number"""
    # Remove spaces, hyphens, parentheses, plus sign
    clean_phone = re.sub(r'[\s\-\(\)\+]', '', answer)
    
    if not clean_phone.isdigit():
        return False, "Phone number should contain only digits (with optional +, -, spaces)"
    
    if len(clean_phone) < 10:
        return False, "Phone number should be at least 10 digits"
    
    if len(clean_phone) > 15:
        return False, "Phone number seems too long"
    
    return True, ""


def validate_number_field(answer: str, field_label: str) -> Tuple[bool, str]:
    """Validate numeric fields"""
    try:
        num = float(answer.strip())
        
        # Check for reasonable ranges
        if "age" in field_label.lower():
            if num < 0 or num > 120:
                return False, "Please provide a valid age (0-120)"
        
        return True, ""
    except ValueError:
        return False, f"Please provide a valid number for {field_label}"


# ========== AI-BASED VALIDATOR (Fallback) ==========

async def validate_with_ai(field: Dict, answer: str) -> Tuple[bool, str]:
    """
    Use AI validation for complex or text-based fields
    """
    label = field.get("label", "")
    field_type = field.get("type", "text")
    description = field.get("description", "")
    
    prompt = f"""Validate this form answer:

Field Name: {label}
Field Type: {field_type}
Description: {description}
User's Answer: "{answer}"

Check if the answer is:
1. Complete and reasonable
2. In appropriate format
3. Not obviously invalid

Return JSON ONLY:
{{
  "valid": true or false,
  "message": "Brief feedback (1-2 sentences)"
}}

Be lenient - accept reasonable answers."""
    
    try:
        response = await call_openai_chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a form validator. Be helpful but not overly strict. Return only JSON.",
            temperature=0.3,
            max_tokens=200
        )
        
        # Parse JSON response
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        import json
        result = json.loads(response)
        
        is_valid = result.get("valid", True)
        message = result.get("message", "Thank you!")
        
        if is_valid:
            if not message or message == "Thank you!":
                message = "Perfect! Got it. ✅"
        else:
            if not message.startswith("Please"):
                message = f"Hmm, {message}"
        
        return is_valid, message
    
    except Exception as e:
        print(f"AI validation error: {e}")
        # Default to accepting answer if AI fails
        return True, "Got it! Moving forward. ✅"