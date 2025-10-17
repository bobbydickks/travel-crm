#!/usr/bin/env python3
"""
Initialization script for PythonAnywhere:
- Runs Alembic migrations to head
- Creates/updates admin user using ADMIN_EMAIL/ADMIN_PASSWORD

Usage:
- Through Files interface: just run this file
- Through Python console: exec(open('/home/username/travel-crm/pythonanywhere_init.py').read())
"""
import os
import sys
from pathlib import Path

# Ensure we're in project root and add paths
root = Path(__file__).resolve().parent
os.chdir(root)
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
if str(root / "src") not in sys.path:
    sys.path.insert(0, str(root / "src"))

def main():
    print("=== Travel CRM Initialization ===")
    
    # Check DATABASE_URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL is not set in environment.")
        print("Please set it in Web app → Environment variables or create .env file")
        return False

    print(f"Database URL: {db_url[:50]}...")

    # Run Alembic migrations directly
    print("\n1. Running Alembic migrations...")
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✓ Migrations completed successfully")
    except Exception as e:
        print(f"✗ Alembic migration failed: {e}")
        return False

    # Create/update admin directly
    print("\n2. Creating/updating admin user...")
    try:
        from src.database import SessionLocal
        from src.models.user import User, UserRole
        from src.auth import get_password_hash
        
        email = os.getenv("ADMIN_EMAIL", "admin@travelcrm.com")
        password = os.getenv("ADMIN_PASSWORD", "admin123")

        db = SessionLocal()
        try:
            # Check if admin exists
            admin = db.query(User).filter((User.role == UserRole.ADMIN) | (User.email == email)).first()
            if admin:
                admin.role = UserRole.ADMIN
                if password:
                    admin.password_hash = get_password_hash(password)
                db.commit()
                print(f"✓ Admin user updated: {admin.email}")
            else:
                # Create new admin
                admin_user = User(
                    email=email,
                    password_hash=get_password_hash(password),
                    role=UserRole.ADMIN
                )
                db.add(admin_user)
                db.commit()
                print(f"✓ Admin user created: {email}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"✗ Admin creation failed: {e}")
        return False

    print("\n✓ Initialization completed successfully!")
    print(f"Admin login: {os.getenv('ADMIN_EMAIL', 'admin@travelcrm.com')}")
    print("You can now access:")
    print("- Web interface: https://yourdomain.pythonanywhere.com/")
    print("- Swagger API: https://yourdomain.pythonanywhere.com/docs")
    return True


if __name__ == "__main__":
    main()
