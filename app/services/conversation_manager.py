# # """
# # Conversation State Management
# # """

# # from typing import Tuple, Dict, Optional
# # from app.core.storage import load_conversation, save_conversation, get_form_by_id
# # from app.core.config import settings

# # class ConversationManager:
    
# #     @staticmethod
# #     def transition_to_form_matched(session_id: str, form_id: str):
# #         data = load_conversation(session_id)
# #         data["state"] = settings.STATE_FORM_MATCHED
# #         data["matched_form_id"] = form_id
# #         data["current_field_index"] = 0
# #         data["answers"] = {}
# #         save_conversation(session_id, data)
    
# #     @staticmethod
# #     def transition_to_filling_form(session_id: str):
# #         data = load_conversation(session_id)
# #         data["state"] = settings.STATE_FILLING_FORM
# #         data["current_field_index"] = 0
# #         save_conversation(session_id, data)
    
# #     @staticmethod
# #     def transition_to_completed(session_id: str):
# #         data = load_conversation(session_id)
# #         data["state"] = settings.STATE_COMPLETED
# #         save_conversation(session_id, data)
    
# #     @staticmethod
# #     def get_current_field(session_id: str) -> Tuple[Dict, int, int]:
# #         data = load_conversation(session_id)
# #         form_id = data.get("matched_form_id")
# #         form = get_form_by_id(form_id)
        
# #         if not form:
# #             raise Exception("Form not found")
        
# #         fields = form.get("fields", [])
# #         idx = data.get("current_field_index", 0)
        
# #         if idx >= len(fields):
# #             raise Exception("No more fields")
        
# #         return fields[idx], idx, len(fields)
    
# #     @staticmethod
# #     def save_answer(session_id: str, answer: str) -> bool:
# #         data = load_conversation(session_id)
# #         form_id = data.get("matched_form_id")
# #         form = get_form_by_id(form_id)
        
# #         fields = form.get("fields", [])
# #         idx = data.get("current_field_index", 0)
        
# #         if idx >= len(fields):
# #             return False
        
# #         field = fields[idx]
        
# #         if "answers" not in data:
# #             data["answers"] = {}
        
# #         data["answers"][field["id"]] = {
# #             "label": field["label"],
# #             "answer": answer
# #         }
        
# #         data["current_field_index"] = idx + 1
# #         save_conversation(session_id, data)
        
# #         return idx + 1 < len(fields)




# from typing import Tuple, Dict
# from app.core.storage import load_conversation, save_conversation, get_form_by_id
# from app.core.config import settings


# class ConversationManager:
    
#     @staticmethod
#     async def transition_to_form_matched(session_id: str, form_id: str):
#         data = await load_conversation(session_id)
#         data["state"] = settings.STATE_FORM_MATCHED
#         data["matched_form_id"] = form_id
#         data["current_field_index"] = 0
#         data["answers"] = {}        # Keep original logic
#         await save_conversation(session_id, data)
    
#     @staticmethod
#     async def transition_to_filling_form(session_id: str):
#         data = await load_conversation(session_id)
#         data["state"] = settings.STATE_FILLING_FORM
#         data["current_field_index"] = 0
#         await save_conversation(session_id, data)
    
#     @staticmethod
#     async def transition_to_completed(session_id: str):
#         data = await load_conversation(session_id)
#         data["state"] = settings.STATE_COMPLETED
#         await save_conversation(session_id, data)
    
#     @staticmethod
#     async def get_current_field(session_id: str) -> Tuple[Dict, int, int]:
#         data = await load_conversation(session_id)
#         form_id = data.get("matched_form_id")
#         form = await get_form_by_id(form_id)
        
#         if not form:
#             raise Exception("Form not found")
        
#         fields = form.get("fields", [])
#         idx = data.get("current_field_index", 0)
        
#         if idx >= len(fields):
#             raise Exception("No more fields")
        
#         return fields[idx], idx, len(fields)
    
#     @staticmethod
#     async def save_answer(session_id: str, answer: str) -> bool:
#         data = await load_conversation(session_id)
#         form_id = data.get("matched_form_id")
#         form = await get_form_by_id(form_id)
        
#         fields = form.get("fields", [])
#         idx = data.get("current_field_index", 0)
        
#         if idx >= len(fields):
#             return False
        
#         field = fields[idx]

#         # Preserve original logic
#         if "answers" not in data:
#             data["answers"] = {}

#         data["answers"][field["id"]] = {
#             "label": field["label"],
#             "answer": answer
#         }

#         data["current_field_index"] = idx + 1
#         await save_conversation(session_id, data)
        
#         # Return whether more fields remain
#         return idx + 1 < len(fields)




"""
Conversation State Management
✅ FULLY ASYNC: All functions properly await storage operations
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
        """
        Transition to form matched state
        User has been matched with a form, waiting for confirmation
        """
        data = await load_conversation(session_id)
        data["state"] = settings.STATE_FORM_MATCHED
        data["matched_form_id"] = form_id
        data["current_field_index"] = 0
        data["answers"] = {}
        await save_conversation(session_id, data)
    
    @staticmethod
    async def transition_to_filling_form(session_id: str):
        """
        Transition to filling form state
        User confirmed and started filling the form
        """
        data = await load_conversation(session_id)
        data["state"] = settings.STATE_FILLING_FORM
        data["current_field_index"] = 0
        await save_conversation(session_id, data)
    
    @staticmethod
    async def transition_to_completed(session_id: str):
        """
        Transition to completed state
        User finished filling all fields
        """
        data = await load_conversation(session_id)
        data["state"] = settings.STATE_COMPLETED
        await save_conversation(session_id, data)
    
    @staticmethod
    async def get_current_field(session_id: str) -> Tuple[Dict, int, int]:
        """
        Get the current field user needs to fill
        
        Returns:
            Tuple[Dict, int, int]: (field_dict, current_index, total_fields)
        
        Raises:
            Exception: If form not found or no more fields
        """
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
        
        Args:
            session_id: User session ID
            answer: User's answer text
        
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
    async def get_progress(session_id: str) -> Dict:
        """
        Get form filling progress
        
        Returns:
            Dict with: current_index, total_fields, percentage, answers_count
        """
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
        """
        Reset session to initial state
        Useful for starting over or handling errors
        """
        data = await load_conversation(session_id)
        data["state"] = settings.STATE_CHATTING
        data["matched_form_id"] = None
        data["current_field_index"] = 0
        data["answers"] = {}
        data["history"] = []
        await save_conversation(session_id, data)