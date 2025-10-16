"""
Система авторизации и проверки прав доступа
"""
from functools import wraps
from typing import List, Optional
from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from ..models.user import User, UserRole
from ..database import get_db
from .core import verify_token
import logging

logger = logging.getLogger(__name__)


class PermissionDenied(HTTPException):
    """Исключение для отказа в доступе"""
    def __init__(self, detail: str = "Недостаточно прав для выполнения операции"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class RoleHierarchy:
    """Иерархия ролей в системе"""
    ROLES = {
        UserRole.ADMIN: 4,
        UserRole.SUPERVISOR: 3,
        UserRole.ACCOUNTANT: 2,
        UserRole.OPERATOR: 1
    }
    
    @classmethod
    def has_permission(cls, user_role: UserRole, required_role: UserRole) -> bool:
        """Проверяет, имеет ли пользователь достаточные права"""
        user_level = cls.ROLES.get(user_role, 0)
        required_level = cls.ROLES.get(required_role, 999)
        return user_level >= required_level
    
    @classmethod
    def can_manage_role(cls, user_role: UserRole, target_role: UserRole) -> bool:
        """Проверяет, может ли пользователь управлять указанной ролью"""
        # Пользователь может управлять ролями ниже своей по иерархии
        user_level = cls.ROLES.get(user_role, 0)
        target_level = cls.ROLES.get(target_role, 999)
        return user_level > target_level


class Permissions:
    """Определение разрешений для различных операций"""
    
    # Управление пользователями
    CREATE_USER = "create_user"
    DELETE_USER = "delete_user"
    ASSIGN_ROLES = "assign_roles"
    VIEW_ALL_USERS = "view_all_users"
    
    # Управление клиентами
    CREATE_CLIENT = "create_client"
    EDIT_CLIENT = "edit_client"
    DELETE_CLIENT = "delete_client"
    VIEW_ALL_CLIENTS = "view_all_clients"
    
    # Управление заявками
    CREATE_APPLICATION = "create_application"
    EDIT_APPLICATION = "edit_application"
    DELETE_APPLICATION = "delete_application"
    ASSIGN_APPLICATION = "assign_application"
    VIEW_ALL_APPLICATIONS = "view_all_applications"
    
    # Финансовые операции
    VIEW_FINANCIAL_DATA = "view_financial_data"
    EDIT_FINANCIAL_DATA = "edit_financial_data"
    GENERATE_REPORTS = "generate_reports"
    
    # Системные операции
    SYSTEM_SETTINGS = "system_settings"
    VIEW_LOGS = "view_logs"


# Матрица разрешений для ролей
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        # Все разрешения
        Permissions.CREATE_USER,
        Permissions.DELETE_USER,
        Permissions.ASSIGN_ROLES,
        Permissions.VIEW_ALL_USERS,
        Permissions.CREATE_CLIENT,
        Permissions.EDIT_CLIENT,
        Permissions.DELETE_CLIENT,
        Permissions.VIEW_ALL_CLIENTS,
        Permissions.CREATE_APPLICATION,
        Permissions.EDIT_APPLICATION,
        Permissions.DELETE_APPLICATION,
        Permissions.ASSIGN_APPLICATION,
        Permissions.VIEW_ALL_APPLICATIONS,
        Permissions.VIEW_FINANCIAL_DATA,
        Permissions.EDIT_FINANCIAL_DATA,
        Permissions.GENERATE_REPORTS,
        Permissions.SYSTEM_SETTINGS,
        Permissions.VIEW_LOGS,
    ],
    
    UserRole.SUPERVISOR: [
        # Управление пользователями (ограниченно)
        Permissions.CREATE_USER,  # Только роли ниже
        Permissions.VIEW_ALL_USERS,
        # Полное управление клиентами и заявками
        Permissions.CREATE_CLIENT,
        Permissions.EDIT_CLIENT,
        Permissions.DELETE_CLIENT,
        Permissions.VIEW_ALL_CLIENTS,
        Permissions.CREATE_APPLICATION,
        Permissions.EDIT_APPLICATION,
        Permissions.DELETE_APPLICATION,
        Permissions.ASSIGN_APPLICATION,
        Permissions.VIEW_ALL_APPLICATIONS,
        # Ограниченные финансовые права
        Permissions.VIEW_FINANCIAL_DATA,
        Permissions.GENERATE_REPORTS,
    ],
    
    UserRole.ACCOUNTANT: [
        # Ограниченное управление клиентами
        Permissions.VIEW_ALL_CLIENTS,
        Permissions.EDIT_CLIENT,  # Только финансовую информацию
        # Ограниченное управление заявками
        Permissions.VIEW_ALL_APPLICATIONS,
        Permissions.EDIT_APPLICATION,  # Только финансовую часть
        # Полные финансовые права
        Permissions.VIEW_FINANCIAL_DATA,
        Permissions.EDIT_FINANCIAL_DATA,
        Permissions.GENERATE_REPORTS,
    ],
    
    UserRole.OPERATOR: [
        # Базовые операции с клиентами
        Permissions.CREATE_CLIENT,
        Permissions.EDIT_CLIENT,  # Только свои
        # Базовые операции с заявками
        Permissions.CREATE_APPLICATION,
        Permissions.EDIT_APPLICATION,  # Только свои
    ]
}


def has_permission(user: User, permission: str) -> bool:
    """Проверяет, имеет ли пользователь определенное разрешение"""
    user_permissions = ROLE_PERMISSIONS.get(user.role, [])
    return permission in user_permissions


def require_permission(permission: str):
    """Декоратор для проверки разрешений"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем текущего пользователя из зависимостей
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Требуется аутентификация"
                )
            
            if not has_permission(current_user, permission):
                logger.warning(f"User {current_user.email} ({current_user.role.value}) denied access to {permission}")
                raise PermissionDenied(f"Недостаточно прав для операции: {permission}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(*allowed_roles: UserRole):
    """Декоратор для проверки роли пользователя"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем текущего пользователя из зависимостей
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Требуется аутентификация"
                )
            
            if current_user.role not in allowed_roles:
                logger.warning(
                    f"User {current_user.email} ({current_user.role.value}) "
                    f"denied access. Required roles: {[r.value for r in allowed_roles]}"
                )
                raise PermissionDenied(
                    f"Требуется одна из ролей: {', '.join([r.value for r in allowed_roles])}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def get_current_user_with_permissions(
    request: Request, 
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя с проверкой токена"""
    # Для API - проверяем Bearer token
    authorization = request.headers.get("Authorization")
    token = None
    
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        # Для веб-интерфейса - проверяем cookie
        token = request.cookies.get("access_token")
        if token and token.startswith("Bearer "):
            token = token[7:]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется токен доступа",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен"
            )
        
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        
        return user
        
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )


def can_create_user_with_role(creator: User, target_role: UserRole) -> bool:
    """Проверяет, может ли пользователь создать аккаунт с указанной ролью"""
    # Админ может создавать любые роли
    if creator.role == UserRole.ADMIN:
        return True
    
    # Супервайзер может создавать только операторов и бухгалтеров
    if creator.role == UserRole.SUPERVISOR:
        return target_role in [UserRole.OPERATOR, UserRole.ACCOUNTANT]
    
    # Остальные не могут создавать пользователей
    return False


def get_allowed_roles_for_user(user: User) -> List[UserRole]:
    """Возвращает список ролей, которые может назначить пользователь"""
    if user.role == UserRole.ADMIN:
        return [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.ACCOUNTANT, UserRole.OPERATOR]
    elif user.role == UserRole.SUPERVISOR:
        return [UserRole.ACCOUNTANT, UserRole.OPERATOR]
    else:
        return []
