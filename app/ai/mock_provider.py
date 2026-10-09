from app.ai.base import BaseAIProvider


class MockProvider(BaseAIProvider):
    """
    Mock AI Provider used when no external API key is provided,
    during offline automated tests, or for demo/bench evaluation.
    """

    def generate_description(self, title: str) -> str:
        return (
            f"### Task Overview: {title}\n\n"
            f"**Objective:** Successfully implement and deliver '{title}' according to quality specifications.\n\n"
            f"**Action Steps:**\n"
            f"1. Conduct architectural review and requirement analysis for '{title}'.\n"
            f"2. Implement core business logic, schema migrations, and REST endpoints.\n"
            f"3. Write comprehensive unit and integration tests.\n"
            f"4. Verify RBAC permissions and security safeguards.\n\n"
            f"**Acceptance Criteria:**\n"
            f"- Fully operational API endpoint with validation.\n"
            f"- Proper error handling and status codes.\n"
            f"- Passes all regression test suites."
        )

    def summarize_task(self, title: str, description: str) -> str:
        clean_desc = (description or "").strip()
        first_line = clean_desc.split("\n")[0] if clean_desc else "No detailed description."
        return (
            f"Executive Summary: Task '{title}' focuses on delivering core requirements. "
            f"Primary focus: {first_line[:120]}. Ready for milestone tracking."
        )
