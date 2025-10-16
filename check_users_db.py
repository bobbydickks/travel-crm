#!/usr/bin/env python3
"""
Проверка содержимого таблицы users в базе данных
"""
import sqlite3
from datetime import datetime

def check_users_database():
    try:
        conn = sqlite3.connect('travel_crm.db')
        cursor = conn.cursor()
        
        print('📊 СТРУКТУРА ТАБЛИЦЫ USERS:')
        print('=' * 50)
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        for col in columns:
            null_info = "NOT NULL" if col[3] else "NULL"
            print(f"  {col[1]:<15} {col[2]:<10} {null_info:<8}")
        
        print(f'\n📈 КОЛИЧЕСТВО ПОЛЬЗОВАТЕЛЕЙ:')
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        print(f'  Всего пользователей: {count}')
        
        print(f'\n👥 СПИСОК ПОЛЬЗОВАТЕЛЕЙ:')
        print('=' * 80)
        cursor.execute('''
            SELECT id, email, role, created_at, updated_at 
            FROM users 
            ORDER BY created_at DESC
        ''')
        users = cursor.fetchall()
        
        if users:
            print(f'{"ID":<4} {"EMAIL":<30} {"ROLE":<12} {"CREATED":<20}')
            print('-' * 80)
            for user in users:
                created_at = user[3][:19] if user[3] else 'NULL'
                print(f'{user[0]:<4} {user[1]:<30} {user[2]:<12} {created_at:<20}')
        else:
            print('❌ Пользователей в базе нет!')
        
        # Проверяем последние записи логов
        print(f'\n📝 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:')
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f'  Таблицы в БД: {[table[0] for table in tables]}')
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке БД: {e}")
        return False

if __name__ == "__main__":
    check_users_database()
