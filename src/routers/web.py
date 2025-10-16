"""
Web interface routes for Travel CRM
Handles HTML page rendering and form processing
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Form, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import User, UserRole
from ..schemas.user import UserCreate
from ..auth import get_password_hash, verify_password, create_access_token, create_refresh_token
from ..auth.permissions import (
    get_current_user_with_permissions, 
    can_create_user_with_role, 
    get_allowed_roles_for_user,
    PermissionDenied
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Dependency для получения текущего пользователя из cookies
async def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user from JWT token in cookie"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
        
        # Verify JWT token properly
        from ..auth import verify_token
        payload = verify_token(token)
        email: str = payload.get("sub")
        
        if email is None:
            return None
            
        user = db.query(User).filter(User.email == email).first()
        return user
        
    except Exception as e:
        logger.error(f"Error getting user from cookie: {e}")
        return None


# Context processor для шаблонов
def get_template_context(request: Request, user: Optional[User] = None, messages: list = None):
    """Get common template context"""
    return {
        "request": request,
        "current_user": user,
        "datetime": datetime,
        "messages": messages or [],
    }


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    """Home page - redirect to dashboard if authenticated, otherwise to login"""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """Display login form"""
    context = get_template_context(request)
    context["error"] = error
    return templates.TemplateResponse("login.html", context)


@router.post("/login")
async def login_submit(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process login form"""
    try:
        # Authenticate user
        user = db.query(User).filter(User.email == email).first()
        
        if not user or not verify_password(password, user.password_hash):
            context = get_template_context(request)
            context.update({
                "error": "Неверный email или пароль",
                "email": email
            })
            return templates.TemplateResponse("login.html", context)
        
        # Create JWT tokens
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})
        
        # Set cookies and redirect
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            max_age=1800,  # 30 minutes
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        response.set_cookie(
            key="refresh_token", 
            value=refresh_token,
            max_age=604800,  # 7 days
            httponly=True,
            secure=False,
            samesite="lax"
        )
        
        logger.info(f"User {email} logged in successfully")
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        context = get_template_context(request)
        context.update({
            "error": "Ошибка сервера. Попробуйте позже.",
            "email": email
        })
        return templates.TemplateResponse("login.html", context)


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request, 
    current_user: Optional[User] = Depends(get_current_user_from_cookie)
):
    """Display registration form - только для авторизованных пользователей с правами"""
    # Если пользователь не авторизован, перенаправляем на логин
    if not current_user:
        return RedirectResponse(url="/login?message=register_required", status_code=302)
    
    # Проверяем права на создание пользователей
    allowed_roles = get_allowed_roles_for_user(current_user)
    if not allowed_roles:
        # Если нет прав, показываем ошибку
        context = get_template_context(request, current_user)
        context["error"] = "У вас нет прав для создания новых пользователей"
        return templates.TemplateResponse("error.html", context)
    
    context = get_template_context(request, current_user)
    context["allowed_roles"] = allowed_roles
    return templates.TemplateResponse("register.html", context)


@router.post("/register")
async def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    role: str = Form(default="OPERATOR"),
    current_user: Optional[User] = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Process registration form - с проверкой прав"""
    errors = []
    
    try:
        # Проверяем авторизацию
        if not current_user:
            return RedirectResponse(url="/login?message=auth_required", status_code=302)
        
        # Validate form data
        if password != password_confirm:
            errors.append("Пароли не совпадают")
        
        if len(password) < 6:
            errors.append("Пароль должен содержать минимум 6 символов")
            
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            errors.append("Пользователь с таким email уже существует")
        
        # Validate role
        try:
            user_role = UserRole(role)
        except ValueError:
            errors.append("Недопустимая роль")
            user_role = UserRole.OPERATOR
        
        # Проверяем права на создание пользователя с указанной ролью
        if not can_create_user_with_role(current_user, user_role):
            errors.append(f"У вас нет прав для создания пользователя с ролью {user_role.value}")
        
        if errors:
            context = get_template_context(request, current_user)
            context.update({
                "errors": errors,
                "email": email,
                "role": role,
                "allowed_roles": get_allowed_roles_for_user(current_user)
            })
            return templates.TemplateResponse("register.html", context)
        
        # Create new user
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            password_hash=hashed_password,
            role=user_role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User {current_user.email} created new user: {email} with role {role}")
        
        # Redirect to dashboard with success message
        return RedirectResponse(url="/dashboard?user_created=1", status_code=302)
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        errors.append("Ошибка сервера. Попробуйте позже.")
        
        context = get_template_context(request, current_user)
        context.update({
            "errors": errors,
            "email": email,
            "role": role,
            "allowed_roles": get_allowed_roles_for_user(current_user)
        })
        return templates.TemplateResponse("register.html", context)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    current_user: Optional[User] = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Dashboard page"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get dashboard statistics
    stats = {
        "clients": 0,  # Will be populated from actual Client model later
        "applications": 0,  # Will be populated from Application model later  
        "orders": 0,  # Will be populated from Order model later
        "revenue": "0 ₽"  # Will be calculated from payments later
    }
    
    # Get recent activity (mock data for now)
    recent_activity = [
        {
            "title": "Система запущена",
            "description": "Travel CRM успешно развернута и готова к работе",
            "created_at": datetime.now() - timedelta(minutes=5),
            "icon": "check-circle",
            "type_color": "success"
        }
    ]
    
    context = get_template_context(request, current_user)
    context.update({
        "stats": stats,
        "recent_activity": recent_activity
    })
    
    return templates.TemplateResponse("dashboard.html", context)


@router.get("/logout")
async def logout(request: Request):
    """Logout user"""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


# Placeholder routes for future features
@router.get("/clients", response_class=HTMLResponse)
async def clients_page(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    """Clients management page"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # TODO: Implement clients list page in Stage 2
    return HTMLResponse(content="<h1>Клиенты</h1><p>Раздел будет реализован на этапе 2</p><a href='/dashboard'>← Назад</a>")


@router.get("/applications", response_class=HTMLResponse) 
async def applications_page(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    """Applications management page"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
        
    # TODO: Implement applications list page in Stage 2
    return HTMLResponse(content="<h1>Заявки</h1><p>Раздел будет реализован на этапе 2</p><a href='/dashboard'>← Назад</a>")


@router.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    """Orders management page"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
        
    # TODO: Implement orders list page in Stage 3
    return HTMLResponse(content="<h1>Заказы</h1><p>Раздел будет реализован на этапе 3</p><a href='/dashboard'>← Назад</a>")


@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    """Reports page"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
        
    # TODO: Implement reports page in Stage 5
    return HTMLResponse(content="<h1>Отчёты</h1><p>Раздел будет реализован на этапе 5</p><a href='/dashboard'>← Назад</a>")


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    """User profile page"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
        
    context = get_template_context(request, current_user)
    return HTMLResponse(content=f"""
    <h1>Профиль пользователя</h1>
    <p><strong>Email:</strong> {current_user.email}</p>
    <p><strong>Роль:</strong> {current_user.role.value}</p>
    <p><strong>Создан:</strong> {current_user.created_at.strftime('%d.%m.%Y %H:%M')}</p>
    <a href='/dashboard'>← Назад к дашборду</a>
    """)
