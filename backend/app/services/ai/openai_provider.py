import json
from typing import Any, Dict, List
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.prompts import EXTRACT_ATOMS_PROMPT, REWRITE_CONTENT_PROMPT, REPURPOSE_METADATA_PROMPT

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def extract_atoms(self, text: str) -> List[Dict[str, str]]:
        """
        Extract structured content atoms from transcript using OpenAI.
        """
        # Truncate text to avoid token limits if necessary, though ideally we handle this upstream
        truncated_text = text[:15000] 
        prompt = EXTRACT_ATOMS_PROMPT.format(transcript_text=truncated_text)

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106", # Cost effective JSON mode support
                messages=[
                    {"role": "system", "content": "You are an expert content strategist."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                return []
                
            data = json.loads(content)
            return data.get("atoms", [])
            
        except Exception as e:
            print(f"Error extracting atoms from OpenAI: {e}")
            raise e

    async def extract_atoms_from_metadata(self, metadata: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Extract atoms from metadata using OpenAI.
        """
        prompt = REPURPOSE_METADATA_PROMPT.format(
            title=metadata.get("title", ""),
            channel=metadata.get("channel_name", ""),
            description=metadata.get("description", "")
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": "You are an expert content strategist."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                return []
                
            data = json.loads(content)
            return data.get("atoms", [])
            
        except Exception as e:
            print(f"Error extracting atoms from metadata: {e}")
            raise e

    async def rewrite_for_platform(self, text: str, platform: str) -> str:
        """
        Rewrite content for a specific platform using OpenAI.
        """
        if platform == "twitter":
            style_guide = "concise, punchy, under 280 characters, use hashtags if appropriate"
        elif platform == "linkedin":
            style_guide = "professional, story-like, engaging, use formatting"
        else:
            style_guide = "professional and clear"

        prompt = REWRITE_CONTENT_PROMPT.format(platform=platform, style_guide=style_guide, text=text)

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an expert {platform} content creator."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip() if response.choices[0].message.content else text
        except Exception as e:
            print(f"Error rewriting for {platform}: {e}")
            return text # Fallback to original text
