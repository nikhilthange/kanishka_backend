import sys
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.auth.jwt_handler import hash_password
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models.task import Task, TaskStatus
from app.models.user import User, UserRole


def seed_database(db: Session | None = None) -> None:
    """Seed the database with initial users and tasks."""
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        # Check if already seeded
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_admin:
            print("Database already contains seed data. Skipping seed process.")
            return

        print("Seeding Users...")
        # 1. Admin User
        admin_user = User(
            name="Administrator",
            email="admin@example.com",
            password=hash_password("AdminPass123!"),
            role=UserRole.ADMIN.value,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # 2. Regular User 1
        user_1 = User(
            name="Alice Johnson",
            email="user1@example.com",
            password=hash_password("UserPass123!"),
            role=UserRole.USER.value,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # 3. Regular User 2
        user_2 = User(
            name="Bob Smith",
            email="user2@example.com",
            password=hash_password("UserPass123!"),
            role=UserRole.USER.value,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        db.add_all([admin_user, user_1, user_2])
        db.commit()
        db.refresh(admin_user)
        db.refresh(user_1)
        db.refresh(user_2)

        print(f"Users created: Admin (id={admin_user.id}), Alice (id={user_1.id}), Bob (id={user_2.id})")

        print("Seeding Tasks...")
        sample_tasks = [
            Task(
                user_id=user_1.id,
                title="Setup FastAPI Architecture",
                description="Configure FastAPI application structure with routers, dependencies, and settings.",
                status=TaskStatus.COMPLETED.value,
            ),
            Task(
                user_id=user_1.id,
                title="Implement JWT Authentication",
                description="Create secure token generation and validation middleware with role checking.",
                status=TaskStatus.IN_PROGRESS.value,
            ),
            Task(
                user_id=user_1.id,
                title="Integrate AI Description Generator",
                description="Connect LLM service to automatically generate actionable task descriptions.",
                status=TaskStatus.PENDING.value,
            ),
            Task(
                user_id=user_2.id,
                title="Write Comprehensive Postman Collection",
                description="Create automated Postman test scenarios verifying RBAC and AI endpoints.",
                status=TaskStatus.TESTING.value,
            ),
            Task(
                user_id=user_2.id,
                title="Configure Database Migrations",
                description="Implement Alembic migration scripts and test rollback procedures.",
                status=TaskStatus.PENDING.value,
            ),
            Task(
                user_id=admin_user.id,
                title="System Infrastructure & Security Audit",
                description="Verify environment variables protection, CORS security, and database connection pooling.",
                status=TaskStatus.IN_PROGRESS.value,
            ),
        ]

        db.add_all(sample_tasks)
        db.commit()
        print(f"Successfully seeded {len(sample_tasks)} tasks.")
        print("\nSeed Completed Successfully!")
        print("--------------------------------------------------")
        print("Admin Credentials:  admin@example.com / AdminPass123!")
        print("User 1 Credentials: user1@example.com / UserPass123!")
        print("User 2 Credentials: user2@example.com / UserPass123!")
        print("--------------------------------------------------")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}", file=sys.stderr)
        raise
    finally:
        if close_session:
            db.close()


if __name__ == "__main__":
    seed_database()
