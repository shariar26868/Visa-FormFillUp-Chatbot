"""
Chat API - Professional Consultation Flow
IMPROVED: Warm greetings, 5-6 questions, better confirmations
"""

import uuid
from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.core.config import settings
from app.core.storage import (
    load_conversation,
    save_conversation,
    get_form_by_id
)
from app.services.ai_service import call_openai_chat
from app.services.form_matcher import match_form_from_conversation
from app.services.question_generator import (
    generate_question_for_field,
    generate_help_for_field,
    is_help_request
)
from app.services.answer_validator import validate_answer
from app.services.conversation_manager import ConversationManager

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - Professional consultation flow
    """
    
    # Initialize or load session
    session_id = request.session_id or str(uuid.uuid4())
    data = await load_conversation(session_id)
    
    if not data.get("history"):
        data["history"] = []
        data["state"] = settings.STATE_CHATTING
    
    current_state = data.get("state", settings.STATE_CHATTING)
    history = data["history"]
    
    print(f"\n{'='*60}")
    print(f"Message: {request.message[:80]}...")
    print(f"Current State: {current_state}")
    print(f"History Length: {len(history)}")
    print(f"{'='*60}\n")
    
    # STATE: COMPLETED
    if current_state == settings.STATE_COMPLETED:
        return await handle_completed_state(session_id, data, request.message)
    
    # STATE: FILLING_FORM
    if current_state == settings.STATE_FILLING_FORM:
        return await handle_filling_form_state(session_id, data, request.message)
    
    # STATE: AWAITING_CONFIRMATION
    if current_state == settings.STATE_AWAITING_CONFIRMATION:
        return await handle_awaiting_confirmation_state(session_id, data, request.message)
    
    # STATE: FORM_MATCHED
    if current_state == settings.STATE_FORM_MATCHED:
        return await handle_form_matched_state(session_id, data, request.message)
    
    # STATE: CHATTING
    return await handle_chatting_state(session_id, data, request.message, history)


# ========== STATE HANDLERS ==========

async def handle_completed_state(session_id: str, data: dict, message: str):
    """Handle conversation when form is completed"""
    form_id = data.get("matched_form_id")
    form = await get_form_by_id(form_id)
    
    # Check if user wants a new form
    new_form_words = ["another", "new", "different", "next", "more"]
    if any(word in message.lower() for word in new_form_words):
        data["state"] = settings.STATE_CHATTING
        data["matched_form_id"] = None
        data["current_field_index"] = 0
        data["history"] = []
        await save_conversation(session_id, data)
        
        return ChatResponse(
            session_id=session_id,
            message="Great! I'm ready to help with another visa application. Which country would you like to apply for?",
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # Show completion summary
    answers_count = len(data.get("answers", {}))
    total_fields = len(form.get("fields", []))
    
    summary_msg = f"Form Completed Successfully! Form: {form['title']}, Visa Type: {form['visa_type']}, Completed: {answers_count}/{total_fields} fields. View full summary: /api/summary/{session_id}. Would you like to fill another form?"
    
    return ChatResponse(
        session_id=session_id,
        message=summary_msg,
        state=settings.STATE_COMPLETED,
        is_form_ready=False,
        matched_form={
            "form_id": form["form_id"],
            "title": form["title"],
            "visa_type": form["visa_type"],
            "country": form.get("country", "N/A")
        }
    )


async def handle_filling_form_state(session_id: str, data: dict, message: str):
    """Handle form filling with help support"""
    try:
        # Get current field
        field, field_index, total_fields = await ConversationManager.get_current_field(session_id)
        
        print(f"Current Field: {field['label']} ({field_index + 1}/{total_fields})")
        print(f"User Message: {message[:100]}...")
        
        # Check if asking for help
        if is_help_request(message):
            print(f"User asking for help on field: {field['label']}")
            
            help_text = await generate_help_for_field(field, message)
            
            help_response = f"Let me help you with this field: {help_text} Once you understand, just type your answer and I'll save it!"
            
            return ChatResponse(
                session_id=session_id,
                message=help_response,
                state=settings.STATE_FILLING_FORM,
                is_form_ready=False
            )
        
        # Process as answer
        print(f"Processing as answer...")
        
        # Validate answer
        is_valid, validation_msg = await validate_answer(field, message)
        
        if not is_valid:
            invalid_response = f"{validation_msg} Please provide a valid answer. Need help? Just type 'help'"
            
            return ChatResponse(
                session_id=session_id,
                message=invalid_response,
                state=settings.STATE_FILLING_FORM,
                is_form_ready=False
            )
        
        # Save answer and move to next
        has_more_fields = await ConversationManager.save_answer(session_id, message)
        
        if not has_more_fields:
            # Form completed!
            await ConversationManager.transition_to_completed(session_id)
            
            form_id = data.get("matched_form_id")
            form = await get_form_by_id(form_id)
            
            completion_msg = f"Congratulations! Form Completed! You've successfully filled all {total_fields} fields of: {form['title']} ({form['visa_type']}). View Summary: /api/summary/{session_id}. Would you like to fill another visa form?"
            
            return ChatResponse(
                session_id=session_id,
                message=completion_msg,
                state=settings.STATE_COMPLETED,
                is_form_ready=False,
                matched_form=form
            )
        
        # Get next field
        next_field, next_idx, total = await ConversationManager.get_current_field(session_id)
        next_question = await generate_question_for_field(next_field, next_idx, total)
        
        response_msg = f"Got it! {next_question} Need help? Just type 'help'"
        
        return ChatResponse(
            session_id=session_id,
            message=response_msg,
            state=settings.STATE_FILLING_FORM,
            is_form_ready=False
        )
    
    except Exception as e:
        print(f"Error in filling form: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


async def handle_awaiting_confirmation_state(session_id: str, data: dict, message: str):
    """Handle multiple form choices"""
    message_lower = message.lower()
    recommended_form = data.get("recommended_form")
    
    if not recommended_form:
        data["state"] = settings.STATE_CHATTING
        await save_conversation(session_id, data)
        
        return ChatResponse(
            session_id=session_id,
            message="Let's start fresh. Which country's visa do you need?",
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # Check confirmation
    yes_words = ["yes", "ok", "okay", "sure", "start", "continue", "proceed", "correct"]
    no_words = ["no", "not", "don't", "dont", "cancel", "stop"]
    
    if any(word in message_lower for word in yes_words):
        await ConversationManager.transition_to_form_matched(
            session_id,
            recommended_form["form_id"]
        )
        
        form = await get_form_by_id(recommended_form["form_id"])
        
        ready_msg = f"Perfect! Let's proceed with: {form['title']}, Visa Type: {form['visa_type']}, Total Fields: {len(form.get('fields', []))}. May we start filling the form now? Say 'Yes, let's begin'"
        
        return ChatResponse(
            session_id=session_id,
            message=ready_msg,
            state=settings.STATE_FORM_MATCHED,
            is_form_ready=True,
            matched_form={
                "form_id": form["form_id"],
                "title": form["title"],
                "visa_type": form["visa_type"],
                "country": form.get("country", "N/A"),
                "total_fields": len(form.get("fields", []))
            }
        )
    
    if any(word in message_lower for word in no_words):
        data["state"] = settings.STATE_CHATTING
        data["recommended_form"] = None
        data["history"] = []
        await save_conversation(session_id, data)
        
        return ChatResponse(
            session_id=session_id,
            message="No problem! I'm here to help. Which country and visa type would you prefer?",
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # Unclear response
    data["state"] = settings.STATE_CHATTING
    data["recommended_form"] = None
    await save_conversation(session_id, data)
    
    return ChatResponse(
        session_id=session_id,
        message="No problem! Which country and visa type would you like instead?",
        state=settings.STATE_CHATTING,
        is_form_ready=False
    )


async def handle_form_matched_state(session_id: str, data: dict, message: str):
    """Handle form matched - waiting for user confirmation to start"""
    message_lower = message.lower()
    form_id = data.get("matched_form_id")
    form = await get_form_by_id(form_id)
    
    if not form:
        data["state"] = settings.STATE_CHATTING
        await save_conversation(session_id, data)
        
        return ChatResponse(
            session_id=session_id,
            message="Sorry, there was an issue. Let's start again. Which visa do you need?",
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # Check if user wants to start
    start_words = ["yes", "start", "begin", "ok", "okay", "sure", "let's", "ready", "proceed"]
    no_words = ["no", "not", "don't", "dont", "cancel", "stop", "maybe later", "not now"]
    
    if any(word in message_lower for word in start_words):
        # Start filling form
        await ConversationManager.transition_to_filling_form(session_id)
        
        field, idx, total = await ConversationManager.get_current_field(session_id)
        question = await generate_question_for_field(field, idx, total)
        
        start_msg = f"Great! Let's begin filling the form. {question} Tip: Type 'help' anytime if you need assistance!"
        
        return ChatResponse(
            session_id=session_id,
            message=start_msg,
            state=settings.STATE_FILLING_FORM,
            is_form_ready=False,
            matched_form=None
        )
    
    # Check if user declines
    if any(word in message_lower for word in no_words):
        data["state"] = settings.STATE_CHATTING
        data["matched_form_id"] = None
        data["history"] = []
        await save_conversation(session_id, data)
        
        return ChatResponse(
            session_id=session_id,
            message="No problem at all! Take your time. If you need help with visa applications in the future, I'm here!",
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # User asking about the form
    history = data.get("history", [])
    history.append({"role": "user", "content": message})
    
    system_prompt = f"""You are a helpful visa consultant.

The user has been matched with this form:
- Title: {form['title']}
- Visa Type: {form['visa_type']}
- Country: {form.get('country', 'Unknown')}
- Total Fields: {len(form.get('fields', []))}

Answer their question in 2-3 sentences.
Encourage them to start when ready by saying "Yes, let's begin"
"""
    
    ai_response = await call_openai_chat(
        messages=history,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=300
    )
    
    history.append({"role": "assistant", "content": ai_response})
    data["history"] = history
    await save_conversation(session_id, data)
    
    return ChatResponse(
        session_id=session_id,
        message=ai_response,
        state=settings.STATE_FORM_MATCHED,
        is_form_ready=True,
        matched_form={
            "form_id": form["form_id"],
            "title": form["title"],
            "visa_type": form["visa_type"],
            "country": form.get("country", "N/A"),
            "total_fields": len(form.get("fields", []))
        }
    )


async def handle_chatting_state(session_id: str, data: dict, message: str, history: list):
    """
    IMPROVED: Warm greetings + 5-6 questions before matching
    """
    # Add user message
    history.append({"role": "user", "content": message})
    
    # Count user messages
    user_msg_count = len([m for m in history if m["role"] == "user"])
    
    # WARM GREETING for first message
    if user_msg_count == 1:
        greeting = "Hello! Welcome to our Visa Application Assistant! I'm here to help you find and fill the right visa form for your needs. Let's have a quick chat to understand your requirements. To get started, which country would you like to visit?"
        
        history.append({"role": "assistant", "content": greeting})
        data["history"] = history
        await save_conversation(session_id, data)
        
        return ChatResponse(
            session_id=session_id,
            message=greeting,
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # PROFESSIONAL CONSULTATION (questions 2-6)
    system_prompt = """You are a professional visa consultant assistant.

Your role:
1. Have a warm, natural conversation to understand visa needs
2. Ask ONE clear question at a time
3. Focus on: destination country, visa type, purpose, duration, background
4. Be friendly and patient - 2-3 sentences max per response
5. Handle uncertainty gracefully ("not sure" = keep asking)

Important:
- If user says "not sure" or "maybe", ask a different question
- Don't rush - gather information naturally
- After 5-6 exchanges, a form will be matched automatically

Example questions:
- "Which country would you like to visit?"
- "What's the purpose of your trip?"
- "How long are you planning to stay?"
- "Have you traveled to this country before?"

Keep it conversational and friendly."""
    
    # Get AI response
    ai_response = await call_openai_chat(
        messages=history,
        system_prompt=system_prompt,
        temperature=settings.CHAT_TEMPERATURE,
        max_tokens=settings.CHAT_MAX_TOKENS
    )
    
    # Add AI response
    history.append({"role": "assistant", "content": ai_response})
    data["history"] = history
    await save_conversation(session_id, data)
    
    # Try matching after 6+ messages (5-6 questions answered)
    if user_msg_count >= settings.MIN_MESSAGES_FOR_MATCHING:
        print(f"Attempting form matching (messages: {user_msg_count})...")
        
        matched = await match_form_from_conversation(history)
        
        if matched:
            return await process_matching_result(session_id, data, matched, ai_response)
    
    # Continue chatting
    return ChatResponse(
        session_id=session_id,
        message=ai_response,
        state=settings.STATE_CHATTING,
        is_form_ready=False
    )


async def process_matching_result(session_id: str, data: dict, matched: dict, ai_response: str):
    """Process form matching results"""
    
    # OFF TOPIC
    if matched.get("form_id") == "OFF_TOPIC":
        return ChatResponse(
            session_id=session_id,
            message=matched.get("message", "I'm here to help with visa applications. Which country would you like to visit?"),
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # NO MATCH
    if matched.get("form_id") == "NO_MATCH":
        missing_info = matched.get("missing_info", [])
        
        help_msg = matched.get("message", "I need more information to find the right form.")
        
        if missing_info:
            help_msg += " Could you tell me: " + ", ".join(missing_info)
        
        return ChatResponse(
            session_id=session_id,
            message=help_msg,
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # MULTIPLE MATCHES
    if matched.get("form_id") == "MULTIPLE_MATCHES":
        forms = matched.get("matched_forms", [])
        
        if not forms:
            return ChatResponse(
                session_id=session_id,
                message=ai_response,
                state=settings.STATE_CHATTING,
                is_form_ready=False
            )
        
        recommendation = await ai_recommend_from_multiple(forms, data.get("history", []))
        
        data["multiple_matched_forms"] = forms
        data["recommended_form"] = recommendation["recommended_form"]
        data["state"] = settings.STATE_AWAITING_CONFIRMATION
        await save_conversation(session_id, data)
        
        return ChatResponse(
            session_id=session_id,
            message=recommendation["message"],
            state=settings.STATE_AWAITING_CONFIRMATION,
            is_form_ready=False,
            multiple_forms=forms
        )
    
    # PERFECT SINGLE MATCH
    if matched.get("visa_type"):
        await ConversationManager.transition_to_form_matched(session_id, matched["form_id"])
        
        match_msg = f"Perfect! I found the right form for you: {matched['title']}, Visa Type: {matched['visa_type']}, Country: {matched.get('country', 'N/A')}, Total Fields: {len(matched.get('fields', []))}. May we proceed with filling this form? Say 'Yes, let's begin' when you're ready!"
        
        return ChatResponse(
            session_id=session_id,
            message=match_msg,
            state=settings.STATE_FORM_MATCHED,
            is_form_ready=True,
            matched_form={
                "form_id": matched["form_id"],
                "title": matched["title"],
                "visa_type": matched["visa_type"],
                "country": matched.get("country", "N/A"),
                "total_fields": len(matched.get("fields", []))
            }
        )
    
    # Fallback
    return ChatResponse(
        session_id=session_id,
        message=ai_response,
        state=settings.STATE_CHATTING,
        is_form_ready=False
    )


async def ai_recommend_from_multiple(forms: list, history: list) -> dict:
    """Use AI to recommend best form from multiple matches"""
    conversation_text = " ".join([m["content"] for m in history if m["role"] == "user"])
    
    forms_info = "\n".join([
        f"{i+1}. {f['title']} - {f['visa_type']} ({f.get('country', 'N/A')})"
        for i, f in enumerate(forms)
    ])
    
    recommend_prompt = f"""Multiple forms match the user's needs.

CONVERSATION:
{conversation_text}

AVAILABLE FORMS:
{forms_info}

Choose the BEST form and explain why.

Return JSON:
{{
  "recommended_index": 0,
  "explanation": "Based on your needs, this visa is most suitable because..."
}}"""
    
    try:
        response = await call_openai_chat(
            messages=[{"role": "user", "content": recommend_prompt}],
            system_prompt="You are a visa recommendation expert. Return only JSON.",
            temperature=0.6,
            max_tokens=300
        )
        
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        import json
        result = json.loads(response)
        
        idx = result.get("recommended_index", 0)
        explanation = result.get("explanation", "")
        
        if 0 <= idx < len(forms):
            recommended = forms[idx]
            
            message = f"I found {len(forms)} possible forms. I recommend: {recommended['title']}, {recommended['visa_type']} visa for {recommended.get('country', 'N/A')}. {explanation} Is this correct? Say 'Yes' to proceed!"
            
            return {
                "recommended_form": recommended,
                "message": message
            }
    
    except Exception as e:
        print(f"AI recommendation failed: {e}")
    
    # Fallback
    recommended = forms[0]
    
    message = f"I found {len(forms)} matching forms. I recommend: {recommended['title']}, {recommended['visa_type']} for {recommended.get('country', 'N/A')}. This matches your needs best. Say 'Yes' to proceed!"
    
    return {
        "recommended_form": recommended,
        "message": message
    }