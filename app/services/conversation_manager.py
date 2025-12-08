"""
Conversation State Management
✅ UPDATED: Added update_specific_answer for smart corrections
"""

from typing import Tuple, Dict
from app.core.storage import load_conversation, save_conversation, get_form_by_id
from app.core.config import settings


class ConversationManager:
    """
    Manages conversation state transitions and form filling progress
    """
    
    @staticmethod
    async def transition_to_form_matched(session_id: str, form_id: str):
        """Transition to form matched state"""
        data = await load_conversation(session_id)
        data["state"] = settings.STATE_FORM_MATCHED
        data["matched_form_id"] = form_id
        data["current_field_index"] = 0
        data["answers"] = {}
        await save_conversation(session_id, data)
    
    @staticmethod
    async def transition_to_filling_form(session_id: str):
        """Transition to filling form state"""
        data = await load_conversation(session_id)
        data["state"] = settings.STATE_FILLING_FORM
        data["current_field_index"] = 0
        await save_conversation(session_id, data)
    
    @staticmethod
    async def transition_to_completed(session_id: str):
        """Transition to completed state"""
        data = await load_conversation(session_id)
        data["state"] = settings.STATE_COMPLETED
        await save_conversation(session_id, data)
    
    @staticmethod
    async def get_current_field(session_id: str) -> Tuple[Dict, int, int]:
        """Get the current field user needs to fill"""
        data = await load_conversation(session_id)
        form_id = data.get("matched_form_id")
        form = await get_form_by_id(form_id)
        
        if not form:
            raise Exception("Form not found")
        
        fields = form.get("fields", [])
        idx = data.get("current_field_index", 0)
        
        if idx >= len(fields):
            raise Exception("No more fields to fill")
        
        return fields[idx], idx, len(fields)
    
    @staticmethod
    async def save_answer(session_id: str, answer: str) -> bool:
        """
        Save user's answer for current field and move to next
        
        Returns:
            bool: True if more fields remain, False if form is complete
        """
        data = await load_conversation(session_id)
        form_id = data.get("matched_form_id")
        form = await get_form_by_id(form_id)
        
        if not form:
            return False
        
        fields = form.get("fields", [])
        idx = data.get("current_field_index", 0)
        
        if idx >= len(fields):
            return False
        
        field = fields[idx]
        
        # Initialize answers dict if not exists
        if "answers" not in data:
            data["answers"] = {}
        
        # Save answer with field metadata
        data["answers"][field["id"]] = {
            "label": field["label"],
            "answer": answer,
            "field_type": field.get("type", "text")
        }
        
        # Move to next field
        data["current_field_index"] = idx + 1
        await save_conversation(session_id, data)
        
        # Return whether more fields remain
        return idx + 1 < len(fields)
    
    @staticmethod
    async def update_specific_answer(session_id: str, field_id: str, new_answer: str) -> bool:
        """
        ✅ NEW: Update a specific field's answer without changing current position
        This allows users to correct previous answers naturally
        
        Args:
            session_id: User session ID
            field_id: ID of the field to update
            new_answer: New answer value
        
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            data = await load_conversation(session_id)
            form_id = data.get("matched_form_id")
            form = await get_form_by_id(form_id)
            
            if not form:
                return False
            
            # Find the field
            target_field = None
            for field in form.get("fields", []):
                if field.get("id") == field_id:
                    target_field = field
                    break
            
            if not target_field:
                return False
            
            # Initialize answers dict if needed
            if "answers" not in data:
                data["answers"] = {}
            
            # Update the specific answer
            data["answers"][field_id] = {
                "label": target_field["label"],
                "answer": new_answer,
                "field_type": target_field.get("type", "text"),
                "updated": True  # Mark as updated
            }
            
            # Save without changing current_field_index
            await save_conversation(session_id, data)
            
            print(f"✅ Updated answer for field: {target_field['label']}")
            print(f"   New answer: {new_answer}")
            
            return True
        
        except Exception as e:
            print(f"❌ Update specific answer failed: {e}")
            return False
    
    @staticmethod
    async def get_answer_history(session_id: str) -> Dict:
        """
        Get all answered fields with their values
        Useful for showing user what they've filled so far
        """
        data = await load_conversation(session_id)
        form_id = data.get("matched_form_id")
        
        if not form_id:
            return {}
        
        form = await get_form_by_id(form_id)
        if not form:
            return {}
        
        answers = data.get("answers", {})
        fields = form.get("fields", [])
        
        # Build structured answer history
        history = {}
        for field in fields:
            field_id = field.get("id")
            if field_id in answers:
                history[field_id] = {
                    "label": field.get("label"),
                    "answer": answers[field_id].get("answer"),
                    "field_type": field.get("type"),
                    "updated": answers[field_id].get("updated", False)
                }
        
        return history
    
    @staticmethod
    async def get_progress(session_id: str) -> Dict:
        """Get form filling progress"""
        data = await load_conversation(session_id)
        form_id = data.get("matched_form_id")
        
        if not form_id:
            return {
                "current_index": 0,
                "total_fields": 0,
                "percentage": 0.0,
                "answers_count": 0
            }
        
        form = await get_form_by_id(form_id)
        
        if not form:
            return {
                "current_index": 0,
                "total_fields": 0,
                "percentage": 0.0,
                "answers_count": 0
            }
        
        fields = form.get("fields", [])
        current_idx = data.get("current_field_index", 0)
        answers = data.get("answers", {})
        
        total = len(fields)
        percentage = (current_idx / total * 100) if total > 0 else 0
        
        return {
            "current_index": current_idx,
            "total_fields": total,
            "percentage": round(percentage, 2),
            "answers_count": len(answers)
        }
    
    @staticmethod
    async def reset_session(session_id: str):
        """Reset session to initial state"""
        data = await load_conversation(session_id)
        data["state"] = settings.STATE_CHATTING
        data["matched_form_id"] = None
        data["current_field_index"] = 0
        data["answers"] = {}
        data["history"] = []
        await save_conversation(session_id, data)