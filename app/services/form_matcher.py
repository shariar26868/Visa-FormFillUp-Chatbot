# # """
# # Form matching service
# # Matches user conversation with appropriate visa form
# # """

# # import json
# # from typing import List, Dict, Optional

# # from app.core.storage import load_forms_db
# # from app.services.ai_service import call_openai_chat

# # async def match_form_from_conversation(conversation: List[Dict]) -> Optional[Dict]:
# #     """
# #     Use AI to match user conversation with available forms
    
# #     Args:
# #         conversation: List of message dicts with 'role' and 'content'
    
# #     Returns:
# #         Matched form dict or None
# #     """
    
# #     forms = load_forms_db()
    
# #     if not forms:
# #         print("⚠️  No forms available for matching")
# #         return None
    
# #     # Extract user messages
# #     user_messages = [m["content"] for m in conversation if m["role"] == "user"]
# #     conversation_text = " ".join(user_messages)
    
# #     # Prepare forms summary for AI
# #     forms_summary = []
# #     for i, form in enumerate(forms):
# #         forms_summary.append({
# #             "index": i,
# #             "title": form["title"],
# #             "visa_type": form["visa_type"],
# #             "country": form.get("country", "Unknown"),
# #             "keywords": form["purpose_keywords"]
# #         })
    
# #     # AI prompt for matching
# #     prompt = f"""Based on this conversation, which visa form is most suitable?

# # Conversation:
# # {conversation_text}

# # Available forms:
# # {json.dumps(forms_summary, indent=2)}

# # Analyze the user's:
# # - Country of origin (if mentioned)
# # - Destination country
# # - Purpose (tourism, business, study, work, family)
# # - Duration and plans

# # Return ONLY the index number (0, 1, 2, etc.) of the best matching form.
# # If no good match, return -1.
# # Just return the number, nothing else."""

# #     try:
# #         response = await call_openai_chat(
# #             messages=[{"role": "user", "content": prompt}],
# #             system_prompt="You are an expert at matching user needs with visa forms. Be precise.",
# #             temperature=0.2,
# #             max_tokens=10
# #         )
        
# #         # Parse index
# #         index = int(response.strip())
        
# #         if 0 <= index < len(forms):
# #             matched_form = forms[index]
# #             print(f"✅ Matched form: {matched_form['title']}")
# #             return matched_form
# #         else:
# #             print("⚠️  AI returned invalid index")
    
# #     except Exception as e:
# #         print(f"❌ AI form matching failed: {e}")
    
# #     # Fallback: Simple keyword matching
# #     print("🔄 Using fallback keyword matching...")
# #     conversation_lower = conversation_text.lower()
    
# #     for form in forms:
# #         keywords = form.get("purpose_keywords", [])
# #         if any(keyword.lower() in conversation_lower for keyword in keywords):
# #             print(f"✅ Keyword matched form: {form['title']}")
# #             return form
    
# #     print("❌ No form matched")
# #     return None

# # def get_matching_score(conversation_text: str, form: Dict) -> float:
# #     """
# #     Calculate matching score between conversation and form
# #     (Simple keyword-based scoring)
    
# #     Args:
# #         conversation_text: User conversation text
# #         form: Form dict
    
# #     Returns:
# #         Score (0-1)
# #     """
    
# #     conversation_lower = conversation_text.lower()
# #     score = 0.0
    
# #     # Check visa type
# #     visa_type = form.get("visa_type", "").lower()
# #     if visa_type in conversation_lower:
# #         score += 0.4
    
# #     # Check keywords
# #     keywords = form.get("purpose_keywords", [])
# #     matched_keywords = sum(1 for kw in keywords if kw.lower() in conversation_lower)
    
# #     if keywords:
# #         score += 0.6 * (matched_keywords / len(keywords))
    
# #     return min(score, 1.0)



# # """
# # SUPER FLEXIBLE Form Matching Service
# # Handles multiple countries, multiple forms, and complex scenarios
# # """

# # import json
# # from typing import List, Dict, Optional, Tuple

# # from app.core.storage import load_forms_db
# # from app.services.ai_service import call_openai_chat


# # # ========== COUNTRY NORMALIZATION ==========
# # COUNTRY_ALIASES = {
# #     # North America
# #     "usa": ["usa", "us", "united states", "america", "united states of america", "u.s.", "u.s.a", "american"],
# #     "canada": ["canada", "canadian", "ca"],

# #     # UK / Europe
# #     "uk": ["uk", "united kingdom", "britain", "great britain", "england", "u.k.", "british"],
# #     "ireland": ["ireland", "irish", "ie", "eire"],
# #     "germany": ["germany", "german", "de", "deutschland"],
# #     "france": ["france", "french", "fr"],
# #     "spain": ["spain", "spanish", "es", "espana"],
# #     "italy": ["italy", "italian", "it"],
# #     "netherlands": ["netherlands", "dutch", "nl", "holland"],
# #     "sweden": ["sweden", "swedish", "se"],
# #     "norway": ["norway", "norwegian", "no"],
# #     "denmark": ["denmark", "danish", "dk"],
# #     "switzerland": ["switzerland", "swiss", "ch"],
# #     "finland": ["finland", "finnish", "fi"],
# #     "poland": ["poland", "polish", "pl"],
# #     "portugal": ["portugal", "portuguese", "pt"],
# #     "greece": ["greece", "greek", "gr"],
# #     "belgium": ["belgium", "belgian", "be"],
# #     "austria": ["austria", "austrian", "at"],
# #     "czech republic": ["czech republic", "czechia", "cz", "czech"],
# #     "hungary": ["hungary", "hungarian", "hu"],
# #     "romania": ["romania", "romanian", "ro"],
# #     "turkey": ["turkey", "türkiye", "turkish", "tr"],

# #     # Asia
# #     "india": ["india", "indian", "in"],
# #     "pakistan": ["pakistan", "pakistani", "pk"],
# #     "bangladesh": ["bangladesh", "bd", "bangla"],
# #     "nepal": ["nepal", "nepali", "np"],
# #     "sri lanka": ["sri lanka", "srilanka", "lankan", "lk"],
# #     "china": ["china", "chinese", "cn", "prc"],
# #     "japan": ["japan", "japanese", "jp"],
# #     "south korea": ["south korea", "korea", "korean", "kr"],
# #     "north korea": ["north korea", "dprk", "nk"],
# #     "singapore": ["singapore", "singaporean", "sg"],
# #     "malaysia": ["malaysia", "malaysian", "my"],
# #     "indonesia": ["indonesia", "indonesian", "id"],
# #     "philippines": ["philippines", "filipino", "ph", "pinoy"],
# #     "vietnam": ["vietnam", "vietnamese", "vn"],
# #     "thailand": ["thailand", "thai", "th"],
# #     "hong kong": ["hong kong", "hk", "hongkonger"],
# #     "taiwan": ["taiwan", "taiwanese", "tw"],

# #     # Middle East / GCC
# #     "uae": ["uae", "united arab emirates", "dubai", "abu dhabi", "emirati"],
# #     "saudi arabia": ["saudi arabia", "saudi", "ksa", "saudi arabian"],
# #     "qatar": ["qatar", "qatari", "qa"],
# #     "oman": ["oman", "omani", "om"],
# #     "kuwait": ["kuwait", "kuwaiti", "kw"],
# #     "bahrain": ["bahrain", "bahraini", "bh"],
# #     "jordan": ["jordan", "jordanian", "jo"],
# #     "lebanon": ["lebanon", "lebanese", "lb"],

# #     # Australia / Oceania
# #     "australia": ["australia", "australian", "aussie", "au"],
# #     "new zealand": ["new zealand", "nz", "kiwi"],

# #     # Africa
# #     "south africa": ["south africa", "sa", "south african", "rsa"],
# #     "nigeria": ["nigeria", "nigerian", "ng"],
# #     "kenya": ["kenya", "kenyan", "ke"],
# #     "egypt": ["egypt", "egyptian", "eg"],
# #     "ghana": ["ghana", "ghanaian", "gh"],
# #     "ethiopia": ["ethiopia", "ethiopian", "et"],
# #     "morocco": ["morocco", "moroccan", "ma"],

# #     # Latin America
# #     "mexico": ["mexico", "mexican", "mx"],
# #     "brazil": ["brazil", "brazilian", "br"],
# #     "argentina": ["argentina", "argentinian", "ar"],
# #     "colombia": ["colombia", "colombian", "co"],
# #     "chile": ["chile", "chilean", "cl"],
# #     "peru": ["peru", "peruvian", "pe"],
# # }


# # def normalize_country_name(country: str) -> List[str]:
# #     """
# #     Normalize country name and return all possible aliases
    
# #     Args:
# #         country: Country name from form
    
# #     Returns:
# #         List of country aliases
# #     """
# #     if not country:
# #         return []
    
# #     country_lower = country.lower().strip()
    
# #     # Find matching group
# #     for main_name, aliases in COUNTRY_ALIASES.items():
# #         if country_lower in aliases:
# #             return aliases
    
# #     # If not found in aliases, return original + lowercase
# #     return [country_lower, country.strip()]


# # def detect_countries_in_text(text: str) -> List[str]:
# #     """
# #     Detect all countries mentioned in conversation text
    
# #     Args:
# #         text: Conversation text
    
# #     Returns:
# #         List of detected country groups (e.g., ['usa', 'canada'])
# #     """
# #     text_lower = text.lower()
# #     detected = set()
    
# #     for main_name, aliases in COUNTRY_ALIASES.items():
# #         for alias in aliases:
# #             if alias in text_lower:
# #                 detected.add(main_name)
# #                 break
    
# #     return list(detected)


# # # ========== VISA TYPE PATTERNS ==========

# # VISA_TYPE_KEYWORDS = {
# #     "student": [
# #         # General
# #         "student", "study", "university", "college", "admission", "degree",
# #         "masters", "bachelor", "phd", "study permit", "academic", "exchange",

# #         # U.S.
# #         "f-1", "f1", "j-1", "j1", "m-1", "m1", "i-20", "i20", "sevis",

# #         # Canada
# #         "canada study permit", "sds", "dli number",

# #         # UK
# #         "tier 4", "uk student visa", "confirmation of acceptance of studies", "cas letter",

# #         # Australia
# #         "subclass 500", "australia student visa", "coe", "study in australia",

# #         # New Zealand
# #         "nz student visa", "fee-payer student visa"
# #     ],
    
    
# #     "tourist": [
# #         # General
# #         "tourist", "tourism", "visit", "travel", "vacation", "holiday",
# #         "sightseeing", "visitor visa", "short stay",

# #         # U.S.
# #         "b-1", "b-2", "b1", "b2", "esta",

# #         # Canada
# #         "trv", "temporary resident visa", "canada visitor visa", "eta",

# #         # UK
# #         "uk visitor visa", "standard visitor visa",

# #         # EU / Schengen
# #         "schengen visa", "type c visa", "europe tourist visa",

# #         # Australia
# #         "subclass 600", "eta australia", "visitor (600)",

# #         # New Zealand
# #         "nz visitor visa",
# #     ],
    
    
# #     "work": [
# #         # General
# #         "work", "job", "employment", "work permit", "skilled worker", "work visa",
# #         "job offer", "sponsor", "work authorization",

# #         # U.S.
# #         "h-1b", "h1b", "l-1", "l1", "o-1", "o1", "eb-3", "eb3", "perm labor",

# #         # Canada
# #         "express entry", "work permit canada", "lmia", "pgwp",

# #         # UK
# #         "skilled worker visa", "tier 2", "uk work visa", "sponsorship license",

# #         # EU
# #         "eu blue card", "work residence permit", "highly skilled migrant",

# #         # Australia
# #         "subclass 482", "tss visa", "subclass 189", "skilled independent visa",
# #         "subclass 190", "regional sponsored migration scheme",

# #         # New Zealand
# #         "nz skilled migrant", "accredited employer work visa"
# #     ],
    
    
# #     "business": [
# #         # General
# #         "business", "conference", "meeting", "trade", "entrepreneur", "investor",
# #         "startup", "business trip", "corporate", "business purpose",

# #         # U.S.
# #         "b1 business", "eb-5", "eb5 investor", "e-2 treaty investor",

# #         # Canada
# #         "canada business visa", "start-up visa", "investor program",

# #         # UK
# #         "innovator visa", "startup visa uk", "global talent visa",

# #         # EU
# #         "schengen business visa",

# #         # Australia
# #         "subclass 188", "business innovation", "investor stream",

# #         # New Zealand
# #         "nz entrepreneur visa"
# #     ],
    
    
# #     "family": [
# #         # General
# #         "family", "spouse", "parents", "children", "dependant", "marriage",
# #         "relative", "reunion", "partner", "fiancé", "fiancee", "dependent visa",

# #         # U.S.
# #         "k-1", "k1", "i-130", "cr1", "ir1", "family-based green card",

# #         # Canada
# #         "family sponsorship", "spousal sponsorship", "parent and grandparent program",

# #         # UK
# #         "uk spouse visa", "family settlement visa", "partner visa",

# #         # EU
# #         "eu family reunification", "dependent residence permit",

# #         # Australia
# #         "partner visa 820", "partner visa 309", "parent visa 103",

# #         # New Zealand
# #         "nz partnership visa", "family stream"
# #     ],
    
    
# #     "permanent": [
# #         # General
# #         "permanent", "pr", "permanent residence", "residence", "citizenship",
# #         "migrate", "immigration", "settle", "indefinite stay", "移民",

# #         # U.S.
# #         "green card", "dv lottery", "i-485", "adjustment of status",

# #         # Canada
# #         "express entry", "canada pr", "crs score", "provincial nominee program", "pnp",

# #         # UK
# #         "indefinite leave to remain", "ilr", "uk settlement",

# #         # EU
# #         "eu long-term residence", "permanent residence permit",

# #         # Australia
# #         "subclass 189", "subclass 190", "australia pr", "regional pr",

# #         # New Zealand
# #         "nz resident visa", "nz permanent resident"
# #     ]
# # }


# # def detect_visa_types_in_text(text: str) -> List[str]:
# #     """
# #     Detect visa types mentioned in conversation
    
# #     Args:
# #         text: Conversation text
    
# #     Returns:
# #         List of detected visa types (e.g., ['student', 'work'])
# #     """
# #     text_lower = text.lower()
# #     detected = set()
    
# #     for visa_type, keywords in VISA_TYPE_KEYWORDS.items():
# #         for keyword in keywords:
# #             if keyword in text_lower:
# #                 detected.add(visa_type)
# #                 break
    
# #     return list(detected)


# # # ========== IMMIGRATION CHECK ==========

# # async def check_if_immigration_related(conversation: List[Dict]) -> bool:
# #     """
# #     Check if conversation is about immigration/visa topics
# #     """
# #     user_messages = [m["content"] for m in conversation if m["role"] == "user"]
# #     conversation_text = " ".join(user_messages[-3:])
    
# #     # Quick keyword check first (faster)
# #     immigration_keywords = [
# #         "visa", "immigration", "travel", "visit", "country", "passport",
# #         "form", "application", "permit", "embassy", "consulate", "study abroad"
# #     ]
    
# #     if any(keyword in conversation_text.lower() for keyword in immigration_keywords):
# #         return True
    
# #     # AI check if keywords don't match
# #     check_prompt = f"""Is this conversation about immigration, visa, or international travel?

# # Conversation: {conversation_text}

# # Return ONLY "YES" or "NO":"""
    
# #     try:
# #         response = await call_openai_chat(
# #             messages=[{"role": "user", "content": check_prompt}],
# #             system_prompt="You are a classifier. Return only YES or NO.",
# #             temperature=0.1,
# #             max_tokens=5
# #         )
# #         return "YES" in response.strip().upper()
# #     except:
# #         return True  # Default to true to avoid blocking


# # # ========== MULTI-FORM MATCHING ==========

# # async def match_form_from_conversation(conversation: List[Dict]) -> Optional[Dict]:
# #     """
# #     Match forms from conversation - supports MULTIPLE FORMS
    
# #     Returns:
# #         - Single form dict if one perfect match
# #         - Multiple forms dict if user needs multiple forms
# #         - OFF_TOPIC dict if not immigration-related
# #         - NO_MATCH dict if no suitable forms found
# #     """
    
# #     # Step 1: Immigration check
# #     is_immigration = await check_if_immigration_related(conversation)
    
# #     if not is_immigration:
# #         print("🚫 Not immigration-related")
# #         return {
# #             "form_id": "OFF_TOPIC",
# #             "title": "Off Topic",
# #             "error": "NOT_IMMIGRATION_RELATED"
# #         }
    
# #     # Step 2: Load forms
# #     forms = load_forms_db()
    
# #     if not forms:
# #         print("⚠️  No forms in database")
# #         return None
    
# #     # Step 3: Extract conversation
# #     user_messages = [m["content"] for m in conversation if m["role"] == "user"]
# #     conversation_text = " ".join(user_messages)
    
# #     print(f"\n🔍 Analyzing conversation: {conversation_text[:150]}...")
# #     print(f"📋 Available forms: {len(forms)}")
    
# #     # Step 4: Detect countries and visa types in conversation
# #     detected_countries = detect_countries_in_text(conversation_text)
# #     detected_visa_types = detect_visa_types_in_text(conversation_text)
    
# #     print(f"🌍 Detected countries: {detected_countries}")
# #     print(f"📝 Detected visa types: {detected_visa_types}")
    
# #     # Step 5: Score each form
# #     form_scores = []
    
# #     for i, form in enumerate(forms):
# #         score = calculate_form_score(form, conversation_text, detected_countries, detected_visa_types)
        
# #         if score > 0:
# #             form_scores.append({
# #                 "index": i,
# #                 "form": form,
# #                 "score": score
# #             })
# #             print(f"  ✓ Form {i}: {form['title']} - Score: {score}")
    
# #     # Sort by score (highest first)
# #     form_scores.sort(key=lambda x: x["score"], reverse=True)
    
# #     # Step 6: Decide what to return
    
# #     if not form_scores:
# #         # No matching forms found
# #         print("❌ No forms matched")
# #         return await generate_no_match_response(conversation_text, detected_countries, detected_visa_types)
    
# #     # Check if user wants multiple forms (multiple countries detected)
# #     if len(detected_countries) > 1 or len([f for f in form_scores if f["score"] >= 5]) > 1:
# #         # Multiple strong matches - ask user to choose
# #         top_matches = [f for f in form_scores if f["score"] >= 5][:3]  # Top 3
        
# #         if len(top_matches) > 1:
# #             print(f"✅ Multiple forms matched: {len(top_matches)}")
# #             return await generate_multiple_match_response(top_matches, conversation_text)
    
# #     # Single best match
# #     best_match = form_scores[0]
    
# #     if best_match["score"] >= 5:  # Good confidence threshold
# #         print(f"✅ Best match: {best_match['form']['title']} (Score: {best_match['score']})")
# #         return best_match["form"]
    
# #     # Low confidence - try AI matching
# #     print("🤖 Trying AI-based matching...")
# #     ai_match = await ai_based_matching(conversation_text, forms, form_scores)
    
# #     if ai_match:
# #         return ai_match
    
# #     # Still no good match
# #     return await generate_no_match_response(conversation_text, detected_countries, detected_visa_types)


# # def calculate_form_score(
# #     form: Dict, 
# #     conversation_text: str,
# #     detected_countries: List[str],
# #     detected_visa_types: List[str]
# # ) -> float:
# #     """
# #     Calculate matching score for a form
    
# #     Scoring:
# #     - Country match: +10 points
# #     - Visa type match: +5 points
# #     - Purpose keywords: +2 points each
# #     - Form title relevance: +3 points
# #     """
# #     score = 0
# #     conversation_lower = conversation_text.lower()
    
# #     # Country matching
# #     form_country = form.get("country", "").lower()
# #     form_country_aliases = normalize_country_name(form_country)
    
# #     for detected in detected_countries:
# #         if detected in form_country_aliases or form_country in COUNTRY_ALIASES.get(detected, []):
# #             score += 10
# #             print(f"    Country match: {detected} ↔ {form_country} (+10)")
# #             break
    
# #     # Visa type matching
# #     form_visa_type = form.get("visa_type", "").lower()
    
# #     for detected_type in detected_visa_types:
# #         type_keywords = VISA_TYPE_KEYWORDS.get(detected_type, [])
# #         if any(kw in form_visa_type for kw in type_keywords):
# #             score += 5
# #             print(f"    Visa type match: {detected_type} (+5)")
# #             break
    
# #     # Purpose keywords matching
# #     form_keywords = form.get("purpose_keywords", [])
# #     for keyword in form_keywords:
# #         if keyword.lower() in conversation_lower:
# #             score += 2
# #             print(f"    Keyword match: {keyword} (+2)")
    
# #     # Title relevance
# #     form_title = form.get("title", "").lower()
# #     for detected_type in detected_visa_types:
# #         if detected_type in form_title:
# #             score += 3
# #             print(f"    Title relevance: {detected_type} in title (+3)")
    
# #     return score


# # async def ai_based_matching(
# #     conversation_text: str,
# #     forms: List[Dict],
# #     scored_forms: List[Dict]
# # ) -> Optional[Dict]:
# #     """
# #     Use AI as fallback matching when keyword-based fails
# #     """
    
# #     # Prepare forms summary
# #     forms_summary = []
# #     for i, form in enumerate(forms):
# #         forms_summary.append({
# #             "index": i,
# #             "form_id": form["form_id"],
# #             "title": form["title"],
# #             "visa_type": form["visa_type"],
# #             "country": form.get("country", "Unknown"),
# #             "keywords": form.get("purpose_keywords", [])
# #         })
    
# #     prompt = f"""You are an expert visa consultant. Match the conversation with the best form.

# # Conversation:
# # {conversation_text}

# # Available Forms:
# # {json.dumps(forms_summary, indent=2)}

# # Rules:
# # 1. Match destination country first (USA, Canada, UK, Australia, etc.)
# # 2. Then match visa type (student, tourist, work, business, family)
# # 3. Consider keywords and user intent

# # Return ONLY the index number (0, 1, 2...) of the best form, or -1 if no good match.
# # Just the number:"""
    
# #     try:
# #         response = await call_openai_chat(
# #             messages=[{"role": "user", "content": prompt}],
# #             system_prompt="You are a visa form matcher. Return only the form index or -1.",
# #             temperature=0.2,
# #             max_tokens=10
# #         )
        
# #         index = int(response.strip())
        
# #         if 0 <= index < len(forms):
# #             print(f"✅ AI matched form index: {index}")
# #             return forms[index]
        
# #     except Exception as e:
# #         print(f"⚠️  AI matching failed: {e}")
    
# #     return None


# # async def generate_multiple_match_response(
# #     top_matches: List[Dict],
# #     conversation_text: str
# # ) -> Dict:
# #     """
# #     Generate response when multiple forms match
# #     User needs to choose which one
# #     """
    
# #     matched_forms = [m["form"] for m in top_matches]
    
# #     return {
# #         "form_id": "MULTIPLE_MATCHES",
# #         "title": "Multiple Forms Available",
# #         "matched_forms": matched_forms,
# #         "message": f"I found {len(matched_forms)} visa forms that match your needs. Please specify which one you'd like to fill.",
# #         "scores": [m["score"] for m in top_matches]
# #     }


# # async def generate_no_match_response(
# #     conversation_text: str,
# #     detected_countries: List[str],
# #     detected_visa_types: List[str]
# # ) -> Dict:
# #     """
# #     Generate helpful response when no forms match
# #     """
    
# #     return {
# #         "form_id": "NO_MATCH",
# #         "title": "No Matching Form",
# #         "error": "NO_FORM_AVAILABLE",
# #         "detected_countries": detected_countries,
# #         "detected_visa_types": detected_visa_types,
# #         "message": "I couldn't find a suitable visa form in my database for your requirements."
# #     }


# # # ========== LEGACY COMPATIBILITY ==========

# # def get_matching_score(conversation_text: str, form: Dict) -> float:
# #     """
# #     Legacy function for backward compatibility
# #     """
# #     detected_countries = detect_countries_in_text(conversation_text)
# #     detected_visa_types = detect_visa_types_in_text(conversation_text)
    
# #     score = calculate_form_score(form, conversation_text, detected_countries, detected_visa_types)
    
# #     # Normalize to 0-1 range
# #     return min(score / 20, 1.0)



# """
# AI-First Form Matching Service
# Removes hardcoded logic, lets AI handle everything intelligently
# """

# import json
# from typing import List, Dict, Optional
# from app.core.storage import load_forms_db
# from app.services.ai_service import call_openai_chat


# async def is_conversation_about_visa(conversation: List[Dict]) -> bool:
#     """
#     Check if conversation is about visa/immigration using AI
#     """
#     user_messages = [m["content"] for m in conversation if m["role"] == "user"]
#     recent_text = " ".join(user_messages[-2:])  # Last 2 messages
    
#     check_prompt = f"""Is this conversation about visa, immigration, or international travel applications?

# Conversation: "{recent_text}"

# Answer ONLY "YES" or "NO":"""
    
#     try:
#         response = await call_openai_chat(
#             messages=[{"role": "user", "content": check_prompt}],
#             system_prompt="You are a topic classifier. Return only YES or NO.",
#             temperature=0.1,
#             max_tokens=5
#         )
#         return "YES" in response.strip().upper()
#     except:
#         # Default to true to avoid blocking legitimate requests
#         return True


# async def match_form_from_conversation(conversation: List[Dict]) -> Optional[Dict]:
#     """
#     AI-driven form matching - no hardcoded rules
    
#     Returns:
#         - Single form if one clear match
#         - Multiple forms dict if user needs to choose
#         - Off-topic dict if not visa-related
#         - No-match dict if no suitable forms
#     """
    
#     # Step 1: Check if conversation is about visa/immigration
#     is_visa_related = await is_conversation_about_visa(conversation)
    
#     if not is_visa_related:
#         return {
#             "form_id": "OFF_TOPIC",
#             "title": "Off Topic",
#             "message": "I'm specialized in visa applications. How can I help with your visa needs?"
#         }
    
#     # Step 2: Load available forms
#     forms = load_forms_db()
    
#     if not forms:
#         return None
    
#     # Step 3: Extract conversation context
#     user_messages = [m["content"] for m in conversation if m["role"] == "user"]
#     conversation_text = " ".join(user_messages)
    
#     print(f"\n🔍 Analyzing: {conversation_text[:100]}...")
#     print(f"📋 Available forms: {len(forms)}")
    
#     # Step 4: Prepare forms summary for AI
#     forms_summary = []
#     for i, form in enumerate(forms):
#         forms_summary.append({
#             "index": i,
#             "form_id": form["form_id"],
#             "title": form["title"],
#             "visa_type": form["visa_type"],
#             "country": form.get("country", "Unknown"),
#             "description": f"{form['visa_type']} visa for {form.get('country', 'Unknown')}"
#         })
    
#     print(f"📝 Forms Summary:")
#     for fs in forms_summary:
#         print(f"   [{fs['index']}] {fs['title']} - {fs['description']}")
    
#     # Step 5: AI-powered intelligent matching
#     matching_result = await ai_intelligent_match(conversation_text, forms_summary, forms)
    
#     return matching_result


# async def ai_intelligent_match(
#     conversation_text: str, 
#     forms_summary: List[Dict],
#     forms: List[Dict]
# ) -> Optional[Dict]:
#     """
#     Let AI intelligently match forms based on conversation
#     AI decides: single match, multiple matches, or no match
#     """
    
#     ai_prompt = f"""You are an expert visa consultant. Match the conversation with available visa forms.

# CONVERSATION:
# "{conversation_text}"

# AVAILABLE FORMS:
# {json.dumps(forms_summary, indent=2)}

# IMPORTANT INSTRUCTIONS:
# 1. Carefully read what the user wants (country + visa type)
# 2. Look at the available forms and find matches
# 3. Example: "I want to study in USA" → Find "Student" visa for "USA"
# 4. Example: "Masters in USA" → Find "Student" visa for "USA"

# MATCH RULES:
# - If ONE clear country + purpose mentioned → SINGLE (return one index)
# - If MULTIPLE countries mentioned → MULTIPLE (return multiple indices)
# - If forms exist but you're unsure → Pick the closest SINGLE match
# - ONLY use NO_MATCH if truly no relevant form exists

# RESPONSE (JSON only):
# {{
#   "match_type": "SINGLE|MULTIPLE|NO_MATCH",
#   "matched_indices": [0],
#   "confidence": 0.9,
#   "reasoning": "User wants to study in USA, matched with US Student Visa"
# }}

# Return ONLY JSON:"""
    
#     try:
#         response = await call_openai_chat(
#             messages=[{"role": "user", "content": ai_prompt}],
#             system_prompt="You are a visa form matching expert. Return only JSON.",
#             temperature=0.3,
#             max_tokens=400
#         )
        
#         # Parse AI response
#         if "```json" in response:
#             response = response.split("```json")[1].split("```")[0].strip()
#         elif "```" in response:
#             response = response.split("```")[1].split("```")[0].strip()
        
#         ai_decision = json.loads(response)
        
#         print(f"🤖 AI Decision: {ai_decision['match_type']} (confidence: {ai_decision['confidence']})")
#         print(f"💭 Reasoning: {ai_decision['reasoning']}")
        
#         # Process AI decision
#         match_type = ai_decision.get("match_type", "NO_MATCH")
#         matched_indices = ai_decision.get("matched_indices", [])
#         confidence = ai_decision.get("confidence", 0.0)
        
#         # Handle based on match type
#         if match_type == "NO_MATCH" or confidence < 0.4:
#             # Create helpful message without exposing internal reasoning
#             missing = ai_decision.get("missing_info", [])
            
#             base_msg = "I understand you need a visa, but I need a bit more information to find the perfect form for you."
            
#             if not missing:
#                 missing = [
#                     "Which country are you planning to visit?",
#                     "What's the purpose of your visit?"
#                 ]
            
#             return {
#                 "form_id": "NO_MATCH",
#                 "title": "No Match Found",
#                 "message": base_msg,
#                 "missing_info": missing
#             }
        
#         elif match_type == "MULTIPLE":
#             # User needs to choose between multiple forms
#             matched_forms = [forms[i] for i in matched_indices if 0 <= i < len(forms)]
            
#             if not matched_forms:
#                 return await handle_no_match(ai_decision)
            
#             print(f"✅ Multiple matches: {len(matched_forms)} forms")
            
#             return {
#                 "form_id": "MULTIPLE_MATCHES",
#                 "title": "Multiple Forms Available",
#                 "matched_forms": matched_forms,
#                 "reasoning": ai_decision.get("reasoning", ""),
#                 "indices": matched_indices
#             }
        
#         else:  # SINGLE match
#             if not matched_indices or matched_indices[0] >= len(forms):
#                 return await handle_no_match(ai_decision)
            
#             matched_form = forms[matched_indices[0]]
#             print(f"✅ Single match: {matched_form['title']}")
            
#             return matched_form
    
#     except Exception as e:
#         print(f"❌ AI matching error: {e}")
#         import traceback
#         traceback.print_exc()
        
#         # Fallback to simple keyword matching
#         return await fallback_keyword_match(conversation_text, forms)


# async def fallback_keyword_match(conversation_text: str, forms: List[Dict]) -> Optional[Dict]:
#     """
#     Simple fallback if AI fails - basic keyword matching
#     """
#     print("🔄 Using fallback keyword matching...")
    
#     conversation_lower = conversation_text.lower()
    
#     # Score each form
#     scored_forms = []
    
#     for form in forms:
#         score = 0
        
#         # Check country
#         country = form.get("country", "").lower()
#         if country and country in conversation_lower:
#             score += 5
        
#         # Check visa type
#         visa_type = form.get("visa_type", "").lower()
#         if visa_type and visa_type in conversation_lower:
#             score += 3
        
#         # Check purpose keywords
#         keywords = form.get("purpose_keywords", [])
#         for kw in keywords:
#             if kw.lower() in conversation_lower:
#                 score += 1
        
#         if score > 0:
#             scored_forms.append({"form": form, "score": score})
    
#     if not scored_forms:
#         return {
#             "form_id": "NO_MATCH",
#             "title": "No Match Found",
#             "message": "I couldn't find a suitable visa form. Please tell me which country and visa type you need."
#         }
    
#     # Sort by score
#     scored_forms.sort(key=lambda x: x["score"], reverse=True)
    
#     # Return best match
#     best = scored_forms[0]
#     print(f"✅ Fallback match: {best['form']['title']} (score: {best['score']})")
    
#     return best["form"]


# async def handle_no_match(ai_decision: Dict) -> Dict:
#     """
#     Handle no match scenario with helpful guidance
#     """
#     return {
#         "form_id": "NO_MATCH",
#         "title": "No Match Found",
#         "message": ai_decision.get("reasoning", "I need more details to find the right form."),
#         "missing_info": ai_decision.get("missing_info", [
#             "Which country are you applying to?",
#             "What type of visa do you need?"
#         ])
#     }


# # Legacy compatibility function
# def get_matching_score(conversation_text: str, form: Dict) -> float:
#     """
#     Legacy function for backward compatibility (if needed elsewhere)
#     Returns a simple 0-1 score
#     """
#     conversation_lower = conversation_text.lower()
#     score = 0.0
    
#     # Country match
#     country = form.get("country", "").lower()
#     if country and country in conversation_lower:
#         score += 0.5
    
#     # Visa type match
#     visa_type = form.get("visa_type", "").lower()
#     if visa_type and visa_type in conversation_lower:
#         score += 0.3
    
#     # Keywords match
#     keywords = form.get("purpose_keywords", [])
#     if keywords:
#         matched = sum(1 for kw in keywords if kw.lower() in conversation_lower)
#         score += 0.2 * (matched / len(keywords))
    
#     return min(score, 1.0)




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