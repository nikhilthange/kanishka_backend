import logging
from app.ai.base import BaseAIProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.mock_provider import MockProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self._provider_name: str = settings.AI_PROVIDER.lower()
        self._provider: BaseAIProvider = self._resolve_provider()

    def _resolve_provider(self) -> BaseAIProvider:
        """Resolve and instantiate the configured AI provider with graceful fallback."""
        if self._provider_name == "gemini":
            if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
                try:
                    logger.info("Initializing Google Gemini AI provider.")
                    return GeminiProvider(
                        api_key=settings.GEMINI_API_KEY,
                        model_name=settings.GEMINI_MODEL,
                    )
                except Exception as e:
                    logger.warning(f"Failed to initialize Gemini provider ({e}). Falling back to MockProvider.")
            else:
                logger.info("No GEMINI_API_KEY detected. Using intelligent Mock AI provider.")
            self._provider_name = "mock"
            return MockProvider()

        elif self._provider_name == "openai":
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
                try:
                    logger.info("Initializing OpenAI provider.")
                    return OpenAIProvider(
                        api_key=settings.OPENAI_API_KEY,
                        model_name=settings.OPENAI_MODEL,
                    )
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI provider ({e}). Falling back to MockProvider.")
            else:
                logger.info("No OPENAI_API_KEY detected. Using intelligent Mock AI provider.")
            self._provider_name = "mock"
            return MockProvider()

        else:
            self._provider_name = "mock"
            return MockProvider()

    @property
    def active_provider_name(self) -> str:
        return self._provider_name

    def generate_description(self, title: str) -> str:
        """Generate a description using the active AI provider."""
        return self._provider.generate_description(title)

    def summarize_task(self, title: str, description: str) -> str:
        """Generate a summary using the active AI provider."""
        return self._provider.summarize_task(title, description)


ai_service = AIService()
