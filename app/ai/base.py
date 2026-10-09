from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    """Abstract base class defining the contract for AI providers."""

    @abstractmethod
    def generate_description(self, title: str) -> str:
        """Generate a structured, actionable task description based on a title."""
        pass

    @abstractmethod
    def summarize_task(self, title: str, description: str) -> str:
        """Generate a concise executive summary from a task's title and description."""
        pass
