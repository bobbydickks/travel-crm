"""
Модуль аутентификации и авторизации
"""
# Импортируем основные функции аутентификации
from .core import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)

# Импортируем систему прав
from .permissions import (
    PermissionDenied,
    RoleHierarchy,
    Permissions,
    has_permission,
    require_permission,
    require_role,
    get_current_user_with_permissions,
    can_create_user_with_role,
    get_allowed_roles_for_user
)

__all__ = [
    # Основные функции аутентификации
    "verify_password",
    "get_password_hash", 
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    # Система прав
    "PermissionDenied",
    "RoleHierarchy", 
    "Permissions",
    "has_permission",
    "require_permission",
    "require_role",
    "get_current_user_with_permissions",
    "can_create_user_with_role",
    "get_allowed_roles_for_user"
]
