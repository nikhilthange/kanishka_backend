import pytest
from collections.abc import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.auth.jwt_handler import hash_password, create_access_token
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.task import Task, TaskStatus
from app.models.user import User, UserRole

# Use an in-memory SQLite database for isolated test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_users(db_session: Session) -> dict[str, User]:
    """Create test users in database and return them."""
    admin = User(
        name="Admin Test",
        email="admin@test.com",
        password=hash_password("AdminSecret123!"),
        role=UserRole.ADMIN.value,
    )
    user1 = User(
        name="User One",
        email="user1@test.com",
        password=hash_password("UserOneSecret123!"),
        role=UserRole.USER.value,
    )
    user2 = User(
        name="User Two",
        email="user2@test.com",
        password=hash_password("UserTwoSecret123!"),
        role=UserRole.USER.value,
    )
    db_session.add_all([admin, user1, user2])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(user1)
    db_session.refresh(user2)

    return {"admin": admin, "user1": user1, "user2": user2}


@pytest.fixture
def auth_headers(test_users: dict[str, User]) -> dict[str, dict[str, str]]:
    """Generate authorization headers with Bearer tokens for each test user."""
    headers = {}
    for key, user in test_users.items():
        token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        headers[key] = {"Authorization": f"Bearer {token}"}
    return headers


@pytest.fixture
def sample_tasks(db_session: Session, test_users: dict[str, User]) -> list[Task]:
    """Create sample tasks in the test database."""
    t1 = Task(
        user_id=test_users["user1"].id,
        title="User1 Task 1",
        description="First task description for user 1",
        status=TaskStatus.PENDING.value,
    )
    t2 = Task(
        user_id=test_users["user1"].id,
        title="User1 Task 2",
        description="Second task description for user 1",
        status=TaskStatus.IN_PROGRESS.value,
    )
    t3 = Task(
        user_id=test_users["user2"].id,
        title="User2 Task 1",
        description="First task description for user 2",
        status=TaskStatus.TESTING.value,
    )
    db_session.add_all([t1, t2, t3])
    db_session.commit()
    db_session.refresh(t1)
    db_session.refresh(t2)
    db_session.refresh(t3)
    return [t1, t2, t3]
