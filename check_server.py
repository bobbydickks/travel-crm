#!/usr/bin/env python3
"""
Простая проверка работоспособности Travel CRM сервера
"""
import requests
import time
import json

def check_server():
    base_url = 'http://127.0.0.1:8000'
    
    print('🚀 TRAVEL CRM - ПРОВЕРКА РАБОТОСПОСОБНОСТИ СЕРВЕРА')
    print('=' * 60)
    
    # Проверка основных endpoints
    endpoints = [
        ('/health', '🏥 Health Check'),
        ('/docs', '📚 Swagger UI Documentation'),
        ('/redoc', '📖 ReDoc Documentation'), 
        ('/openapi.json', '🔧 OpenAPI JSON Schema'),
        ('/', '🏠 Home Page (redirect to login)'),
        ('/login', '🔐 Login Page'),
        ('/register', '📝 Registration Page'),
        ('/robots.txt', '🤖 Robots.txt'),
        ('/favicon.ico', '🎯 Favicon'),
        ('/static/style.css', '🎨 CSS Styles')
    ]
    
    working_endpoints = 0
    total_endpoints = len(endpoints)
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=5)
            
            if response.status_code == 200:
                status = '✅ OK'
                working_endpoints += 1
            elif response.status_code == 302:
                status = '🔄 REDIRECT'
                working_endpoints += 1
            else:
                status = f'⚠️ {response.status_code}'
                
            print(f'{status} {endpoint:20} - {description}')
            
        except requests.exceptions.ConnectionError:
            print(f'❌ {endpoint:20} - {description} (Server not running)')
        except Exception as e:
            print(f'❌ {endpoint:20} - {description} (Error: {e})')
    
    print('\n' + '=' * 60)
    
    # Проверка API аутентификации
    print('\n🔑 API AUTHENTICATION TEST:')
    try:
        auth_response = requests.post(
            f'{base_url}/auth/login',
            data={'username': 'admin@travelcrm.com', 'password': 'admin123'},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=5
        )
        
        if auth_response.status_code == 200:
            token_data = auth_response.json()
            print(f'✅ Admin login successful')
            print(f'   Token type: {token_data.get("token_type")}')
            print(f'   Has access token: {"access_token" in token_data}')
        else:
            print(f'❌ Admin login failed - Status: {auth_response.status_code}')
            
    except Exception as e:
        print(f'❌ Authentication test failed: {e}')
    
    # Итоговый отчет
    print('\n' + '=' * 60)
    print('📊 ИТОГОВЫЙ ОТЧЕТ:')
    print(f'✅ Работающих endpoints: {working_endpoints}/{total_endpoints}')
    percentage = (working_endpoints / total_endpoints) * 100
    print(f'📈 Процент работоспособности: {percentage:.1f}%')
    
    if percentage >= 90:
        print('🎉 ОТЛИЧНО! Сервер работает стабильно')
    elif percentage >= 70:
        print('⚠️ ХОРОШО, но есть некоторые проблемы')
    else:
        print('❌ ТРЕБУЕТСЯ ВНИМАНИЕ! Много проблем')
    
    print('\n🌐 ДОСТУПНЫЕ ССЫЛКИ:')
    print(f'   • Веб-интерфейс:     {base_url}')
    print(f'   • Swagger UI:        {base_url}/docs')
    print(f'   • ReDoc:             {base_url}/redoc')
    print(f'   • Health Check:      {base_url}/health')
    
    print('\n👤 АДМИНИСТРАТОР:')
    print(f'   • Email:    admin@travelcrm.com')
    print(f'   • Password: admin123')

if __name__ == '__main__':
    check_server()
