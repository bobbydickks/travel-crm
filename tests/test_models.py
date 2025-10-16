import pytest
from src.auth import verify_password, get_password_hash, create_access_token, verify_token
from src.models.user import User, UserRole


def test_password_hashing():
    password = "testpassword"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    
    payload = verify_token(token)
    assert payload["sub"] == "test@example.com"


def test_user_model():
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        role=UserRole.OPERATOR
    )
    
    assert user.email == "test@example.com"
    assert user.role == UserRole.OPERATOR
    assert user.password_hash == "hashed_password"
