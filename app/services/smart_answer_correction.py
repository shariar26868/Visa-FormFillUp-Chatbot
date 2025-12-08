"""
Smart Answer Correction Service
✅ Detects when user wants to fix a previous answer
✅ Works naturally - no question numbers needed
"""

from typing import Dict, Optional
from app.core.storage import load_conversation, get_form_by_id
from app.services.ai_service import call_openai_chat
import json


async def detect_answer_correction(session_id: str, message: str, data: dict) -> Dict:
    """
    Detect if user is correcting a previous answer
    
    Returns:
        {
            "is_correction": bool,
            "field": Dict,  # The field being corrected
            "new_answer": str,  # The new answer
            "confidence": float
        }
    """
    
    # Get previous answers
    answers = data.get("answers", {})
    
    if not answers:
        return {"is_correction": False}
    
    # Get form to know field labels
    form_id = data.get("matched_form_id")
    if not form_id:
        return {"is_correction": False}
    
    form = await get_form_by_id(form_id)
    if not form:
        return {"is_correction": False}
    
    fields = form.get("fields", [])
    
    # Quick keyword check first
    correction_keywords = [
        "sorry", "wait", "actually", "correction", "mistake", 
        "wrong", "change", "update", "fix", "meant to say",
        "i mean", "should be", "correct answer", "my bad",
        "oops", "no wait", "i said", "earlier i"
    ]
    
    message_lower = message.lower()
    has_correction_keyword = any(kw in message_lower for kw in correction_keywords)
    
    if not has_correction_keyword:
        # Check if message references a previous field
        for field in fields:
            field_label_lower = field.get("label", "").lower()
            # Check for field label mentions
            if len(field_label_lower) > 3 and field_label_lower in message_lower:
                has_correction_keyword = True
                break
    
    if not has_correction_keyword:
        return {"is_correction": False}
    
    # Use AI to detect correction with context
    return await ai_detect_correction(message, answers, fields, data)


async def ai_detect_correction(message: str, answers: Dict, fields: list, data: dict) -> Dict:
    """
    Use AI to intelligently detect answer correction
    """
    
    # Build context of previous answers
    answered_fields = []
    for field in fields:
        field_id = field.get("id")
        if field_id in answers:
            answered_fields.append({
                "field_id": field_id,
                "label": field.get("label"),
                "type": field.get("type"),
                "current_answer": answers[field_id].get("answer")
            })
    
    if not answered_fields:
        return {"is_correction": False}
    
    # Get recent conversation for context
    history = data.get("history", [])
    recent_messages = []
    for msg in history[-6:]:  # Last 6 messages
        if msg.get("role") == "user":
            recent_messages.append(msg.get("content"))
    
    context_text = "\n".join(recent_messages[-3:]) if recent_messages else ""
    
    prompt = f"""Analyze if the user wants to CORRECT a previous answer.

USER'S NEW MESSAGE:
"{message}"

RECENT CONVERSATION CONTEXT:
{context_text}

PREVIOUSLY ANSWERED FIELDS:
{json.dumps(answered_fields, indent=2)}

DETECTION RULES:

1. **IS CORRECTION** if user:
   - Says "sorry", "wait", "actually", "wrong", "mistake", etc.
   - References a specific field they answered before
   - Provides NEW information for a field they already filled
   - Examples:
     * "sorry my address is actually 123 Main St" → CORRECTION for address field
     * "wait, I meant to say my phone is +1234567890" → CORRECTION for phone
     * "my date of birth is wrong, it's 1990-01-15" → CORRECTION for DOB
     * "actually I'm from Canada, not USA" → CORRECTION for country

2. **NOT CORRECTION** if:
   - Just answering current question normally
   - Asking for help
   - Making casual conversation
   - Examples:
     * "I was born in 1990" → Just answering current question
     * "help me with this" → Not correction
     * "what do I need?" → Not correction

RESPONSE FORMAT (JSON only):
{{
  "is_correction": true or false,
  "field_id": "field_id_being_corrected" or null,
  "field_label": "Field label" or null,
  "new_answer": "extracted new answer" or null,
  "confidence": 0.0 to 1.0,
  "reasoning": "Brief explanation"
}}

IMPORTANT:
- Be confident in detection (confidence > 0.7)
- Extract the NEW answer value from the message
- Match field by CONTENT, not just name mention
- If multiple fields could match, choose the most relevant one

Return ONLY valid JSON:"""
    
    try:
        response = await call_openai_chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are an expert at understanding user intent in form corrections. Be precise and confident. Return only JSON.",
            temperature=0.2,
            max_tokens=400
        )
        
        # Parse JSON
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response)
        
        is_correction = result.get("is_correction", False)
        confidence = result.get("confidence", 0.0)
        
        print(f"\n🔍 Correction Detection:")
        print(f"   Is Correction: {is_correction}")
        print(f"   Confidence: {confidence}")
        print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
        
        # Only consider it a correction if high confidence
        if not is_correction or confidence < 0.7:
            return {"is_correction": False}
        
        field_id = result.get("field_id")
        new_answer = result.get("new_answer")
        
        if not field_id or not new_answer:
            return {"is_correction": False}
        
        # Find the field object
        target_field = None
        for field in fields:
            if field.get("id") == field_id:
                target_field = field
                break
        
        if not target_field:
            return {"is_correction": False}
        
        print(f"   ✅ Detected correction for: {target_field.get('label')}")
        print(f"   New answer: {new_answer}")
        
        return {
            "is_correction": True,
            "field": target_field,
            "new_answer": new_answer,
            "confidence": confidence
        }
    
    except Exception as e:
        print(f"❌ Correction detection error: {e}")
        return {"is_correction": False}


async def get_correction_suggestions(session_id: str, message: str) -> Optional[Dict]:
    """
    Suggest which field the user might want to correct
    (Optional helper function for ambiguous cases)
    """
    data = await load_conversation(session_id)
    answers = data.get("answers", {})
    
    if not answers:
        return None
    
    form_id = data.get("matched_form_id")
    form = await get_form_by_id(form_id)
    
    if not form:
        return None
    
    fields = form.get("fields", [])
    
    # Build list of answerable fields
    correction_options = []
    for field in fields:
        field_id = field.get("id")
        if field_id in answers:
            correction_options.append({
                "field_id": field_id,
                "label": field.get("label"),
                "current_answer": answers[field_id].get("answer")
            })
    
    return {
        "options": correction_options,
        "message": message
    }