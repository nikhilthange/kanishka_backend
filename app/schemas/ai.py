from pydantic import BaseModel, Field


class GenerateDescriptionRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=255,
        examples=["Set up PostgreSQL database with Alembic migrations"],
        description="Task title for which AI will generate a structured description",
    )
    provider: str | None = Field(
        default=None,
        description="Optional LLM provider override ('gemini', 'openai', or 'mock')",
        examples=["gemini"],
    )


class GenerateDescriptionResponse(BaseModel):
    title: str
    description: str
    provider: str


class SummarizeTaskResponse(BaseModel):
    task_id: int
    title: str
    summary: str
    provider: str
