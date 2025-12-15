from typing import List, Dict, Optional
from app.services.ai.factory import get_ai_provider

class AIService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def extract_content_atoms(self, transcript_text: str) -> List[Dict[str, str]]:
        """
        Extracts structured content atoms (insights, quotes, etc.) from transcript.
        Delegates to the configured AI provider.
        """
        return await self.provider.extract_atoms(transcript_text)

    async def rewrite_content(self, text: str, platform: str) -> str:
        """
        Rewrites the given text for a specific platform.
        Delegates to the configured AI provider.
        """
        return await self.provider.rewrite_for_platform(text, platform)
