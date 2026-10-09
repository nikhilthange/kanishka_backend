import logging
from anthropic import Anthropic, APIError
from app.ai.base import BaseAIProvider
from app.core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude AI integration (e.g., Claude 3.5 Sonnet / Claude 3 Haiku)."""

    def __init__(self, api_key: str, model_name: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = Anthropic(api_key=self.api_key)

    def generate_description(self, title: str) -> str:
        prompt = (
            f"You are a professional project management assistant. "
            f"Generate a clear, structured, and actionable task description for the following task title: '{title}'.\n\n"
            f"Include:\n"
            f"- Objective\n"
            f"- Key Deliverables / Action Steps\n"
            f"- Acceptance Criteria\n"
            f"Keep the output professional, concise, and ready for development tracking."
        )
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            if not message.content:
                raise AIServiceException(detail="Anthropic returned an empty description.")
            return message.content[0].text.strip()
        except AIServiceException:
            raise
        except APIError as e:
            logger.error(f"Anthropic API error during description generation: {e}", exc_info=True)
            raise AIServiceException(detail=f"Anthropic API call failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Anthropic provider: {e}", exc_info=True)
            raise AIServiceException(detail=f"AI service error: {str(e)}")

    def summarize_task(self, title: str, description: str) -> str:
        prompt = (
            f"You are a helpful project manager. Provide a concise, 2-3 sentence executive summary "
            f"of the following task:\n\n"
            f"Title: {title}\n"
            f"Description: {description or 'No description provided.'}\n\n"
            f"Summary:"
        )
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=250,
                messages=[{"role": "user", "content": prompt}],
            )
            if not message.content:
                raise AIServiceException(detail="Anthropic returned an empty summary.")
            return message.content[0].text.strip()
        except AIServiceException:
            raise
        except APIError as e:
            logger.error(f"Anthropic API error during summarization: {e}", exc_info=True)
            raise AIServiceException(detail=f"Anthropic API call failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Anthropic provider: {e}", exc_info=True)
            raise AIServiceException(detail=f"AI service error: {str(e)}")
