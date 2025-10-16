#!/usr/bin/env python3
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8002"

def test_api():
    print("🧪 End-to-End тестирование Travel CRM API")
    print("=" * 50)
    
    try:
        # 1. Health check
        print("1️⃣ Проверка health-check...")
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        health_data = response.json()
        print(f"✅ Health check: {health_data['status']}")
        
        # 2. Root endpoint
        print("\n2️⃣ Проверка root endpoint...")
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        root_data = response.json()
        print(f"✅ Root: {root_data['message']}")
        
        # 3. Регистрация нового пользователя
        print("\n3️⃣ Регистрация нового пользователя...")
        register_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        assert response.status_code == 201
        user_data = response.json()
        print(f"✅ Пользователь создан: {user_data['email']}, роль: {user_data['role']}")
        
        # 4. Вход в систему
        print("\n4️⃣ Авторизация пользователя...")
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        assert response.status_code == 200
        token_data = response.json()
        access_token = token_data["access_token"]
        print("✅ Успешная авторизация, токен получен")
        
        # 5. Получение информации о текущем пользователе
        print("\n5️⃣ Получение профиля пользователя...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        assert response.status_code == 200
        profile_data = response.json()
        print(f"✅ Профиль: {profile_data['email']}, роль: {profile_data['role']}")
        
        # 6. Обновление токена
        print("\n6️⃣ Обновление refresh токена...")
        refresh_data = {"refresh_token": token_data["refresh_token"]}
        response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        new_token_data = response.json()
        print("✅ Токен успешно обновлен")
        
        # 7. Тест с админским пользователем
        print("\n7️⃣ Тест авторизации админа...")
        admin_login_data = {
            "username": "admin@travelcrm.com",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=admin_login_data)
        assert response.status_code == 200
        admin_token_data = response.json()
        print("✅ Админ успешно авторизован")
        
        admin_headers = {"Authorization": f"Bearer {admin_token_data['access_token']}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=admin_headers)
        assert response.status_code == 200
        admin_profile = response.json()
        print(f"✅ Админ профиль: {admin_profile['email']}, роль: {admin_profile['role']}")
        
        print("\n" + "=" * 50)
        print("🎉 Все End-to-End тесты прошли успешно!")
        print("✅ Этап 1 полностью функционален")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Ошибка: Сервер не запущен на {BASE_URL}")
        return False
    except AssertionError as e:
        print(f"❌ Тест провален: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
