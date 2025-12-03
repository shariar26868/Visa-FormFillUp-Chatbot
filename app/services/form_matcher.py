"""
AI-First Form Matching Service
✅ IMPROVED: Soft OFF_TOPIC validation with detailed prompts
✅ 2-Tier approach: Fast keyword check → AI verification
"""

import json
from typing import List, Dict, Optional
from app.core.storage import load_forms_db
from app.services.ai_service import call_openai_chat


async def is_conversation_about_visa(conversation: List[Dict]) -> bool:
    """
    Intelligent OFF_TOPIC detection with soft validation
    Uses 2-tier approach: Fast keyword check → AI verification
    """
    user_messages = [m["content"] for m in conversation if m["role"] == "user"]
    
    # Handle empty conversation
    if not user_messages:
        return True
    
    recent_text = " ".join(user_messages[-3:])  # Last 3 messages for context
    full_text = " ".join(user_messages).lower()  # All messages for keyword check
    
    print(f"\n🔍 OFF_TOPIC Check Started")
    print(f"   Recent: '{recent_text[:80]}...'")
    
    # =====================================
    # TIER 1: Fast Keyword Check (No AI)
    # =====================================
    visa_keywords = [
        # Core visa terms
        "visa", "immigration", "passport", "embassy", "consulate",
        
        # Application related
        "application", "apply", "form", "document", "file", "paper",
        "requirement", "fill", "submit", "process",
        
        # Travel related
        "travel", "visit", "trip", "journey", "abroad", "international",
        "country", "destination",
        
        # Visa types
        "student", "tourist", "tourism", "work", "business", "transit",
        "study", "education", "employment", "schengen",
        
        # Common phrases
        "going to", "planning to", "want to visit", "need to travel",
        
        # Countries (major ones)
        "usa", "america", "uk", "britain", "canada", "australia",
        "schengen", "europe", "germany", "france", "spain", "italy"
    ]
    
    matched_keywords = [kw for kw in visa_keywords if kw in full_text]
    
    if matched_keywords:
        print(f"   ✅ TIER 1 PASS: Keywords found → {matched_keywords[:3]}")
        return True
    
    print(f"   ⚠️ TIER 1: No keywords - proceeding to AI check...")
    
    # =====================================
    # TIER 2: AI Semantic Understanding
    # =====================================
    
    ai_prompt = f"""You are a professional topic classifier for a visa application service.

Your task: Determine if this conversation is related to visa, immigration, travel documents, or international travel applications.

CONVERSATION HISTORY:
"{recent_text}"

CLASSIFICATION RULES:

✅ Return "YES" for these topics:
   - Visa applications and inquiries (tourist, student, work, business visas)
   - Immigration and travel documentation questions
   - Questions about required documents, forms, files, papers
   - Travel planning to other countries
   - Embassy/consulate related queries
   - Passport and travel permit questions
   - Study abroad, work abroad inquiries
   - Questions about application processes
   - Greetings and pleasantries in visa context (e.g., "hi", "hello", "thanks")
   - Vague questions that MIGHT be visa-related (e.g., "what do I need", "how to apply")
   - General inquiries that could be about visas

❌ Return "NO" ONLY for these clearly unrelated topics:
   - Sports, games, entertainment (e.g., "who won the match")
   - Food, cooking, recipes (e.g., "how to make pasta")
   - Weather inquiries (e.g., "will it rain tomorrow")
   - Technology troubleshooting unrelated to travel
   - Health advice unrelated to travel
   - Random facts or trivia
   - Personal life advice unrelated to travel
   - Shopping, e-commerce
   - Entertainment (movies, music, books) unrelated to travel

EXAMPLES:

User: "what files do I need to fill up"
Classification: YES
Reason: Likely asking about visa application documents

User: "I want to study in USA"
Classification: YES
Reason: Clear visa-related intent (student visa)

User: "help me with my application"
Classification: YES
Reason: Could be visa application

User: "what documents are required"
Classification: YES
Reason: Likely visa documentation query

User: "hi, I need some help"
Classification: YES
Reason: Greeting in service context, likely visa-related

User: "tell me requirements"
Classification: YES
Reason: Could be visa requirements

User: "what's the weather in London"
Classification: NO
Reason: Weather query, clearly off-topic

User: "who won the football match yesterday"
Classification: NO
Reason: Sports, clearly off-topic

User: "how to make chocolate cake"
Classification: NO
Reason: Cooking recipe, clearly off-topic

User: "recommend a good movie"
Classification: NO
Reason: Entertainment, clearly off-topic

IMPORTANT PRINCIPLES:
1. **Be PERMISSIVE**: When uncertain, lean toward YES
2. **Context matters**: If ANY message in history was visa-related, be MORE permissive
3. **Benefit of doubt**: Vague questions deserve YES unless CLEARLY off-topic
4. **User experience**: False negatives (rejecting valid visa questions) are WORSE than false positives

YOUR RESPONSE:
Answer with ONLY "YES" or "NO" - nothing else."""

    try:
        response = await call_openai_chat(
            messages=[{"role": "user", "content": ai_prompt}],
            system_prompt="You are a permissive topic classifier. When in doubt between YES/NO, choose YES to avoid blocking legitimate users. Return ONLY 'YES' or 'NO'.",
            temperature=0.1,  # Very low for consistency
            max_tokens=10
        )
        
        # Parse response
        response_clean = response.strip().upper()
        is_visa_related = "YES" in response_clean
        
        if is_visa_related:
            print(f"   ✅ TIER 2 PASS: AI classified as visa-related")
        else:
            print(f"   ❌ TIER 2 REJECT: AI classified as off-topic")
            print(f"   Response: {response_clean}")
        
        return is_visa_related
        
    except Exception as e:
        print(f"   ⚠️ TIER 2 ERROR: {e}")
        print(f"   🛡️ SAFETY: Defaulting to TRUE (allow conversation)")
        # CRITICAL: If AI fails, allow the conversation to avoid blocking users
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
    
    user_messages = [m["content"] for m in conversation if m["role"] == "user"]
    
    # =====================================
    # EARLY HANDLER: Document Questions Without Context
    # =====================================
    if len(user_messages) <= 3:  # Very early in conversation
        last_msg = user_messages[-1].lower()
        
        # Check if asking about documents/requirements
        doc_keywords = ["document", "file", "paper", "requirement", "what do i need", 
                       "what should i", "what type", "which file", "what kind"]
        is_doc_question = any(kw in last_msg for kw in doc_keywords)
        
        # Check if context is missing
        context_keywords = ["usa", "uk", "canada", "australia", "germany", "france",
                          "student", "tourist", "work", "visit", "study", "business",
                          "schengen", "america", "britain"]
        has_context = any(kw in " ".join(user_messages).lower() for kw in context_keywords)
        
        if is_doc_question and not has_context:
            print(f"📝 Early document question without context - asking for clarification")
            return {
                "form_id": "NO_MATCH",
                "title": "Need More Information",
                "message": "Great question! The required documents depend on which country and type of visa you need. Could you tell me: Which country would you like to visit, and what's the purpose of your trip (tourism, work, study)?",
                "missing_info": ["Country name", "Purpose of visit"]
            }
    
    # =====================================
    # Step 1: Check if conversation is about visa/immigration
    # =====================================
    is_visa_related = await is_conversation_about_visa(conversation)
    
    if not is_visa_related:
        return {
            "form_id": "OFF_TOPIC",
            "title": "Off Topic",
            "message": "I'm specialized in visa applications. How can I help with your visa needs?"
        }
    
    # =====================================
    # Step 2: Load available forms
    # =====================================
    forms = await load_forms_db()
    
    if not forms:
        return None
    
    # =====================================
    # Step 3: Extract conversation context
    # =====================================
    conversation_text = " ".join(user_messages)
    
    print(f"\n🔍 Form Matching Started")
    print(f"   Analyzing: {conversation_text[:100]}...")
    print(f"   Available forms: {len(forms)}")
    
    # =====================================
    # Step 4: Prepare forms summary for AI
    # =====================================
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
    for fs in forms_summary[:5]:  # Show first 5
        print(f"   [{fs['index']}] {fs['title']} - {fs['description']}")
    if len(forms_summary) > 5:
        print(f"   ... and {len(forms_summary) - 5} more forms")
    
    # =====================================
    # Step 5: AI-powered intelligent matching
    # =====================================
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
    
    ai_prompt = f"""You are an expert visa consultant with deep knowledge of visa types and requirements.

Your task: Analyze the user's conversation and match them with the most appropriate visa form(s).

USER'S CONVERSATION:
"{conversation_text}"

AVAILABLE VISA FORMS:
{json.dumps(forms_summary, indent=2)}

MATCHING INSTRUCTIONS:

1. **UNDERSTAND USER INTENT:**
   - What country do they want to visit?
   - What is their purpose? (study, tourism, work, business, etc.)
   - How long will they stay?
   - Any specific visa type mentioned?

2. **MATCH WITH FORMS:**
   - Look for EXACT country match first
   - Then match visa type/purpose
   - Consider synonyms (e.g., "study" = "Student", "work" = "Work/Employment")

3. **DECIDE MATCH TYPE:**

   **SINGLE** - Use when:
   - ONE clear country + ONE clear purpose mentioned
   - Only ONE form matches perfectly
   - User's intent is unambiguous
   - Example: "I want to study in USA" → US Student Visa (SINGLE match)

   **MULTIPLE** - Use when:
   - User mentions MULTIPLE countries (e.g., "USA or Canada")
   - User mentions MULTIPLE purposes (e.g., "tourism or business")
   - MULTIPLE forms match equally well
   - Example: "I want to visit Europe" → Multiple Schengen visas (MULTIPLE)

   **NO_MATCH** - Use ONLY when:
   - No country mentioned at all
   - No purpose/visa type mentioned at all
   - Available forms don't match user's needs
   - Need critical information to proceed
   - Example: "I need a visa" → Need country info (NO_MATCH)

4. **EXAMPLES:**

   User: "I want to study in USA for my Masters"
   → SINGLE match: US Student Visa (index 0)
   Reasoning: Clear country (USA) + Clear purpose (Student)

   User: "I'm planning to visit UK or France for tourism"
   → MULTIPLE matches: UK Tourist Visa, France Tourist Visa
   Reasoning: Multiple countries mentioned

   User: "I need a visa"
   → NO_MATCH
   Reasoning: Missing country and purpose
   Missing info: ["Which country?", "Purpose of visit?"]

   User: "I want to go to USA"
   → SINGLE match: US Tourist Visa (if available)
   Reasoning: Country clear, assume tourism if no purpose mentioned

5. **CONFIDENCE SCORING:**
   - 0.9-1.0: Perfect match (country + visa type clear)
   - 0.7-0.8: Good match (country clear, visa type inferred)
   - 0.5-0.6: Uncertain match (vague information)
   - Below 0.5: Use NO_MATCH

RESPONSE FORMAT (JSON only):
{{
  "match_type": "SINGLE" | "MULTIPLE" | "NO_MATCH",
  "matched_indices": [0, 1],
  "confidence": 0.85,
  "reasoning": "User wants to study in USA, matched with US Student Visa form",
  "missing_info": ["Country", "Purpose"]  // Only for NO_MATCH
}}

IMPORTANT:
- Be decisive - prefer SINGLE over MULTIPLE when possible
- Only use NO_MATCH if truly insufficient information
- Include clear reasoning for your decision
- Confidence should reflect match quality

Return ONLY valid JSON, nothing else:"""
    
    try:
        response = await call_openai_chat(
            messages=[{"role": "user", "content": ai_prompt}],
            system_prompt="You are a visa form matching expert. Analyze carefully and return only valid JSON with your matching decision.",
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse AI response
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        ai_decision = json.loads(response)
        
        print(f"\n🤖 AI Matching Decision:")
        print(f"   Type: {ai_decision['match_type']}")
        print(f"   Confidence: {ai_decision['confidence']}")
        print(f"   Reasoning: {ai_decision['reasoning']}")
        
        # Process AI decision
        match_type = ai_decision.get("match_type", "NO_MATCH")
        matched_indices = ai_decision.get("matched_indices", [])
        confidence = ai_decision.get("confidence", 0.0)
        
        # =====================================
        # Handle NO_MATCH
        # =====================================
        if match_type == "NO_MATCH" or confidence < 0.4:
            missing = ai_decision.get("missing_info", [])
            
            base_msg = "I understand you need a visa, but I need a bit more information to find the perfect form for you."
            
            if not missing:
                missing = [
                    "Which country are you planning to visit?",
                    "What's the purpose of your visit?"
                ]
            
            print(f"   ℹ️ Result: NO_MATCH - Need more info")
            
            return {
                "form_id": "NO_MATCH",
                "title": "Need More Information",
                "message": base_msg,
                "missing_info": missing
            }
        
        # =====================================
        # Handle MULTIPLE MATCHES
        # =====================================
        elif match_type == "MULTIPLE":
            matched_forms = [forms[i] for i in matched_indices if 0 <= i < len(forms)]
            
            if not matched_forms:
                return await handle_no_match(ai_decision)
            
            print(f"   ✅ Result: MULTIPLE matches → {len(matched_forms)} forms")
            
            return {
                "form_id": "MULTIPLE_MATCHES",
                "title": "Multiple Forms Available",
                "matched_forms": matched_forms,
                "reasoning": ai_decision.get("reasoning", ""),
                "indices": matched_indices
            }
        
        # =====================================
        # Handle SINGLE MATCH
        # =====================================
        else:  # SINGLE match
            if not matched_indices or matched_indices[0] >= len(forms):
                return await handle_no_match(ai_decision)
            
            matched_form = forms[matched_indices[0]]
            print(f"   ✅ Result: SINGLE match → {matched_form['title']}")
            
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
    print("\n🔄 Using fallback keyword matching...")
    
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
        print(f"   ❌ No matches found")
        return {
            "form_id": "NO_MATCH",
            "title": "No Match Found",
            "message": "I couldn't find a suitable visa form. Please tell me which country and visa type you need.",
            "missing_info": ["Country name", "Visa type or purpose"]
        }
    
    # Sort by score
    scored_forms.sort(key=lambda x: x["score"], reverse=True)
    
    # Return best match
    best = scored_forms[0]
    print(f"   ✅ Fallback match: {best['form']['title']} (score: {best['score']})")
    
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