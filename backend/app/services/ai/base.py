from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    """

    @abstractmethod
    async def extract_atoms(self, text: str) -> Any:
        """
        Extract atomic ideas or segments from the text.
        
        Args:
            text (str): The input text to process.
            
        Returns:
            Any: The extracted atoms. Return type depends on implementation.
        """
        pass

    @abstractmethod
    async def rewrite_for_platform(self, text: str, platform: str) -> str:
        """
        Rewrite the text for a specific social media platform.
        
        Args:
            text (str): The text to rewrite.
            platform (str): The target platform (e.g., 'twitter', 'linkedin').
            
        Returns:
            str: The rewritten text.
        """
        pass
