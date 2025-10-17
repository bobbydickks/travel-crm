#!/usr/bin/env python3
"""
Script to create initial admin user
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database import SessionLocal
from src.models.user import User, UserRole
from src.auth import get_password_hash

def create_admin_user():
    db = SessionLocal()
    try:
        email = os.getenv("ADMIN_EMAIL", "admin@travelcrm.com")
        password = os.getenv("ADMIN_PASSWORD", "admin123")

        # Check if admin already exists by role or email
        admin = db.query(User).filter((User.role == UserRole.ADMIN) | (User.email == email)).first()
        if admin:
            # Ensure admin has ADMIN role and update password if env provided
            admin.role = UserRole.ADMIN
            if password:
                admin.password_hash = get_password_hash(password)
            db.commit()
            print(f"Admin user ensured. Email: {admin.email}")
            return

        # Create admin user
        admin_user = User(
            email=email,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
