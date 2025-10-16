#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for Travel CRM
Выполняет полную проверку всех компонентов системы
"""

import asyncio
import subprocess
import time
import requests
import os
import sys
from pathlib import Path
import json
import sqlite3

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TravelCRMTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8003"  # Используем порт 8003 для тестов
        self.server_process = None
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Логирование результатов тестов"""
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if success else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"  {status} {test_name}")
        if message:
            print(f"    {Colors.CYAN}{message}{Colors.END}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    def start_server(self):
        """Запуск сервера для тестирования"""
        print(f"{Colors.BLUE}{Colors.BOLD}🚀 Запуск сервера для тестирования...{Colors.END}")
        
        try:
            # Переходим в директорию проекта
            os.chdir(Path(__file__).parent)
            
            # Запускаем сервер в фоновом режиме
            self.server_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "src.main:app",
                "--host", "127.0.0.1",
                "--port", "8003",
                "--log-level", "error"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Ждем запуска сервера
            for i in range(30):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=1)
                    if response.status_code == 200:
                        print(f"{Colors.GREEN}✓ Сервер запущен на {self.base_url}{Colors.END}")
                        return True
                except:
                    time.sleep(1)
            
            print(f"{Colors.RED}✗ Не удалось запустить сервер{Colors.END}")
            return False
            
        except Exception as e:
            print(f"{Colors.RED}✗ Ошибка запуска сервера: {e}{Colors.END}")
            return False
    
    def stop_server(self):
        """Остановка сервера"""
        if self.server_process:
            print(f"{Colors.YELLOW}🛑 Остановка сервера...{Colors.END}")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
    
    def test_database_connection(self):
        """Тест подключения к базе данных"""
        print(f"\n{Colors.BOLD}📊 Тестирование базы данных{Colors.END}")
        
        try:
            # Проверяем наличие файла БД
            db_path = Path("travel_crm.db")
            if not db_path.exists():
                self.log_test("Database file exists", False, "travel_crm.db не найден")
                return
            
            self.log_test("Database file exists", True, f"Размер: {db_path.stat().st_size} байт")
            
            # Проверяем структуру БД
            conn = sqlite3.connect("travel_crm.db")
            cursor = conn.cursor()
            
            # Проверяем таблицу users
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if cursor.fetchone():
                self.log_test("Users table exists", True)
                
                # Считаем количество пользователей
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                self.log_test("Users count", True, f"Пользователей в БД: {user_count}")
            else:
                self.log_test("Users table exists", False)
            
            conn.close()
            
        except Exception as e:
            self.log_test("Database connection", False, str(e))
    
    def test_api_endpoints(self):
        """Тест API эндпоинтов"""
        print(f"\n{Colors.BOLD}🌐 Тестирование API эндпоинтов{Colors.END}")
        
        # Тест health check
        try:
            response = requests.get(f"{self.base_url}/health")
            self.log_test("GET /health", response.status_code == 200, 
                         f"Status: {response.status_code}, Response: {response.json()}")
        except Exception as e:
            self.log_test("GET /health", False, str(e))
        
        # Тест robots.txt
        try:
            response = requests.get(f"{self.base_url}/robots.txt")
            self.log_test("GET /robots.txt", response.status_code == 200,
                         f"Content-Type: {response.headers.get('content-type')}")
        except Exception as e:
            self.log_test("GET /robots.txt", False, str(e))
        
        # Тест favicon
        try:
            response = requests.get(f"{self.base_url}/favicon.ico")
            self.log_test("GET /favicon.ico", response.status_code == 200,
                         f"Content-Type: {response.headers.get('content-type')}")
        except Exception as e:
            self.log_test("GET /favicon.ico", False, str(e))
        
        # Тест OpenAPI docs
        try:
            response = requests.get(f"{self.base_url}/docs")
            self.log_test("GET /docs", response.status_code == 200,
                         "Swagger UI доступен")
        except Exception as e:
            self.log_test("GET /docs", False, str(e))
    
    def test_web_interface(self):
        """Тест веб-интерфейса"""
        print(f"\n{Colors.BOLD}🌐 Тестирование веб-интерфейса{Colors.END}")
        
        session = requests.Session()
        
        # Тест главной страницы (перенаправление на /login)
        try:
            response = session.get(f"{self.base_url}/", allow_redirects=False)
            self.log_test("GET / (redirect to login)", response.status_code == 302,
                         f"Location: {response.headers.get('location')}")
        except Exception as e:
            self.log_test("GET / (redirect)", False, str(e))
        
        # Тест страницы логина
        try:
            response = session.get(f"{self.base_url}/login")
            success = response.status_code == 200 and ("Войти" in response.text or "Travel CRM" in response.text)
            self.log_test("GET /login", success,
                         f"Status: {response.status_code}, Contains login form: {success}")
        except Exception as e:
            self.log_test("GET /login", False, str(e))
        
        # Тест страницы регистрации
        try:
            response = session.get(f"{self.base_url}/register")
            success = response.status_code == 200 and ("Зарегистрироваться" in response.text or "Travel CRM" in response.text)
            self.log_test("GET /register", success,
                         f"Status: {response.status_code}, Contains register form: {success}")
        except Exception as e:
            self.log_test("GET /register", False, str(e))
        
        # Тест доступа к dashboard без авторизации
        try:
            response = session.get(f"{self.base_url}/dashboard", allow_redirects=False)
            self.log_test("GET /dashboard (unauthorized)", response.status_code == 302,
                         "Правильное перенаправление неавторизованного пользователя")
        except Exception as e:
            self.log_test("GET /dashboard (unauthorized)", False, str(e))
    
    def test_authentication_flow(self):
        """Тест аутентификации"""
        print(f"\n{Colors.BOLD}🔐 Тестирование аутентификации{Colors.END}")
        
        session = requests.Session()
        
        # Тест неверного логина через API (OAuth2PasswordRequestForm)
        try:
            response = session.post(f"{self.base_url}/auth/login", 
                                  data={"username": "wrong_user", "password": "wrong_pass"},
                                  headers={"Content-Type": "application/x-www-form-urlencoded"})
            self.log_test("Login with wrong credentials (API)", response.status_code == 401,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Login with wrong credentials (API)", False, str(e))
        
        # Тест логина админа через API (используем email вместо username)
        try:
            response = session.post(f"{self.base_url}/auth/login", 
                                  data={"username": "admin@travelcrm.com", "password": "admin123"},
                                  headers={"Content-Type": "application/x-www-form-urlencoded"})
            if response.status_code == 200:
                token_data = response.json()
                self.log_test("Admin login (API)", True,
                             f"Token type: {token_data.get('token_type')}")
            else:
                self.log_test("Admin login (API)", False,
                             f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Admin login (API)", False, str(e))
        
        # Тест логина через веб-форму (используем email поле)
        try:
            # Получаем страницу логина
            response = session.get(f"{self.base_url}/login")
            if response.status_code == 200:
                # Отправляем форму логина с email полем
                login_response = session.post(f"{self.base_url}/login", 
                                            data={"email": "admin@travelcrm.com", "password": "admin123"},
                                            allow_redirects=False)
                
                if login_response.status_code == 302:
                    # Проверяем доступ к dashboard после логина
                    dashboard_response = session.get(f"{self.base_url}/dashboard")
                    success = dashboard_response.status_code == 200 and ("Dashboard" in dashboard_response.text or "Дашборд" in dashboard_response.text)
                    self.log_test("Web login flow", success,
                                 f"Dashboard accessible: {success}")
                else:
                    self.log_test("Web login flow", False,
                                 f"Login failed: {login_response.status_code}")
            else:
                self.log_test("Web login flow", False, "Cannot access login page")
        except Exception as e:
            self.log_test("Web login flow", False, str(e))
    
    def test_static_files(self):
        """Тест статических файлов"""
        print(f"\n{Colors.BOLD}📁 Тестирование статических файлов{Colors.END}")
        
        # Тест CSS
        try:
            response = requests.get(f"{self.base_url}/static/style.css")
            success = response.status_code == 200 and "text/css" in response.headers.get('content-type', '')
            self.log_test("Static CSS file", success,
                         f"Status: {response.status_code}, Size: {len(response.content)} bytes")
        except Exception as e:
            self.log_test("Static CSS file", False, str(e))
        
        # Тест favicon из static
        try:
            response = requests.get(f"{self.base_url}/static/favicon.ico")
            self.log_test("Static favicon", response.status_code == 200,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Static favicon", False, str(e))
    
    def test_alembic_migrations(self):
        """Тест миграций Alembic"""
        print(f"\n{Colors.BOLD}🔧 Тестирование миграций Alembic{Colors.END}")
        
        try:
            # Проверяем текущую ревизию
            result = subprocess.run([sys.executable, "-m", "alembic", "current"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                self.log_test("Alembic current revision", True, 
                             f"Current: {output}")
            else:
                self.log_test("Alembic current revision", False, 
                             f"Error: {result.stderr}")
            
            # Проверяем историю миграций
            result = subprocess.run([sys.executable, "-m", "alembic", "history"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                migrations_count = len([line for line in result.stdout.split('\n') if line.strip()])
                self.log_test("Alembic migrations history", True,
                             f"Migrations found: {migrations_count}")
            else:
                self.log_test("Alembic migrations history", False,
                             f"Error: {result.stderr}")
                
        except Exception as e:
            self.log_test("Alembic migrations", False, str(e))
    
    def test_project_structure(self):
        """Тест структуры проекта"""
        print(f"\n{Colors.BOLD}📋 Тестирование структуры проекта{Colors.END}")
        
        required_files = [
            "src/main.py",
            "src/database.py", 
            "src/auth.py",
            "src/models/user.py",
            "src/routers/auth.py",
            "src/routers/web.py",
            "templates/base.html",
            "templates/login.html",
            "templates/register.html", 
            "templates/dashboard.html",
            "static/style.css",
            "requirements.txt",
            "pyproject.toml",
            "alembic.ini"
        ]
        
        for file_path in required_files:
            exists = Path(file_path).exists()
            self.log_test(f"File exists: {file_path}", exists)
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("=" * 60)
        print("🚀 COMPREHENSIVE TRAVEL CRM E2E TEST SUITE")
        print("=" * 60)
        print(f"{Colors.END}")
        
        # Запускаем сервер
        if not self.start_server():
            print(f"{Colors.RED}Не удалось запустить сервер. Тесты прерваны.{Colors.END}")
            return
        
        try:
            # Выполняем все тесты
            self.test_project_structure()
            self.test_database_connection()
            self.test_alembic_migrations()
            self.test_api_endpoints()
            self.test_static_files()
            self.test_web_interface()
            self.test_authentication_flow()
            
        finally:
            # Останавливаем сервер
            self.stop_server()
        
        # Выводим результаты
        self.print_summary()
    
    def print_summary(self):
        """Вывод итогового отчета"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        print(f"{Colors.END}")
        
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        
        print(f"{Colors.GREEN}✓ Тестов пройдено: {passed}{Colors.END}")
        print(f"{Colors.RED}✗ Тестов провалено: {failed}{Colors.END}")
        print(f"📊 Всего тестов: {len(self.test_results)}")
        
        if failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}Провалившиеся тесты:{Colors.END}")
            for result in self.test_results:
                if not result['success']:
                    print(f"  {Colors.RED}✗ {result['test']}{Colors.END}")
                    if result['message']:
                        print(f"    {Colors.YELLOW}{result['message']}{Colors.END}")
        
        success_rate = (passed / len(self.test_results)) * 100 if self.test_results else 0
        
        print(f"\n{Colors.BOLD}Процент успешности: {success_rate:.1f}%{Colors.END}")
        
        if success_rate >= 90:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ОТЛИЧНО! Система работает стабильно{Colors.END}")
        elif success_rate >= 70:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ ХОРОШО, но есть проблемы для исправления{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ ТРЕБУЕТСЯ ВНИМАНИЕ! Много критических проблем{Colors.END}")

if __name__ == "__main__":
    tester = TravelCRMTester()
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Тестирование прервано пользователем{Colors.END}")
        tester.stop_server()
    except Exception as e:
        print(f"\n{Colors.RED}Критическая ошибка: {e}{Colors.END}")
        tester.stop_server()
