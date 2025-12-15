import asyncio
from typing import Any, Dict, List
from app.services.ai.base import AIProvider

class MockProvider(AIProvider):
    async def extract_atoms(self, text: str) -> List[Dict[str, str]]:
        """
        Return static mock data for extraction.
        """
        print("⚠️ Using MOCK AI for extraction")
        await asyncio.sleep(1) # Simulate delay
        return [
            {"type": "insight", "text": "This is a mock insight from the video transcript."},
            {"type": "quote", "text": "This is a mock quote that sounds very inspiring."},
            {"type": "lesson", "text": "This is a mock lesson regarding the content strategy."},
            {"type": "opinion", "text": "This is a mock opinion about the subject matter."}
        ]

    async def rewrite_for_platform(self, text: str, platform: str) -> str:
        """
        Return simple mock rewritten text.
        """
        # print(f"⚠️ Using MOCK AI for rewriting {platform}")
        return f"[MOCK {platform.upper()}] {text}"
