import logging
import google.generativeai as genai
from app.ai.base import BaseAIProvider
from app.core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI integration."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

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
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                raise AIServiceException(detail="Gemini API returned an empty response.")
            return response.text.strip()
        except AIServiceException:
            raise
        except Exception as e:
            logger.error(f"Gemini API error during description generation: {e}", exc_info=True)
            raise AIServiceException(detail=f"Gemini API call failed: {str(e)}")

    def summarize_task(self, title: str, description: str) -> str:
        prompt = (
            f"You are a helpful project manager. Provide a concise, 2-3 sentence executive summary "
            f"of the following task:\n\n"
            f"Title: {title}\n"
            f"Description: {description or 'No description provided.'}\n\n"
            f"Summary:"
        )
        try:
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                raise AIServiceException(detail="Gemini API returned an empty summary response.")
            return response.text.strip()
        except AIServiceException:
            raise
        except Exception as e:
            logger.error(f"Gemini API error during task summarization: {e}", exc_info=True)
            raise AIServiceException(detail=f"Gemini API call failed: {str(e)}")
