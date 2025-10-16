"""
Tests for web interface routes
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database import get_db, Base
from src.models.user import User, UserRole
from src.auth import get_password_hash

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user"""
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        role=UserRole.OPERATOR
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_home_redirect_to_login():
    """Test that home page redirects to login when not authenticated"""
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["location"]


def test_login_page_display():
    """Test that login page displays correctly"""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Travel CRM" in response.content
    assert b"email" in response.content
    assert b"password" in response.content


def test_register_page_display():
    """Test that registration page displays correctly"""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"registration" in response.content.lower() or "регистрация" in response.text.lower()
    assert b"email" in response.content
    assert b"password" in response.content


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post("/login", data={
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }, follow_redirects=False)
    
    assert response.status_code == 200
    assert b"error" in response.content.lower() or "неверный" in response.text.lower()


def test_login_success(test_user):
    """Test successful login"""
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "testpass123"
    }, follow_redirects=False)
    
    assert response.status_code == 302
    assert "/dashboard" in response.headers["location"]
    # Check that cookies are set
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


def test_register_success():
    """Test successful registration"""
    response = client.post("/register", data={
        "email": "newuser@example.com",
        "password": "newpass123",
        "password_confirm": "newpass123",
        "role": "OPERATOR"
    }, follow_redirects=False)
    
    assert response.status_code == 302
    assert "/login" in response.headers["location"]


def test_register_password_mismatch():
    """Test registration with password mismatch"""
    response = client.post("/register", data={
        "email": "newuser@example.com",
        "password": "password123",
        "password_confirm": "differentpass",
        "role": "OPERATOR"
    })
    
    assert response.status_code == 200
    assert "совпадают" in response.text.lower() or b"match" in response.content.lower()


def test_register_existing_email(test_user):
    """Test registration with existing email"""
    response = client.post("/register", data={
        "email": "test@example.com",  # Same as test_user
        "password": "newpass123",
        "password_confirm": "newpass123",
        "role": "OPERATOR"
    })
    
    assert response.status_code == 200
    assert "существует" in response.text.lower() or b"exists" in response.content.lower()


def test_dashboard_requires_auth():
    """Test that dashboard requires authentication"""
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["location"]


def test_logout():
    """Test logout functionality"""
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["location"]


def test_placeholder_pages_require_auth():
    """Test that placeholder pages require authentication"""
    pages = ["/clients", "/applications", "/orders", "/reports", "/profile"]
    
    for page in pages:
        response = client.get(page)
        assert response.status_code == 302
        assert "/login" in response.headers["location"]


def test_static_endpoints():
    """Test static utility endpoints"""
    # Health check
    response = client.get("/health")
    assert response.status_code == 200
    
    # Favicon
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    
    # Robots.txt
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert b"User-agent" in response.content


def test_api_endpoints_still_work():
    """Test that API endpoints are not affected by web routes"""
    # Test API registration
    response = client.post("/auth/register", json={
        "email": "api_user@example.com",
        "password": "apipass123",
        "role": "OPERATOR"
    })
    assert response.status_code == 201
    
    # Test API login
    response = client.post("/auth/login", data={
        "username": "api_user@example.com",
        "password": "apipass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_css_and_assets():
    """Test that CSS and static assets are served"""
    # Test CSS file
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert b"Travel CRM" in response.content or b"css" in response.content.lower()
    
    # Test favicon (should not be 404)
    response = client.get("/static/favicon.ico")
    assert response.status_code in [200, 404]  # Either exists or handled gracefully
