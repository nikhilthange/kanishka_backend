from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.exceptions import EntityNotFoundException, ForbiddenException
from app.models.task import Task, TaskStatus
from app.models.user import User, UserRole
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate


class TaskService:
    @staticmethod
    def create_task(db: Session, task_in: TaskCreate, current_user: User) -> Task:
        """Create a new task assigned to the authenticated user."""
        task = Task(
            user_id=current_user.id,
            title=task_in.title.strip(),
            description=task_in.description.strip() if task_in.description else None,
            status=TaskStatus.PENDING.value,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def list_tasks(
        db: Session,
        current_user: User,
        status: TaskStatus | None = None,
        user_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Task], int]:
        """
        List tasks according to role permissions.
        - Regular User: only sees their own tasks.
        - Admin: can see all tasks or filter by user_id and status.
        """
        query = db.query(Task)

        if current_user.role == UserRole.USER.value:
            # Regular users strictly restricted to their own tasks
            query = query.filter(Task.user_id == current_user.id)
        else:
            # Admin can optionally filter by specific user_id
            if user_id is not None:
                query = query.filter(Task.user_id == user_id)

        if status is not None:
            query = query.filter(Task.status == status.value)

        total = query.count()
        tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
        return tasks, total

    @staticmethod
    def get_task_by_id(db: Session, task_id: int, current_user: User) -> Task:
        """
        Retrieve a task by ID.
        - Regular user: cannot view another user's task (raises 403).
        - Admin: can view any task.
        """
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise EntityNotFoundException(detail=f"Task with ID {task_id} not found.")

        if current_user.role == UserRole.USER.value and task.user_id != current_user.id:
            raise ForbiddenException(detail="Access denied: You cannot view tasks belonging to other users.")

        return task

    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        task_in: TaskUpdate,
        current_user: User,
    ) -> Task:
        """
        Update task title and/or description.
        - Regular User: can only edit own tasks (403 if editing another user's task).
        - Admin: can edit any task.
        """
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise EntityNotFoundException(detail=f"Task with ID {task_id} not found.")

        if current_user.role == UserRole.USER.value and task.user_id != current_user.id:
            raise ForbiddenException(detail="Access denied: You cannot modify tasks belonging to other users.")

        if task_in.title is not None:
            task.title = task_in.title.strip()
        if task_in.description is not None:
            task.description = task_in.description.strip()
        if task_in.status is not None:
            if current_user.role != UserRole.ADMIN.value:
                raise ForbiddenException(
                    detail="Access denied: Regular users are not authorized to update task status. "
                           "Only administrators can update task status."
                )
            task.status = task_in.status.value

        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task_status(
        db: Session,
        task_id: int,
        status_in: TaskStatusUpdate,
        current_user: User,
    ) -> Task:
        """
        Update task status.
        - Strict RBAC Rule: Only Admin can update task status.
        - Regular Users attempting to update task status receive 403 Forbidden.
        """
        if current_user.role != UserRole.ADMIN.value:
            raise ForbiddenException(
                detail="Access denied: Regular users are not authorized to update task status. "
                       "Only administrators can update task status."
            )

        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise EntityNotFoundException(detail=f"Task with ID {task_id} not found.")

        task.status = status_in.status.value
        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)
        return task
