# """
# Question Generation & Help System
# ✅ FIXED: Added field progress counter (1/50, 2/50...)
# """
# from typing import Dict
# from app.services.ai_service import call_openai_chat


# async def generate_question_for_field(field: Dict, idx: int, total: int) -> str:
#     """
#     Generate friendly question for form field
#     ✅ NOW INCLUDES PROGRESS: Question 1/50, 2/50, etc.
#     """
#     label = field.get("label", "")
#     field_type = field.get("type", "text")
    
#     # ✅ Add field counter prefix
#     counter_prefix = f"📝 Question {idx + 1}/{total}"
    
#     prompt = f"""Generate a friendly question for this form field:
# Field: {label}
# Type: {field_type}

# Make it conversational and clear. Add format hints if needed.
# Keep it under 2-3 sentences.
# DO NOT include any numbering or progress indicators."""
    
#     try:
#         question = await call_openai_chat(
#             messages=[{"role": "user", "content": prompt}],
#             system_prompt="You are a helpful form assistant. Be concise and friendly.",
#             temperature=0.8,
#             max_tokens=150
#         )
#         # ✅ Return with counter prefix
#         return f"{counter_prefix}\n{question.strip()}"
#     except Exception as e:
#         print(f"Question generation failed: {e}")
#         return f"{counter_prefix}\n{label}"


# def is_help_request(message: str) -> bool:
#     """
#     Check if user is asking for help
#     ✅ IMPROVED: More precise detection
#     """
#     message_lower = message.lower().strip()
    
#     # ✅ Ignore common uncertainty phrases during consultation
#     # These should NOT trigger help mode during form filling
#     consultation_phrases = [
#         "i'm not sure",
#         "im not sure", 
#         "not sure yet",
#         "don't know yet",
#         "dont know yet",
#         "maybe",
#         "thinking about"
#     ]
    
#     # Check if it's just consultation uncertainty
#     for phrase in consultation_phrases:
#         if phrase in message_lower and len(message_lower.split()) < 10:
#             return False  # Not asking for help, just uncertain
    
#     # ✅ MUST be at START of message (user explicitly asking)
#     help_starters = [
#         "help",
#         "i need help",
#         "can you help",
#         "how do i",
#         "how should i",
#         "how to",
#         "what do i",
#         "what should i",
#         "i don't know how",
#         "i dont know how",
#         "confused",
#         "example",
#         "give me an example",
#         "show me"
#     ]
    
#     # Check if message STARTS with help keywords
#     for starter in help_starters:
#         if message_lower.startswith(starter):
#             return True
    
#     # ✅ Check for short help questions (< 15 words)
#     words = message_lower.split()
#     if len(words) <= 15:
#         help_keywords = ["help me", "how should", "what should", "confused", "example", "show me"]
#         if any(kw in message_lower for kw in help_keywords):
#             return True
    
#     # ✅ If message is long (> 15 words), it's likely an answer, not help
#     return False


# async def generate_help_for_field(field: Dict, user_question: str) -> str:
#     """
#     Generate contextual help for a form field
#     ✅ IMPROVED: Better prompting and token limit
#     """
#     label = field.get("label", "")
#     field_type = field.get("type", "text")
#     description = field.get("description", "")
    
#     prompt = f"""User needs help with this form field:

# Field Name: {label}
# Field Type: {field_type}
# Description: {description}
# User Question: "{user_question}"

# Provide clear, helpful guidance in 3-4 sentences:
# 1. Explain what this field expects
# 2. Give a specific example format
# 3. Mention any important tips

# Be concise and friendly."""
    
#     try:
#         help_text = await call_openai_chat(
#             messages=[{"role": "user", "content": prompt}],
#             system_prompt="You are a helpful form assistant. Provide clear, concise guidance with examples.",
#             temperature=0.7,
#             max_tokens=250
#         )
#         return help_text.strip()
#     except Exception as e:
#         print(f"Help generation failed: {e}")
#         # Fallback help message
#         return f"Please provide your {label}. Expected format: {field_type}. For example, enter the complete information clearly."





"""
Question Generation & Help System
FIXED: Added field progress counter (1/50, 2/50...)
"""
from typing import Dict
from app.services.ai_service import call_openai_chat


async def generate_question_for_field(field: Dict, idx: int, total: int) -> str:
    """
    Generate friendly question for form field
    NOW INCLUDES PROGRESS: Question 1/50, 2/50, etc.
    """
    label = field.get("label", "")
    field_type = field.get("type", "text")
    
    # Add field counter prefix
    counter_prefix = f"Question {idx + 1}/{total}"
    
    prompt = f"""Generate a friendly question for this form field:
Field: {label}
Type: {field_type}

Make it conversational and clear. Add format hints if needed.
Keep it under 2-3 sentences.
DO NOT include any numbering or progress indicators."""
    
    try:
        question = await call_openai_chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a helpful form assistant. Be concise and friendly.",
            temperature=0.8,
            max_tokens=150
        )
        # Return with counter prefix
        return f"{counter_prefix}: {question.strip()}"
    except Exception as e:
        print(f"Question generation failed: {e}")
        return f"{counter_prefix}: {label}"


def is_help_request(message: str) -> bool:
    """
    Check if user is asking for help
    IMPROVED: More precise detection
    """
    message_lower = message.lower().strip()
    
    # Ignore common uncertainty phrases during consultation
    # These should NOT trigger help mode during form filling
    consultation_phrases = [
        "i'm not sure",
        "im not sure", 
        "not sure yet",
        "don't know yet",
        "dont know yet",
        "maybe",
        "thinking about"
    ]
    
    # Check if it's just consultation uncertainty
    for phrase in consultation_phrases:
        if phrase in message_lower and len(message_lower.split()) < 10:
            return False  # Not asking for help, just uncertain
    
    # MUST be at START of message (user explicitly asking)
    help_starters = [
        "help",
        "i need help",
        "can you help",
        "how do i",
        "how should i",
        "how to",
        "what do i",
        "what should i",
        "i don't know how",
        "i dont know how",
        "confused",
        "example",
        "give me an example",
        "show me"
    ]
    
    # Check if message STARTS with help keywords
    for starter in help_starters:
        if message_lower.startswith(starter):
            return True
    
    # Check for short help questions (< 15 words)
    words = message_lower.split()
    if len(words) <= 15:
        help_keywords = ["help me", "how should", "what should", "confused", "example", "show me"]
        if any(kw in message_lower for kw in help_keywords):
            return True
    
    # If message is long (> 15 words), it's likely an answer, not help
    return False


async def generate_help_for_field(field: Dict, user_question: str) -> str:
    """
    Generate contextual help for a form field
    IMPROVED: Better prompting and token limit
    """
    label = field.get("label", "")
    field_type = field.get("type", "text")
    description = field.get("description", "")
    
    prompt = f"""User needs help with this form field:

Field Name: {label}
Field Type: {field_type}
Description: {description}
User Question: "{user_question}"

Provide clear, helpful guidance in 3-4 sentences:
1. Explain what this field expects
2. Give a specific example format
3. Mention any important tips

Be concise and friendly."""
    
    try:
        help_text = await call_openai_chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a helpful form assistant. Provide clear, concise guidance with examples.",
            temperature=0.7,
            max_tokens=250
        )
        return help_text.strip()
    except Exception as e:
        print(f"Help generation failed: {e}")
        # Fallback help message
        return f"Please provide your {label}. Expected format: {field_type}. For example, enter the complete information clearly."