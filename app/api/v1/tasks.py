from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.ai.service import ai_service
from app.api.deps import get_db, get_current_user
from app.models.task import TaskStatus
from app.models.user import User
from app.schemas.ai import (
    GenerateDescriptionRequest,
    GenerateDescriptionResponse,
    SummarizeTaskResponse,
)
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskResponse,
    TaskListResponse,
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/generate-description",
    response_model=GenerateDescriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="AI: Generate Task Description (Option A)",
    description="Accepts a task title and uses AI to generate an actionable, structured description.",
)
def generate_task_description(
    req: GenerateDescriptionRequest,
    current_user: User = Depends(get_current_user),
):
    description = ai_service.generate_description(req.title)
    return GenerateDescriptionResponse(
        title=req.title,
        description=description,
        provider=ai_service.active_provider_name,
    )


@router.post(
    "/{id}/summarize",
    response_model=SummarizeTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="AI: Generate Task Summary (Option B)",
    description="Retrieves a task by ID and uses AI to generate a concise executive summary.",
)
def summarize_task(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = TaskService.get_task_by_id(db=db, task_id=id, current_user=current_user)
    summary = ai_service.summarize_task(title=task.title, description=task.description or "")
    return SummarizeTaskResponse(
        task_id=task.id,
        title=task.title,
        summary=summary,
        provider=ai_service.active_provider_name,
    )


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a new task owned by the authenticated user. Default status is 'Pending'.",
)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService.create_task(db=db, task_in=task_in, current_user=current_user)


@router.get(
    "/",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List tasks",
    description=(
        "Retrieve tasks. Regular users can only see their own tasks. "
        "Administrators can view all tasks and optionally filter by user_id."
    ),
)
def list_tasks(
    status: TaskStatus | None = Query(default=None, description="Filter by task status"),
    user_id: int | None = Query(default=None, description="Admin only: Filter by specific user ID"),
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=50, ge=1, le=100, description="Pagination limit"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks, total = TaskService.list_tasks(
        db=db,
        current_user=current_user,
        status=status,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )
    return TaskListResponse(total=total, tasks=tasks)


@router.get(
    "/{id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="View task by ID",
    description="Retrieve single task. Regular users can only view their own tasks.",
)
def get_task(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService.get_task_by_id(db=db, task_id=id, current_user=current_user)


@router.put(
    "/{id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task details",
    description=(
        "Update title and/or description. Regular users can only edit their own tasks. "
        "Note: Status updates must be made via the status endpoint and require admin role."
    ),
)
def update_task(
    id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService.update_task(
        db=db,
        task_id=id,
        task_in=task_in,
        current_user=current_user,
    )


@router.patch(
    "/{id}/status",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task status (Admin only)",
    description=(
        "Update task status to 'Pending', 'In Progress', 'Testing', or 'Completed'. "
        "Strictly restricted to Admin role. Regular users will receive 403 Forbidden."
    ),
)
def update_task_status_patch(
    id: int,
    status_in: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService.update_task_status(
        db=db,
        task_id=id,
        status_in=status_in,
        current_user=current_user,
    )


@router.put(
    "/{id}/status",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task status - PUT alias (Admin only)",
    description="PUT alias for updating task status (Admin only).",
)
def update_task_status_put(
    id: int,
    status_in: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService.update_task_status(
        db=db,
        task_id=id,
        status_in=status_in,
        current_user=current_user,
    )
