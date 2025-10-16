#!/usr/bin/env python3
"""
Создание администратора для Railway deployment
"""
import os
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.models.user import User, Base
from src.auth.core import get_password_hash

def create_admin():
    """Создает администратора если его нет"""
    # Настройки для Railway
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travel_crm.db")
    
    # Создаем движок базы данных
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL)
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем сессию
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Проверяем, есть ли уже администратор
        admin = session.query(User).filter(User.email == "admin@travelcrm.com").first()
        
        if not admin:
            # Создаем администратора
            admin_user = User(
                email="admin@travelcrm.com",
                password_hash=get_password_hash("admin123"),
                role="ADMIN",
                is_active=True
            )
            
            session.add(admin_user)
            session.commit()
            print("✅ Администратор создан: admin@travelcrm.com / admin123")
        else:
            print("✅ Администратор уже существует")
            
    except Exception as e:
        print(f"❌ Ошибка при создании администратора: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_admin()
