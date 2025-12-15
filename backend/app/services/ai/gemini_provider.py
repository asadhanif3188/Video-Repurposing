import json
import google.generativeai as genai
from typing import Any, Dict, List
from app.core.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.prompts import EXTRACT_ATOMS_PROMPT, REWRITE_CONTENT_PROMPT

class GeminiProvider(AIProvider):
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def extract_atoms(self, text: str) -> List[Dict[str, str]]:
        """
        Extract structured content atoms from transcript using Gemini.
        """
        prompt = EXTRACT_ATOMS_PROMPT.format(transcript_text=text[:30000]) # Example larger context window if needed

        try:
            # Gemini 1.5 Flash supports JSON mode via generation_config
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
            
            # Using generate_content_async if available, else standard wrapper
            # The SDK might not have an async method directly on the model instance in all versions, 
            # but wrapping in executor or assuming async support if checking docs. 
            # Version 0.8.3+ usually supports async.
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            content = response.text
            if not content:
                return []
                
            data = json.loads(content)
            return data.get("atoms", [])
            
        except Exception as e:
            print(f"Error extracting atoms from Gemini: {e}")
            raise e

    async def rewrite_for_platform(self, text: str, platform: str) -> str:
        """
        Rewrite content for a specific platform using Gemini.
        """
        if platform == "twitter":
            style_guide = "concise, punchy, under 280 characters, use hashtags if appropriate"
        elif platform == "linkedin":
            style_guide = "professional, story-like, engaging, use formatting"
        else:
            style_guide = "professional and clear"

        prompt = REWRITE_CONTENT_PROMPT.format(platform=platform, style_guide=style_guide, text=text)

        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip() if response.text else text
        except Exception as e:
            print(f"Error rewriting for {platform}: {e}")
            return text
