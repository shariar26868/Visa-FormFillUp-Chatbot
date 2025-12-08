"""
OpenAI Chat & Vision Service
"""

from typing import List, Dict
from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def call_openai_chat(
    messages: List[Dict],
    system_prompt: str = None,
    temperature: float = 0.9,
    max_tokens: int = 500
) -> str:
    try:
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend(messages)
        
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ OpenAI Chat failed: {e}")
        raise Exception(f"AI error: {str(e)}")

async def call_openai_with_image(
    text_prompt: str,
    base64_image: str,
    temperature: float = 0.1,
    max_tokens: int = 2000
) -> str:
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Vision API failed: {e}")
        raise Exception(f"Vision error: {str(e)}")

