"""
Test configuration and shared fixtures for FighterIA backend test suite.
"""
import pathlib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.utils.security import hash_password, create_access_token

TEST_DB_URL = "sqlite:///./test_fighterai.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables once per session; seed with discipline/technique data."""
    Base.metadata.create_all(bind=engine)

    # Temporarily redirect the app's DB module to the test engine so seed works
    from app import database as db_module
    original_engine = db_module.engine
    original_session = db_module.SessionLocal
    db_module.engine = engine
    db_module.SessionLocal = TestingSessionLocal

    try:
        from seed.seed_data import run_seed
        run_seed()
    except Exception:
        # Seed is best-effort; tests must not depend on seeded data unless explicit
        pass

    db_module.engine = original_engine
    db_module.SessionLocal = original_session

    yield

    Base.metadata.drop_all(bind=engine)
    pathlib.Path("./test_fighterai.db").unlink(missing_ok=True)


@pytest.fixture(scope="function")
def db():
    """
    Provide an isolated DB session per test using a savepoint rollback strategy.
    Each test gets a clean slate without recreating tables.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    """Test client that overrides the DB dependency to use the per-test session."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a standard alumno test user with a known password."""
    user = User(
        email="testfighter@example.com",
        username="testfighter",
        password_hash=hash_password("TestPass123!"),
        full_name="Test Fighter",
        account_type="alumno",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def test_instructor(db):
    """Create a test instructor user with a known password."""
    user = User(
        email="instructor@example.com",
        username="sensei_test",
        password_hash=hash_password("InstructorPass123!"),
        full_name="Test Instructor",
        account_type="instructor",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def auth_headers(test_user):
    """Return Authorization headers for the alumno test user."""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def instructor_headers(test_instructor):
    """Return Authorization headers for the instructor test user."""
    token = create_access_token({"sub": str(test_instructor.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user(db):
    """Create a second alumno for tests that require multiple users."""
    user = User(
        email="fighter2@example.com",
        username="fighter2",
        password_hash=hash_password("Fighter2Pass123!"),
        full_name="Second Fighter",
        account_type="alumno",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def sample_video_bytes():
    """Return minimal fake video bytes for upload endpoint testing."""
    return b"FAKE_MP4_CONTENT_FOR_TESTING_ONLY"
