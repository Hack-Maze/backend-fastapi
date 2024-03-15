import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from starlette import status

from app import crud
from app.core.config import settings
from app.main import app
from app.models import UserCreateOpen


# Fixture for the FastAPI test client
@pytest.fixture
def client():
    with TestClient(app=app) as ac:
        yield ac


# get a mock database


# Fixture for the database session
@pytest.fixture
def session() -> Session:
    # Create a mock or real database session here
    pass


# Fixture to override settings for testing
@pytest.fixture
def override_settings():
    original_value = settings.USERS_OPEN_REGISTRATION
    settings.USERS_OPEN_REGISTRATION = True
    yield
    settings.USERS_OPEN_REGISTRATION = original_value


# Parametrized test cases
@pytest.mark.parametrize(
    "user_in, expected_status, test_id",
    [
        # Happy path tests
        (
            UserCreateOpen(email="test@example.com", password="strongpassword"),
            status.HTTP_200_OK,
            "happy_path_1",
        ),
        (
            UserCreateOpen(
                email="unique@example.com", password="anotherstrongpassword"
            ),
            status.HTTP_200_OK,
            "happy_path_2",
        ),
        # Edge cases
        # Add edge cases here if applicable
        # Error cases
        (
            UserCreateOpen(email="existing@example.com", password="password"),
            status.HTTP_400_BAD_REQUEST,
            "error_existing_user",
        ),
        (
            UserCreateOpen(email="forbidden@example.com", password="password"),
            status.HTTP_403_FORBIDDEN,
            "error_forbidden_registration",
        ),
    ],
    ids=[
        "happy_path_1",
        "happy_path_2",
        "error_existing_user",
        "error_forbidden_registration",
    ],
)
def test_signup(
    client: TestClient,
    session: Session,
    override_settings,
    user_in: UserCreateOpen,
    expected_status: int,
    test_id: str,
):
    # Arrange
    # Mock the crud.get_user_by_email and crud.create_user functions if necessary
    # For example, to simulate an existing user for the error_existing_user test case
    if test_id == "error_existing_user":
        crud.get_user_by_email = (
            lambda *args, **kwargs: True
        )  # Mock returning an existing user
    else:
        crud.get_user_by_email = lambda *args, **kwargs: None  # Mock no existing user

    if test_id == "error_forbidden_registration":
        settings.USERS_OPEN_REGISTRATION = False

    # Act
    response = client.post(f"{settings.API_V1_STR}/signup", json=user_in.model_dump())

    # Assert
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert "id" in response.json()
