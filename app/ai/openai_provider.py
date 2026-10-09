import logging
from openai import OpenAI, OpenAIError
from app.ai.base import BaseAIProvider
from app.core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """OpenAI API integration (e.g. GPT-4o-mini)."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = OpenAI(api_key=self.api_key)

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
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert technical project assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            content = response.choices[0].message.content
            if not content:
                raise AIServiceException(detail="OpenAI returned an empty description.")
            return content.strip()
        except AIServiceException:
            raise
        except OpenAIError as e:
            logger.error(f"OpenAI error during description generation: {e}", exc_info=True)
            raise AIServiceException(detail=f"OpenAI API call failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI provider: {e}", exc_info=True)
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
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a concise executive summarizer."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=250,
                temperature=0.5,
            )
            content = response.choices[0].message.content
            if not content:
                raise AIServiceException(detail="OpenAI returned an empty summary.")
            return content.strip()
        except AIServiceException:
            raise
        except OpenAIError as e:
            logger.error(f"OpenAI error during summarization: {e}", exc_info=True)
            raise AIServiceException(detail=f"OpenAI API call failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI provider: {e}", exc_info=True)
            raise AIServiceException(detail=f"AI service error: {str(e)}")
