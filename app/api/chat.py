# """
# Chat API - Natural Conversational Flow (Like Claude)
# ✅ IMPROVED: Natural conversation, smart answer correction, better memory
# """

# import uuid
# from datetime import datetime  
# from fastapi import APIRouter, HTTPException

# from app.models.schemas import ChatRequest, ChatResponse
# from app.core.config import settings
# from app.core.storage import (
#     load_conversation,
#     save_conversation,
#     get_form_by_id
# )
# from app.services.ai_service import call_openai_chat
# from app.services.form_matcher import match_form_from_conversation
# from app.services.question_generator import (
#     generate_question_for_field,
#     generate_help_for_field,
#     is_help_request
# )
# from app.services.answer_validator import validate_answer
# from app.services.conversation_manager import ConversationManager
# from app.services.smart_answer_correction import detect_answer_correction

# router = APIRouter()


# @router.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest):
#     """
#     Main chat endpoint - Natural conversation like Claude
#     """
    
#     # Initialize or load session
#     session_id = request.session_id or str(uuid.uuid4())
#     data = await load_conversation(session_id)
    
#     if not data.get("history"):
#         data["history"] = []
#         data["state"] = settings.STATE_CHATTING
    
#     current_state = data.get("state", settings.STATE_CHATTING)
#     history = data["history"]
    
#     print(f"\n{'='*60}")
#     print(f"Message: {request.message[:80]}...")
#     print(f"Current State: {current_state}")
#     print(f"History Length: {len(history)}")
#     print(f"{'='*60}\n")
    
#     # STATE: COMPLETED
#     if current_state == settings.STATE_COMPLETED:
#         return await handle_completed_state(session_id, data, request.message)
    
#     # STATE: FILLING_FORM
#     if current_state == settings.STATE_FILLING_FORM:
#         return await handle_filling_form_state(session_id, data, request.message)
    
#     # STATE: AWAITING_CONFIRMATION
#     if current_state == settings.STATE_AWAITING_CONFIRMATION:
#         return await handle_awaiting_confirmation_state(session_id, data, request.message)
    
#     # STATE: FORM_MATCHED
#     if current_state == settings.STATE_FORM_MATCHED:
#         return await handle_form_matched_state(session_id, data, request.message)
    
#     # STATE: CHATTING
#     return await handle_chatting_state(session_id, data, request.message, history)


# # ========== STATE HANDLERS ==========

# async def handle_completed_state(session_id: str, data: dict, message: str):
#     """Handle conversation when form is completed"""
#     form_id = data.get("matched_form_id")
#     form = await get_form_by_id(form_id)
    
#     # Check if user wants a new form
#     new_form_words = ["another", "new", "different", "next", "more"]
#     if any(word in message.lower() for word in new_form_words):
#         data["state"] = settings.STATE_CHATTING
#         data["matched_form_id"] = None
#         data["current_field_index"] = 0
#         data["history"] = []
#         await save_conversation(session_id, data)
        
#         return ChatResponse(
#             session_id=session_id,
#             message="Great! I'm ready to help with another visa application. Which country would you like to apply for?",
#             state=settings.STATE_CHATTING,
#             is_form_ready=False
#         )
    
#     # Show completion summary
#     answers_count = len(data.get("answers", {}))
#     total_fields = len(form.get("fields", []))
    
#     summary_msg = f"🎉 Congratulations! You've successfully completed the {form['title']}. All {answers_count} fields are filled. You can view your complete summary at /api/summary/{session_id}. Would you like to fill another visa form?"
    
#     return ChatResponse(
#         session_id=session_id,
#         message=summary_msg,
#         state=settings.STATE_COMPLETED,
#         is_form_ready=False,
#         matched_form={
#             "form_id": form["form_id"],
#             "title": form["title"],
#             "visa_type": form["visa_type"],
#             "country": form.get("country", "N/A")
#         }
#     )


# async def handle_filling_form_state(session_id: str, data: dict, message: str):
#     """Handle form filling with smart features"""
#     try:
#         # ✅ NEW: Check if user is correcting a previous answer
#         correction_result = await detect_answer_correction(session_id, message, data)
        
#         if correction_result["is_correction"]:
#             # User is fixing a previous answer
#             corrected_field = correction_result["field"]
#             new_answer = correction_result["new_answer"]
            
#             # Validate the new answer
#             is_valid, validation_msg = await validate_answer(corrected_field, new_answer)
            
#             if not is_valid:
#                 return ChatResponse(
#                     session_id=session_id,
#                     message=f"I understand you want to update '{corrected_field['label']}', but {validation_msg}",
#                     state=settings.STATE_FILLING_FORM,
#                     is_form_ready=False
#                 )
            
#             # Save the corrected answer
#             await ConversationManager.update_specific_answer(
#                 session_id, 
#                 corrected_field["id"], 
#                 new_answer
#             )
            
#             # Get current field to continue
#             current_field, idx, total = await ConversationManager.get_current_field(session_id)
#             next_question = await generate_question_for_field(current_field, idx, total)
            
#             response_msg = f"✅ Got it! I've updated your answer for '{corrected_field['label']}'. Now, let's continue: {next_question}"
            
#             return ChatResponse(
#                 session_id=session_id,
#                 message=response_msg,
#                 state=settings.STATE_FILLING_FORM,
#                 is_form_ready=False
#             )
        
#         # Get current field
#         field, field_index, total_fields = await ConversationManager.get_current_field(session_id)
        
#         print(f"Current Field: {field['label']} ({field_index + 1}/{total_fields})")
#         print(f"User Message: {message[:100]}...")
        
#         # Check if asking for help
#         if is_help_request(message):
#             print(f"User asking for help on field: {field['label']}")
            
#             help_text = await generate_help_for_field(field, message)
            
#             help_response = f"{help_text}\n\nOnce you understand, just provide your answer!"
            
#             return ChatResponse(
#                 session_id=session_id,
#                 message=help_response,
#                 state=settings.STATE_FILLING_FORM,
#                 is_form_ready=False
#             )
        
#         # Process as answer
#         print(f"Processing as answer...")
        
#         # Validate answer
#         is_valid, validation_msg = await validate_answer(field, message)
        
#         if not is_valid:
#             invalid_response = f"{validation_msg} Could you provide that again? (Type 'help' if you need assistance)"
            
#             return ChatResponse(
#                 session_id=session_id,
#                 message=invalid_response,
#                 state=settings.STATE_FILLING_FORM,
#                 is_form_ready=False
#             )
        
#         # Save answer and move to next
#         has_more_fields = await ConversationManager.save_answer(session_id, message)
        
#         if not has_more_fields:
#             # Form completed!
#             await ConversationManager.transition_to_completed(session_id)
            
#             form_id = data.get("matched_form_id")
#             form = await get_form_by_id(form_id)
            
#             completion_msg = f"🎉 Excellent! You've completed all {total_fields} fields of the {form['title']}. Your application information is ready! View your summary at /api/summary/{session_id}. Would you like to apply for another visa?"
            
#             return ChatResponse(
#                 session_id=session_id,
#                 message=completion_msg,
#                 state=settings.STATE_COMPLETED,
#                 is_form_ready=False,
#                 matched_form=form
#             )
        
#         # Get next field
#         next_field, next_idx, total = await ConversationManager.get_current_field(session_id)
#         next_question = await generate_question_for_field(next_field, next_idx, total)
        
#         response_msg = f"Perfect! {next_question}\n\n(Need help? Just ask!)"
        
#         return ChatResponse(
#             session_id=session_id,
#             message=response_msg,
#             state=settings.STATE_FILLING_FORM,
#             is_form_ready=False
#         )
    
#     except Exception as e:
#         print(f"Error in filling form: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))


# async def handle_awaiting_confirmation_state(session_id: str, data: dict, message: str):
#     """Handle multiple form choices"""
#     message_lower = message.lower()
#     recommended_form = data.get("recommended_form")
    
#     if not recommended_form:
#         data["state"] = settings.STATE_CHATTING
#         await save_conversation(session_id, data)
        
#         return ChatResponse(
#             session_id=session_id,
#             message="Let's start fresh. Which country would you like to visit?",
#             state=settings.STATE_CHATTING,
#             is_form_ready=False
#         )
    
#     # Check confirmation
#     yes_words = ["yes", "ok", "okay", "sure", "start", "continue", "proceed", "correct", "right"]
#     no_words = ["no", "not", "don't", "dont", "cancel", "stop", "wrong"]
    
#     if any(word in message_lower for word in yes_words):
#         await ConversationManager.transition_to_form_matched(
#             session_id,
#             recommended_form["form_id"]
#         )
        
#         form = await get_form_by_id(recommended_form["form_id"])
        
#         ready_msg = f"Perfect! ✨ Let's proceed with the {form['title']} ({form['visa_type']}). This form has {len(form.get('fields', []))} fields to fill. Ready to begin? Just say 'yes' or 'let's start'!"
        
#         return ChatResponse(
#             session_id=session_id,
#             message=ready_msg,
#             state=settings.STATE_FORM_MATCHED,
#             is_form_ready=True,
#             matched_form={
#                 "form_id": form["form_id"],
#                 "title": form["title"],
#                 "visa_type": form["visa_type"],
#                 "country": form.get("country", "N/A"),
#                 "total_fields": len(form.get("fields", []))
#             }
#         )
    
#     if any(word in message_lower for word in no_words):
#         data["state"] = settings.STATE_CHATTING
#         data["recommended_form"] = None
#         data["history"] = []
#         await save_conversation(session_id, data)
        
#         return ChatResponse(
#             session_id=session_id,
#             message="No problem! Let me know which country and visa type you'd prefer, and I'll find the right form for you.",
#             state=settings.STATE_CHATTING,
#             is_form_ready=False
#         )
    
#     # Unclear response - have natural conversation
#     history = data.get("history", [])
#     history.append({
#         "role": "user",
#         "content": message,
#         "timestamp": datetime.utcnow().isoformat()
#     })
    
#     system_prompt = f"""You are a helpful visa consultant. The user was offered this form:
# - {recommended_form['title']}
# - {recommended_form['visa_type']} for {recommended_form.get('country', 'Unknown')}

# Their response: "{message}"

# Respond naturally to clarify if this is the right form. Be conversational and helpful.
# End by asking if they'd like to proceed with this form."""
    
#     ai_response = await call_openai_chat(
#         messages=history,
#         system_prompt=system_prompt,
#         temperature=0.7,
#         max_tokens=200
#     )
    
#     history.append({
#         "role": "assistant",
#         "content": ai_response,
#         "timestamp": datetime.utcnow().isoformat()
#     })
    
#     data["history"] = history
#     await save_conversation(session_id, data)
    
#     return ChatResponse(
#         session_id=session_id,
#         message=ai_response,
#         state=settings.STATE_AWAITING_CONFIRMATION,
#         is_form_ready=False
#     )


# async def handle_form_matched_state(session_id: str, data: dict, message: str):
#     """Handle form matched - natural conversation before starting"""
#     message_lower = message.lower()
#     form_id = data.get("matched_form_id")
#     form = await get_form_by_id(form_id)
    
#     if not form:
#         data["state"] = settings.STATE_CHATTING
#         await save_conversation(session_id, data)
        
#         return ChatResponse(
#             session_id=session_id,
#             message="Sorry, something went wrong. Let's start again - which visa do you need?",
#             state=settings.STATE_CHATTING,
#             is_form_ready=False
#         )
    
#     # Check if user wants to start
#     start_words = ["yes", "start", "begin", "ok", "okay", "sure", "let's", "lets", "ready", "proceed"]
#     no_words = ["no", "not", "don't", "dont", "cancel", "stop", "maybe later", "not now"]
    
#     if any(word in message_lower for word in start_words):
#         # Start filling form
#         await ConversationManager.transition_to_filling_form(session_id)
        
#         field, idx, total = await ConversationManager.get_current_field(session_id)
#         question = await generate_question_for_field(field, idx, total)
        
#         start_msg = f"Great! Let's begin. 📋\n\n{question}\n\n(Tip: You can ask for help anytime, or correct previous answers naturally by just mentioning what you want to change)"
        
#         return ChatResponse(
#             session_id=session_id,
#             message=start_msg,
#             state=settings.STATE_FILLING_FORM,
#             is_form_ready=False,
#             matched_form=None
#         )
    
#     if any(word in message_lower for word in no_words):
#         data["state"] = settings.STATE_CHATTING
#         data["matched_form_id"] = None
#         data["history"] = []
#         await save_conversation(session_id, data)
        
#         return ChatResponse(
#             session_id=session_id,
#             message="No worries! Take your time. When you're ready for visa assistance, just let me know which country you're interested in.",
#             state=settings.STATE_CHATTING,
#             is_form_ready=False
#         )
    
#     # User asking questions about the form - have natural conversation
#     history = data.get("history", [])
    
#     history.append({
#         "role": "user", 
#         "content": message,
#         "timestamp": datetime.utcnow().isoformat()
#     })
    
#     system_prompt = f"""You are a friendly, helpful visa consultant. 

# The user has been matched with:
# - Form: {form['title']}
# - Visa Type: {form['visa_type']}
# - Country: {form.get('country', 'Unknown')}
# - Total Fields: {len(form.get('fields', []))}

# Respond naturally to their question. Be conversational, warm, and informative.
# Keep responses concise (2-3 sentences).
# Encourage them to start when ready by mentioning they can say "yes" or "let's begin"."""
    
#     ai_response = await call_openai_chat(
#         messages=history,
#         system_prompt=system_prompt,
#         temperature=0.7,
#         max_tokens=300
#     )
    
#     history.append({
#         "role": "assistant", 
#         "content": ai_response,
#         "timestamp": datetime.utcnow().isoformat()
#     })
    
#     data["history"] = history
#     await save_conversation(session_id, data)
    
#     return ChatResponse(
#         session_id=session_id,
#         message=ai_response,
#         state=settings.STATE_FORM_MATCHED,
#         is_form_ready=True,
#         matched_form={
#             "form_id": form["form_id"],
#             "title": form["title"],
#             "visa_type": form["visa_type"],
#             "country": form.get("country", "N/A"),
#             "total_fields": len(form.get("fields", []))
#         }
#     )


# async def handle_chatting_state(session_id: str, data: dict, message: str, history: list):
#     """
#     Natural conversation to understand visa needs
#     ✅ IMPROVED: More human-like, less robotic
#     """
    
#     history.append({
#         "role": "user", 
#         "content": message,
#         "timestamp": datetime.utcnow().isoformat()
#     })
    
#     user_msg_count = len([m for m in history if m["role"] == "user"])
    
#     # First message - warm greeting
#     if user_msg_count == 1:
#         greeting = "Hello! 👋 I'm here to help you with your visa application. I'll ask you a few questions to find the perfect form for your needs. Let's start - which country would you like to visit?"
        
#         history.append({
#             "role": "assistant", 
#             "content": greeting,
#             "timestamp": datetime.utcnow().isoformat()
#         })
        
#         data["history"] = history
#         await save_conversation(session_id, data)
        
#         return ChatResponse(
#             session_id=session_id,
#             message=greeting,
#             state=settings.STATE_CHATTING,
#             is_form_ready=False
#         )
    
#     # Natural consultation conversation
#     system_prompt = """You are a warm, professional visa consultant - think of yourself as a helpful friend who's an expert in visa applications.

# Your approach:
# - Have a natural conversation to understand their visa needs
# - Ask ONE thoughtful question at a time
# - Be conversational and warm (like talking to a friend, but professional)
# - Keep responses short (2-3 sentences maximum)
# - Focus on: destination country, visa type, purpose, duration, travel history
# - If they're unsure about something, gently guide them to think about it
# - Don't be robotic - be human!

# Important:
# - Never use bullet points or lists in conversation
# - Never say generic phrases like "I'm here to help" repeatedly
# - Be specific and personable
# - If they say "I'm not sure", ask a different helpful question

# Examples of good questions:
# - "Which country are you planning to visit?"
# - "What brings you there - work, study, or perhaps a vacation?"
# - "How long are you thinking of staying?"
# - "Have you traveled there before?"

# Keep it natural and flowing!"""
    
#     ai_response = await call_openai_chat(
#         messages=history,
#         system_prompt=system_prompt,
#         temperature=0.8,  # More creative/natural
#         max_tokens=200
#     )
    
#     history.append({
#         "role": "assistant", 
#         "content": ai_response,
#         "timestamp": datetime.utcnow().isoformat()
#     })
    
#     data["history"] = history
#     await save_conversation(session_id, data)
    
#     # Try matching after enough conversation
#     if user_msg_count >= settings.MIN_MESSAGES_FOR_MATCHING:
#         print(f"Attempting form matching (messages: {user_msg_count})...")
        
#         matched = await match_form_from_conversation(history)
        
#         if matched:
#             return await process_matching_result(session_id, data, matched, ai_response)
    
#     return ChatResponse(
#         session_id=session_id,
#         message=ai_response,
#         state=settings.STATE_CHATTING,
#         is_form_ready=False
#     )


# async def process_matching_result(session_id: str, data: dict, matched: dict, ai_response: str):
#     """Process form matching results"""
    
#     # OFF TOPIC
#     if matched.get("form_id") == "OFF_TOPIC":
#         return ChatResponse(
#             session_id=session_id,
#             message=matched.get("message", "I specialize in visa applications. What can I help you with regarding visas?"),
#             state=settings.STATE_CHATTING,
#             is_form_ready=False
#         )
    
#     # NO MATCH
#     if matched.get("form_id") == "NO_MATCH":
#         return ChatResponse(
#             session_id=session_id,
#             message=matched.get("message", "I need a bit more information. Could you tell me which country and visa type you need?"),
#             state=settings.STATE_CHATTING,
#             is_form_ready=False
#         )
    
#     # MULTIPLE MATCHES
#     if matched.get("form_id") == "MULTIPLE_MATCHES":
#         forms = matched.get("matched_forms", [])
        
#         if not forms:
#             return ChatResponse(
#                 session_id=session_id,
#                 message=ai_response,
#                 state=settings.STATE_CHATTING,
#                 is_form_ready=False
#             )
        
#         recommendation = await ai_recommend_from_multiple(forms, data.get("history", []))
        
#         data["multiple_matched_forms"] = forms
#         data["recommended_form"] = recommendation["recommended_form"]
#         data["state"] = settings.STATE_AWAITING_CONFIRMATION
#         await save_conversation(session_id, data)
        
#         return ChatResponse(
#             session_id=session_id,
#             message=recommendation["message"],
#             state=settings.STATE_AWAITING_CONFIRMATION,
#             is_form_ready=False,
#             multiple_forms=forms
#         )
    
#     # ✅ PERFECT SINGLE MATCH - Keep "Perfect!"
#     if matched.get("visa_type"):
#         await ConversationManager.transition_to_form_matched(session_id, matched["form_id"])
        
#         match_msg = f"Perfect! ✨ I found exactly what you need: {matched['title']} ({matched['visa_type']} for {matched.get('country', 'N/A')}). This form has {len(matched.get('fields', []))} fields. Ready to start filling it out? Just say 'yes' when you're ready!"
        
#         return ChatResponse(
#             session_id=session_id,
#             message=match_msg,
#             state=settings.STATE_FORM_MATCHED,
#             is_form_ready=True,
#             matched_form={
#                 "form_id": matched["form_id"],
#                 "title": matched["title"],
#                 "visa_type": matched["visa_type"],
#                 "country": matched.get("country", "N/A"),
#                 "total_fields": len(matched.get("fields", []))
#             }
#         )
    
#     return ChatResponse(
#         session_id=session_id,
#         message=ai_response,
#         state=settings.STATE_CHATTING,
#         is_form_ready=False
#     )


# async def ai_recommend_from_multiple(forms: list, history: list) -> dict:
#     """AI recommends best form from multiple matches"""
#     conversation_text = " ".join([m["content"] for m in history if m["role"] == "user"])
    
#     forms_info = "\n".join([
#         f"{i+1}. {f['title']} - {f['visa_type']} ({f.get('country', 'N/A')})"
#         for i, f in enumerate(forms)
#     ])
    
#     recommend_prompt = f"""Based on this conversation, recommend the BEST visa form:

# CONVERSATION:
# {conversation_text}

# AVAILABLE FORMS:
# {forms_info}

# Return JSON:
# {{
#   "recommended_index": 0,
#   "explanation": "Warm, natural explanation (2-3 sentences) of why this form suits them best"
# }}"""
    
#     try:
#         response = await call_openai_chat(
#             messages=[{"role": "user", "content": recommend_prompt}],
#             system_prompt="You are a visa expert. Be warm and conversational. Return only JSON.",
#             temperature=0.7,
#             max_tokens=300
#         )
        
#         if "```json" in response:
#             response = response.split("```json")[1].split("```")[0].strip()
#         elif "```" in response:
#             response = response.split("```")[1].split("```")[0].strip()
        
#         import json
#         result = json.loads(response)
        
#         idx = result.get("recommended_index", 0)
#         explanation = result.get("explanation", "")
        
#         if 0 <= idx < len(forms):
#             recommended = forms[idx]
            
#             message = f"I found {len(forms)} forms that could work for you. Based on what you've told me, I'd recommend the {recommended['title']} ({recommended['visa_type']} for {recommended.get('country', 'N/A')}). {explanation} Does this sound right?"
            
#             return {
#                 "recommended_form": recommended,
#                 "message": message
#             }
    
#     except Exception as e:
#         print(f"AI recommendation failed: {e}")
    
#     # Fallback
#     recommended = forms[0]
#     message = f"I found {len(forms)} matching forms. The {recommended['title']} ({recommended['visa_type']} for {recommended.get('country', 'N/A')}) seems like the best fit based on what you've shared. Would you like to use this one?"
    
#     return {
#         "recommended_form": recommended,
#         "message": message
#     }




"""
Chat API - Natural Conversational Flow (Like Claude)
IMPROVED: Natural conversation, smart answer correction, better memory
"""

import uuid
from datetime import datetime  
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
from app.services.smart_answer_correction import detect_answer_correction

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - Natural conversation like Claude
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
    
    summary_msg = f"Congratulations! You've successfully completed the {form['title']}. All {answers_count} fields are filled. You can view your complete summary at /api/summary/{session_id}. Would you like to fill another visa form?"
    
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
    """Handle form filling with smart features"""
    try:
        # Check if user is correcting a previous answer
        correction_result = await detect_answer_correction(session_id, message, data)
        
        if correction_result["is_correction"]:
            # User is fixing a previous answer
            corrected_field = correction_result["field"]
            new_answer = correction_result["new_answer"]
            
            # Validate the new answer
            is_valid, validation_msg = await validate_answer(corrected_field, new_answer)
            
            if not is_valid:
                return ChatResponse(
                    session_id=session_id,
                    message=f"I understand you want to update '{corrected_field['label']}', but {validation_msg}",
                    state=settings.STATE_FILLING_FORM,
                    is_form_ready=False
                )
            
            # Save the corrected answer
            await ConversationManager.update_specific_answer(
                session_id, 
                corrected_field["id"], 
                new_answer
            )
            
            # Get current field to continue
            current_field, idx, total = await ConversationManager.get_current_field(session_id)
            next_question = await generate_question_for_field(current_field, idx, total)
            
            response_msg = f"Got it! I've updated your answer for '{corrected_field['label']}'. Now, let's continue: {next_question}"
            
            return ChatResponse(
                session_id=session_id,
                message=response_msg,
                state=settings.STATE_FILLING_FORM,
                is_form_ready=False
            )
        
        # Get current field
        field, field_index, total_fields = await ConversationManager.get_current_field(session_id)
        
        print(f"Current Field: {field['label']} ({field_index + 1}/{total_fields})")
        print(f"User Message: {message[:100]}...")
        
        # Check if asking for help
        if is_help_request(message):
            print(f"User asking for help on field: {field['label']}")
            
            help_text = await generate_help_for_field(field, message)
            
            help_response = f"{help_text}\n\nOnce you understand, just provide your answer!"
            
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
            invalid_response = f"{validation_msg} Could you provide that again? (Type 'help' if you need assistance)"
            
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
            
            completion_msg = f"Excellent! You've completed all {total_fields} fields of the {form['title']}. Your application information is ready! View your summary at /api/summary/{session_id}. Would you like to apply for another visa?"
            
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
        
        response_msg = f"Perfect! {next_question}\n\n(Need help? Just ask!)"
        
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
            message="Let's start fresh. Which country would you like to visit?",
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # Check confirmation
    yes_words = ["yes", "ok", "okay", "sure", "start", "continue", "proceed", "correct", "right"]
    no_words = ["no", "not", "don't", "dont", "cancel", "stop", "wrong"]
    
    if any(word in message_lower for word in yes_words):
        await ConversationManager.transition_to_form_matched(
            session_id,
            recommended_form["form_id"]
        )
        
        form = await get_form_by_id(recommended_form["form_id"])
        
        ready_msg = f"Perfect! Let's proceed with the {form['title']} ({form['visa_type']}). This form has {len(form.get('fields', []))} fields to fill. Ready to begin? Just say 'yes' or 'let's start'!"
        
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
            message="No problem! Let me know which country and visa type you'd prefer, and I'll find the right form for you.",
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # Unclear response - have natural conversation
    history = data.get("history", [])
    history.append({
        "role": "user",
        "content": message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    system_prompt = f"""You are a helpful visa consultant. The user was offered this form:
- {recommended_form['title']}
- {recommended_form['visa_type']} for {recommended_form.get('country', 'Unknown')}

Their response: "{message}"

Respond naturally to clarify if this is the right form. Be conversational and helpful.
End by asking if they'd like to proceed with this form."""
    
    ai_response = await call_openai_chat(
        messages=history,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=200
    )
    
    history.append({
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    data["history"] = history
    await save_conversation(session_id, data)
    
    return ChatResponse(
        session_id=session_id,
        message=ai_response,
        state=settings.STATE_AWAITING_CONFIRMATION,
        is_form_ready=False
    )


async def handle_form_matched_state(session_id: str, data: dict, message: str):
    """Handle form matched - natural conversation before starting"""
    message_lower = message.lower()
    form_id = data.get("matched_form_id")
    form = await get_form_by_id(form_id)
    
    if not form:
        data["state"] = settings.STATE_CHATTING
        await save_conversation(session_id, data)
        
        return ChatResponse(
            session_id=session_id,
            message="Sorry, something went wrong. Let's start again - which visa do you need?",
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # Check if user wants to start
    start_words = ["yes", "start", "begin", "ok", "okay", "sure", "let's", "lets", "ready", "proceed"]
    no_words = ["no", "not", "don't", "dont", "cancel", "stop", "maybe later", "not now"]
    
    if any(word in message_lower for word in start_words):
        # Start filling form
        await ConversationManager.transition_to_filling_form(session_id)
        
        field, idx, total = await ConversationManager.get_current_field(session_id)
        question = await generate_question_for_field(field, idx, total)
        
        start_msg = f"Great! Let's begin.\n\n{question}\n\n(Tip: You can ask for help anytime, or correct previous answers naturally by just mentioning what you want to change)"
        
        return ChatResponse(
            session_id=session_id,
            message=start_msg,
            state=settings.STATE_FILLING_FORM,
            is_form_ready=False,
            matched_form=None
        )
    
    if any(word in message_lower for word in no_words):
        data["state"] = settings.STATE_CHATTING
        data["matched_form_id"] = None
        data["history"] = []
        await save_conversation(session_id, data)
        
        return ChatResponse(
            session_id=session_id,
            message="No worries! Take your time. When you're ready for visa assistance, just let me know which country you're interested in.",
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # User asking questions about the form - have natural conversation
    history = data.get("history", [])
    
    history.append({
        "role": "user", 
        "content": message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    system_prompt = f"""You are a friendly, helpful visa consultant. 

The user has been matched with:
- Form: {form['title']}
- Visa Type: {form['visa_type']}
- Country: {form.get('country', 'Unknown')}
- Total Fields: {len(form.get('fields', []))}

Respond naturally to their question. Be conversational, warm, and informative.
Keep responses concise (2-3 sentences).
Encourage them to start when ready by mentioning they can say "yes" or "let's begin"."""
    
    ai_response = await call_openai_chat(
        messages=history,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=300
    )
    
    history.append({
        "role": "assistant", 
        "content": ai_response,
        "timestamp": datetime.utcnow().isoformat()
    })
    
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
    Natural conversation to understand visa needs
    IMPROVED: More human-like, less robotic
    """
    
    history.append({
        "role": "user", 
        "content": message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    user_msg_count = len([m for m in history if m["role"] == "user"])
    
    # First message - AI generated greeting
    if user_msg_count == 1:
        greeting_prompt = """You are a warm, friendly visa consultant assistant. Generate a welcoming greeting for someone who just arrived.

Requirements:
- Be warm and welcoming
- Briefly introduce yourself as a visa application assistant
- Ask which country they'd like to visit
- Keep it conversational and natural (2-3 sentences max)
- Don't use bullet points or lists
- Be professional but friendly

Generate the greeting now:"""
        
        greeting = await call_openai_chat(
            messages=[{"role": "user", "content": greeting_prompt}],
            system_prompt="You are a friendly visa consultant. Generate a natural, warm greeting.",
            temperature=0.8,
            max_tokens=150
        )
        
        history.append({
            "role": "assistant", 
            "content": greeting,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        data["history"] = history
        await save_conversation(session_id, data)
        
        return ChatResponse(
            session_id=session_id,
            message=greeting,
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # Natural consultation conversation
    system_prompt = """You are a warm, professional visa consultant - think of yourself as a helpful friend who's an expert in visa applications.

Your approach:
- Have a natural conversation to understand their visa needs
- Ask ONE thoughtful question at a time
- Be conversational and warm (like talking to a friend, but professional)
- Keep responses short (2-3 sentences maximum)
- Focus on: destination country, visa type, purpose, duration, travel history
- If they're unsure about something, gently guide them to think about it
- Don't be robotic - be human!

Important:
- Never use bullet points or lists in conversation
- Never say generic phrases like "I'm here to help" repeatedly
- Be specific and personable
- If they say "I'm not sure", ask a different helpful question

Examples of good questions:
- "Which country are you planning to visit?"
- "What brings you there - work, study, or perhaps a vacation?"
- "How long are you thinking of staying?"
- "Have you traveled there before?"

Keep it natural and flowing!"""
    
    ai_response = await call_openai_chat(
        messages=history,
        system_prompt=system_prompt,
        temperature=0.8,
        max_tokens=200
    )
    
    history.append({
        "role": "assistant", 
        "content": ai_response,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    data["history"] = history
    await save_conversation(session_id, data)
    
    # Try matching after enough conversation
    if user_msg_count >= settings.MIN_MESSAGES_FOR_MATCHING:
        print(f"Attempting form matching (messages: {user_msg_count})...")
        
        matched = await match_form_from_conversation(history)
        
        if matched:
            return await process_matching_result(session_id, data, matched, ai_response)
    
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
            message=matched.get("message", "I specialize in visa applications. What can I help you with regarding visas?"),
            state=settings.STATE_CHATTING,
            is_form_ready=False
        )
    
    # NO MATCH
    if matched.get("form_id") == "NO_MATCH":
        return ChatResponse(
            session_id=session_id,
            message=matched.get("message", "I need a bit more information. Could you tell me which country and visa type you need?"),
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
        
        match_msg = f"Perfect! I found exactly what you need: {matched['title']} ({matched['visa_type']} for {matched.get('country', 'N/A')}). This form has {len(matched.get('fields', []))} fields. Ready to start filling it out? Just say 'yes' when you're ready!"
        
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
    
    return ChatResponse(
        session_id=session_id,
        message=ai_response,
        state=settings.STATE_CHATTING,
        is_form_ready=False
    )


async def ai_recommend_from_multiple(forms: list, history: list) -> dict:
    """AI recommends best form from multiple matches"""
    conversation_text = " ".join([m["content"] for m in history if m["role"] == "user"])
    
    forms_info = "\n".join([
        f"{i+1}. {f['title']} - {f['visa_type']} ({f.get('country', 'N/A')})"
        for i, f in enumerate(forms)
    ])
    
    recommend_prompt = f"""Based on this conversation, recommend the BEST visa form:

CONVERSATION:
{conversation_text}

AVAILABLE FORMS:
{forms_info}

Return JSON:
{{
  "recommended_index": 0,
  "explanation": "Warm, natural explanation (2-3 sentences) of why this form suits them best"
}}"""
    
    try:
        response = await call_openai_chat(
            messages=[{"role": "user", "content": recommend_prompt}],
            system_prompt="You are a visa expert. Be warm and conversational. Return only JSON.",
            temperature=0.7,
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
            
            message = f"I found {len(forms)} forms that could work for you. Based on what you've told me, I'd recommend the {recommended['title']} ({recommended['visa_type']} for {recommended.get('country', 'N/A')}). {explanation} Does this sound right?"
            
            return {
                "recommended_form": recommended,
                "message": message
            }
    
    except Exception as e:
        print(f"AI recommendation failed: {e}")
    
    # Fallback
    recommended = forms[0]
    message = f"I found {len(forms)} matching forms. The {recommended['title']} ({recommended['visa_type']} for {recommended.get('country', 'N/A')}) seems like the best fit based on what you've shared. Would you like to use this one?"
    
    return {
        "recommended_form": recommended,
        "message": message
    }