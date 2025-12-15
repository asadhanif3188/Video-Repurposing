from app.core.config import settings
from app.services.ai.base import AIProvider

def get_ai_provider() -> AIProvider:
    """
    Factory function to get the configured AI provider instance.
    Defaults to OpenAI if not specified or unrecognized.
    Uses local imports to avoid hard dependency requirements if a provider is unused.
    """
    
    if settings.USE_MOCK_AI:
        from app.services.ai.mock_provider import MockProvider
        return MockProvider()

    provider_name = settings.AI_PROVIDER.lower()
    
    if provider_name == "gemini":
        from app.services.ai.gemini_provider import GeminiProvider
        return GeminiProvider()
    
    # Default to OpenAI
    from app.services.ai.openai_provider import OpenAIProvider
    return OpenAIProvider()
