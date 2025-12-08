"""
Question Generation & Help System
✅ IMPROVED: More natural, conversational questions
"""
from typing import Dict
from app.services.ai_service import call_openai_chat


async def generate_question_for_field(field: Dict, idx: int, total: int) -> str:
    """
    Generate natural, conversational question for form field
    Progress shown as: Question 1/50, 2/50, etc.
    """
    label = field.get("label", "")
    field_type = field.get("type", "text")
    
    counter_prefix = f"Question {idx + 1}/{total}"
    
    prompt = f"""Generate a natural, conversational question for this visa form field:

Field: {label}
Type: {field_type}

Requirements:
- Make it sound like a friend asking, not a robot
- Be clear and specific
- Add helpful format hints if needed (dates, emails, etc.)
- Keep it under 2 sentences
- Be warm and encouraging
- NO numbering or progress indicators in the question itself

Examples:
❌ Bad: "Please enter your full name"
✅ Good: "What's your full name as it appears on your passport?"

❌ Bad: "Provide date of birth"
✅ Good: "When were you born? (Please use DD/MM/YYYY format)"

❌ Bad: "Enter email"
✅ Good: "What's your email address?"

Generate a natural question:"""
    
    try:
        question = await call_openai_chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a friendly visa consultant. Ask questions naturally, like talking to a friend. Be warm and clear.",
            temperature=0.8,
            max_tokens=150
        )
        
        # Clean up the response
        question = question.strip()
        
        # Remove any accidental numbering
        import re
        question = re.sub(r'^\d+[\.\)]\s*', '', question)
        question = re.sub(r'^Question \d+[:/]\s*', '', question, flags=re.IGNORECASE)
        
        # Return with counter prefix
        return f"{counter_prefix}: {question}"
        
    except Exception as e:
        print(f"Question generation failed: {e}")
        # Fallback to simple format
        return f"{counter_prefix}: Could you tell me your {label.lower()}?"


def is_help_request(message: str) -> bool:
    """
    Detect if user is asking for help
    ✅ IMPROVED: More precise, avoids false positives during consultation
    """
    message_lower = message.lower().strip()
    
    # ============================================
    # STEP 1: Filter out consultation uncertainty
    # ============================================
    # These phrases indicate uncertainty during initial chat,
    # NOT help requests during form filling
    consultation_phrases = [
        "i'm not sure",
        "im not sure", 
        "not sure yet",
        "don't know yet",
        "dont know yet",
        "maybe",
        "thinking about",
        "possibly",
        "probably"
    ]
    
    # If message is just expressing uncertainty (short message)
    for phrase in consultation_phrases:
        if phrase in message_lower and len(message_lower.split()) < 10:
            return False  # Not asking for help, just uncertain
    
    # ============================================
    # STEP 2: Check for explicit help requests
    # ============================================
    # Must be at START of message or be a short question
    help_starters = [
        "help",
        "i need help",
        "can you help",
        "could you help",
        "help me",
        "how do i",
        "how should i",
        "how to",
        "what do i",
        "what should i",
        "i don't know how",
        "i dont know how",
        "i don't understand",
        "i dont understand",
        "confused",
        "example",
        "give me an example",
        "show me",
        "can you explain",
        "what does this mean",
        "i'm confused",
        "im confused"
    ]
    
    # Check if message STARTS with help keywords
    for starter in help_starters:
        if message_lower.startswith(starter):
            return True
    
    # ============================================
    # STEP 3: Check for short help questions
    # ============================================
    words = message_lower.split()
    
    # Short messages (< 15 words) with help keywords
    if len(words) <= 15:
        help_keywords = [
            "help me",
            "how should",
            "what should", 
            "confused",
            "example",
            "show me",
            "explain",
            "don't know",
            "dont know",
            "not sure how",
            "how do"
        ]
        
        if any(kw in message_lower for kw in help_keywords):
            return True
    
    # ============================================
    # STEP 4: Check for question marks with help words
    # ============================================
    if "?" in message and len(words) <= 12:
        question_help_words = ["how", "what", "help", "explain", "mean"]
        if any(word in message_lower for word in question_help_words):
            return True
    
    # If message is long (> 15 words) without clear help keywords,
    # it's likely an answer, not a help request
    return False


async def generate_help_for_field(field: Dict, user_question: str) -> str:
    """
    Generate helpful, natural guidance for a form field
    ✅ IMPROVED: More conversational, like explaining to a friend
    """
    label = field.get("label", "")
    field_type = field.get("type", "text")
    description = field.get("description", "")
    
    prompt = f"""The user needs help with this visa form field:

Field Name: {label}
Field Type: {field_type}
Description: {description}
User's Question: "{user_question}"

Provide warm, helpful guidance like you're helping a friend:

1. Explain what this field expects (1 sentence)
2. Give a specific, realistic example
3. Add any important tips or common mistakes to avoid

Requirements:
- Be conversational and warm
- Use "you" and "your" (not "the applicant")
- Keep it concise (3-4 sentences max)
- Be encouraging
- Give REAL examples (not generic ones)

Example of good help:
"This is asking for your complete home address where you currently live. For example, if you live in an apartment, write something like '123 Main Street, Apt 4B, New York, NY 10001, USA'. Make sure to include your apartment/unit number if you have one!"

Generate helpful guidance:"""
    
    try:
        help_text = await call_openai_chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a warm, patient visa consultant helping a friend. Be clear, encouraging, and use real examples. Keep it conversational.",
            temperature=0.7,
            max_tokens=300
        )
        
        return help_text.strip()
        
    except Exception as e:
        print(f"Help generation failed: {e}")
        
        # Better fallback messages based on field type
        if field_type == "date":
            return f"For {label}, please provide the date in DD/MM/YYYY format. For example, if the date is January 15, 2024, write it as '15/01/2024'. Make sure to use the correct format!"
        
        elif field_type == "email":
            return f"For {label}, enter your complete email address. For example: 'john.smith@email.com'. Make sure there are no spaces and you include the @ symbol!"
        
        elif field_type == "phone":
            return f"For {label}, provide your phone number with country code if possible. For example: '+1-555-123-4567' or '01712345678'. Include the area code!"
        
        else:
            return f"For {label}, please provide the complete information as clearly as possible. If you have any official documents handy, you can reference those to make sure you're entering the correct details. Take your time!"


async def generate_progress_message(current: int, total: int) -> str:
    """
    Generate encouraging progress messages
    ✅ NEW: Add motivation during form filling
    """
    percentage = (current / total * 100) if total > 0 else 0
    
    if percentage < 25:
        messages = [
            "Great start! You're doing well.",
            "Nice! Keep going.",
            "Perfect! Let's continue."
        ]
    elif percentage < 50:
        messages = [
            "You're making good progress!",
            "Halfway there! You're doing great.",
            "Excellent! Almost halfway done."
        ]
    elif percentage < 75:
        messages = [
            "More than halfway! You're doing fantastic.",
            "Great progress! Keep it up.",
            "You're almost there! Doing great."
        ]
    else:
        messages = [
            "Almost done! Just a few more questions.",
            "You're nearly finished! Great job.",
            "Final stretch! You're doing amazing."
        ]
    
    import random
    return random.choice(messages)