import logging
from app.ai.base import BaseAIProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.anthropic_provider import AnthropicProvider
from app.ai.mock_provider import MockProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """
    Pluggable AI Service manager supporting dynamic provider selection,
    connection caching, and graceful offline fallback.
    """

    def __init__(self):
        self._cache: dict[str, BaseAIProvider] = {}

    def get_provider(self, provider_name: str | None = None) -> tuple[BaseAIProvider, str]:
        """Resolve and retrieve an AI provider instance."""
        target = (provider_name or settings.AI_PROVIDER).lower().strip()

        if target == "gemini":
            if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
                if "gemini" not in self._cache:
                    try:
                        self._cache["gemini"] = GeminiProvider(
                            api_key=settings.GEMINI_API_KEY,
                            model_name=settings.GEMINI_MODEL,
                        )
                    except Exception as e:
                        logger.warning(f"Could not initialize Gemini ({e}). Falling back to Mock.")
                        return self._get_mock_provider(), "mock"
                return self._cache["gemini"], "gemini"
            return self._get_mock_provider(), "mock (Gemini API key not configured)"

        elif target == "openai":
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
                if "openai" not in self._cache:
                    try:
                        self._cache["openai"] = OpenAIProvider(
                            api_key=settings.OPENAI_API_KEY,
                            model_name=settings.OPENAI_MODEL,
                        )
                    except Exception as e:
                        logger.warning(f"Could not initialize OpenAI ({e}). Falling back to Mock.")
                        return self._get_mock_provider(), "mock"
                return self._cache["openai"], "openai"
            return self._get_mock_provider(), "mock (OpenAI API key not configured)"

        elif target == "anthropic":
            if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip():
                if "anthropic" not in self._cache:
                    try:
                        self._cache["anthropic"] = AnthropicProvider(
                            api_key=settings.ANTHROPIC_API_KEY,
                            model_name=settings.ANTHROPIC_MODEL,
                        )
                    except Exception as e:
                        logger.warning(f"Could not initialize Anthropic ({e}). Falling back to Mock.")
                        return self._get_mock_provider(), "mock"
                return self._cache["anthropic"], "anthropic"
            return self._get_mock_provider(), "mock (Anthropic API key not configured)"

        else:
            return self._get_mock_provider(), "mock"

    def _get_mock_provider(self) -> BaseAIProvider:
        if "mock" not in self._cache:
            self._cache["mock"] = MockProvider()
        return self._cache["mock"]

    @property
    def active_provider_name(self) -> str:
        _, name = self.get_provider()
        return name

    def generate_description(self, title: str, provider_name: str | None = None) -> tuple[str, str]:
        """Generate a description, returning (description_text, active_provider_name)."""
        provider, resolved_name = self.get_provider(provider_name)
        desc = provider.generate_description(title)
        return desc, resolved_name

    def summarize_task(self, title: str, description: str, provider_name: str | None = None) -> tuple[str, str]:
        """Generate a summary, returning (summary_text, active_provider_name)."""
        provider, resolved_name = self.get_provider(provider_name)
        summary = provider.summarize_task(title, description)
        return summary, resolved_name


ai_service = AIService()
