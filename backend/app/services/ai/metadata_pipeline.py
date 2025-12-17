from typing import Dict, List, Any
from app.services.ai_service import AIService

class MetadataPipeline:
    def __init__(self):
        self.ai_service = AIService()

    async def generate_content_from_metadata(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate content atoms based on video metadata.
        
        Args:
            metadata (Dict): dictionary containing 'title', 'description', 'channel_name'.
            
        Returns:
            List[Dict]: List of content atoms with 'type' and 'text'.
        """
        # 1. Extract atoms using the metadata strategy
        # Delegates to the configured AI provider via AIService
        # Note: We need to ensure AIService exposes this method or accesses provider directly.
        # AIService currently wraps provider calls. We should add a wrapper there too or access provider.
        # Best practice: Add wrapper to AIService.
        
        input_meta = {
            "title": metadata.get("title", ""),
            "description": metadata.get("description", ""),
            "channel_name": metadata.get("channel_name", "")
        }
        
        # Call the provider directly if AIService wrapper not present, 
        # BUT good practice is to update AIService. 
        # I will assume I updated AIService in the next step or access provider directly here.
        # Accessing provider directly:
        atoms = await self.ai_service.provider.extract_atoms_from_metadata(input_meta)
        
        return atoms
