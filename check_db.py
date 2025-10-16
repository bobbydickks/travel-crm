#!/usr/bin/env python3
import sqlite3
import sys
import os

# Change to project directory
os.chdir("c:/Users/user/Desktop/Crm-Travel")

try:
    conn = sqlite3.connect('travel_crm.db')
    
    # Check tables
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print("Tables in database:", [t[0] for t in tables])
    
    # Check users count
    if ('users',) in tables:
        users_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        print(f"Users count: {users_count}")
        
        # Show sample user
        if users_count > 0:
            user = conn.execute('SELECT id, email, role FROM users LIMIT 1').fetchone()
            print(f"Sample user: ID={user[0]}, Email={user[1]}, Role={user[2]}")
    
    conn.close()
    print("✅ Database check completed successfully")
    
except Exception as e:
    print(f"❌ Database check failed: {e}")
    sys.exit(1)
