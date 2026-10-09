from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.task import TaskStatus
from app.schemas.user import UserResponse


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, examples=["Build Authentication System"])
    description: str | None = Field(default=None, examples=["Implement JWT auth with user and admin roles"])


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None)
    # Note: status is intentionally separate or restricted to Admin in service layer


class TaskStatusUpdate(BaseModel):
    status: TaskStatus = Field(
        ...,
        description="Task status must be one of: 'Pending', 'In Progress', 'Testing', 'Completed'",
        examples=["In Progress"],
    )


class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    owner: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    total: int
    tasks: list[TaskResponse]
