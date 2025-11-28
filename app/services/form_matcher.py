"""
AI-First Form Matching Service
✅ FULLY FIXED: All async/await properly added
"""

import json
from typing import List, Dict, Optional
from app.core.storage import load_forms_db
from app.services.ai_service import call_openai_chat


async def is_conversation_about_visa(conversation: List[Dict]) -> bool:
    """
    Check if conversation is about visa/immigration using AI
    """
    user_messages = [m["content"] for m in conversation if m["role"] == "user"]
    recent_text = " ".join(user_messages[-2:])  # Last 2 messages
    
    check_prompt = f"""Is this conversation about visa, immigration, or international travel applications?

Conversation: "{recent_text}"

Answer ONLY "YES" or "NO":"""
    
    try:
        response = await call_openai_chat(
            messages=[{"role": "user", "content": check_prompt}],
            system_prompt="You are a topic classifier. Return only YES or NO.",
            temperature=0.3,
            max_tokens=5
        )
        return "YES" in response.strip().upper()
    except:
        # Default to true to avoid blocking legitimate requests
        return True


async def match_form_from_conversation(conversation: List[Dict]) -> Optional[Dict]:
    """
    AI-driven form matching - no hardcoded rules
    
    Returns:
        - Single form if one clear match
        - Multiple forms dict if user needs to choose
        - Off-topic dict if not visa-related
        - No-match dict if no suitable forms
    """
    
    # Step 1: Check if conversation is about visa/immigration
    is_visa_related = await is_conversation_about_visa(conversation)
    
    if not is_visa_related:
        return {
            "form_id": "OFF_TOPIC",
            "title": "Off Topic",
            "message": "I'm specialized in visa applications. How can I help with your visa needs?"
        }
    
    # Step 2: Load available forms
    forms = await load_forms_db()  # ✅ FIXED: Added await
    
    if not forms:
        return None
    
    # Step 3: Extract conversation context
    user_messages = [m["content"] for m in conversation if m["role"] == "user"]
    conversation_text = " ".join(user_messages)
    
    print(f"\n🔍 Analyzing: {conversation_text[:100]}...")
    print(f"📋 Available forms: {len(forms)}")  # ✅ Now this works!
    
    # Step 4: Prepare forms summary for AI
    forms_summary = []
    for i, form in enumerate(forms):
        forms_summary.append({
            "index": i,
            "form_id": form["form_id"],
            "title": form["title"],
            "visa_type": form["visa_type"],
            "country": form.get("country", "Unknown"),
            "description": f"{form['visa_type']} visa for {form.get('country', 'Unknown')}"
        })
    
    print(f"📝 Forms Summary:")
    for fs in forms_summary:
        print(f"   [{fs['index']}] {fs['title']} - {fs['description']}")
    
    # Step 5: AI-powered intelligent matching
    matching_result = await ai_intelligent_match(conversation_text, forms_summary, forms)
    
    return matching_result


async def ai_intelligent_match(
    conversation_text: str, 
    forms_summary: List[Dict],
    forms: List[Dict]
) -> Optional[Dict]:
    """
    Let AI intelligently match forms based on conversation
    AI decides: single match, multiple matches, or no match
    """
    
    ai_prompt = f"""You are an expert visa consultant. Match the conversation with available visa forms.

CONVERSATION:
"{conversation_text}"

AVAILABLE FORMS:
{json.dumps(forms_summary, indent=2)}

IMPORTANT INSTRUCTIONS:
1. Carefully read what the user wants (country + visa type)
2. Look at the available forms and find matches
3. Example: "I want to study in USA" → Find "Student" visa for "USA"
4. Example: "Masters in USA" → Find "Student" visa for "USA"

MATCH RULES:
- If ONE clear country + purpose mentioned → SINGLE (return one index)
- If MULTIPLE countries mentioned → MULTIPLE (return multiple indices)
- If forms exist but you're unsure → Pick the closest SINGLE match
- ONLY use NO_MATCH if truly no relevant form exists

RESPONSE (JSON only):
{{
  "match_type": "SINGLE|MULTIPLE|NO_MATCH",
  "matched_indices": [0],
  "confidence": 0.9,
  "reasoning": "User wants to study in USA, matched with US Student Visa"
}}

Return ONLY JSON:"""
    
    try:
        response = await call_openai_chat(
            messages=[{"role": "user", "content": ai_prompt}],
            system_prompt="You are a visa form matching expert. Return only JSON.",
            temperature=0.3,
            max_tokens=400
        )
        
        # Parse AI response
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        ai_decision = json.loads(response)
        
        print(f"🤖 AI Decision: {ai_decision['match_type']} (confidence: {ai_decision['confidence']})")
        print(f"💭 Reasoning: {ai_decision['reasoning']}")
        
        # Process AI decision
        match_type = ai_decision.get("match_type", "NO_MATCH")
        matched_indices = ai_decision.get("matched_indices", [])
        confidence = ai_decision.get("confidence", 0.0)
        
        # Handle based on match type
        if match_type == "NO_MATCH" or confidence < 0.4:
            # Create helpful message without exposing internal reasoning
            missing = ai_decision.get("missing_info", [])
            
            base_msg = "I understand you need a visa, but I need a bit more information to find the perfect form for you."
            
            if not missing:
                missing = [
                    "Which country are you planning to visit?",
                    "What's the purpose of your visit?"
                ]
            
            return {
                "form_id": "NO_MATCH",
                "title": "No Match Found",
                "message": base_msg,
                "missing_info": missing
            }
        
        elif match_type == "MULTIPLE":
            # User needs to choose between multiple forms
            matched_forms = [forms[i] for i in matched_indices if 0 <= i < len(forms)]
            
            if not matched_forms:
                return await handle_no_match(ai_decision)
            
            print(f"✅ Multiple matches: {len(matched_forms)} forms")
            
            return {
                "form_id": "MULTIPLE_MATCHES",
                "title": "Multiple Forms Available",
                "matched_forms": matched_forms,
                "reasoning": ai_decision.get("reasoning", ""),
                "indices": matched_indices
            }
        
        else:  # SINGLE match
            if not matched_indices or matched_indices[0] >= len(forms):
                return await handle_no_match(ai_decision)
            
            matched_form = forms[matched_indices[0]]
            print(f"✅ Single match: {matched_form['title']}")
            
            return matched_form
    
    except Exception as e:
        print(f"❌ AI matching error: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to simple keyword matching
        return await fallback_keyword_match(conversation_text, forms)


async def fallback_keyword_match(conversation_text: str, forms: List[Dict]) -> Optional[Dict]:
    """
    Simple fallback if AI fails - basic keyword matching
    """
    print("🔄 Using fallback keyword matching...")
    
    conversation_lower = conversation_text.lower()
    
    # Score each form
    scored_forms = []
    
    for form in forms:
        score = 0
        
        # Check country
        country = form.get("country", "").lower()
        if country and country in conversation_lower:
            score += 5
        
        # Check visa type
        visa_type = form.get("visa_type", "").lower()
        if visa_type and visa_type in conversation_lower:
            score += 3
        
        # Check purpose keywords
        keywords = form.get("purpose_keywords", [])
        for kw in keywords:
            if kw.lower() in conversation_lower:
                score += 1
        
        if score > 0:
            scored_forms.append({"form": form, "score": score})
    
    if not scored_forms:
        return {
            "form_id": "NO_MATCH",
            "title": "No Match Found",
            "message": "I couldn't find a suitable visa form. Please tell me which country and visa type you need."
        }
    
    # Sort by score
    scored_forms.sort(key=lambda x: x["score"], reverse=True)
    
    # Return best match
    best = scored_forms[0]
    print(f"✅ Fallback match: {best['form']['title']} (score: {best['score']})")
    
    return best["form"]


async def handle_no_match(ai_decision: Dict) -> Dict:
    """
    Handle no match scenario with helpful guidance
    """
    return {
        "form_id": "NO_MATCH",
        "title": "No Match Found",
        "message": ai_decision.get("reasoning", "I need more details to find the right form."),
        "missing_info": ai_decision.get("missing_info", [
            "Which country are you applying to?",
            "What type of visa do you need?"
        ])
    }


# Legacy compatibility function
def get_matching_score(conversation_text: str, form: Dict) -> float:
    """
    Legacy function for backward compatibility (if needed elsewhere)
    Returns a simple 0-1 score
    """
    conversation_lower = conversation_text.lower()
    score = 0.0
    
    # Country match
    country = form.get("country", "").lower()
    if country and country in conversation_lower:
        score += 0.5
    
    # Visa type match
    visa_type = form.get("visa_type", "").lower()
    if visa_type and visa_type in conversation_lower:
        score += 0.3
    
    # Keywords match
    keywords = form.get("purpose_keywords", [])
    if keywords:
        matched = sum(1 for kw in keywords if kw.lower() in conversation_lower)
        score += 0.2 * (matched / len(keywords))
    
    return min(score, 1.0)