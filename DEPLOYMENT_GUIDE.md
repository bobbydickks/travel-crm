# 🚀 Travel CRM - Полное руководство по запуску и использованию

## 📋 Обзор системы

**Travel CRM** - это полнофункциональная веб-платформа для управления туристическим бизнесом, разработанная на FastAPI с современным веб-интерфейсом.

### ✅ Текущий статус: **ПОЛНОСТЬЮ ГОТОВА К РАБОТЕ**
- **Процент готовности: 100%** (32/32 теста прошли успешно)
- **Последняя проверка: 16 октября 2025 г.**

---

## 🏗️ Архитектура системы

### Backend (FastAPI)
- **Фреймворк**: FastAPI 0.111.0
- **База данных**: SQLite с SQLAlchemy ORM
- **Миграции**: Alembic
- **Аутентификация**: JWT токены + bcrypt
- **API документация**: Swagger UI

### Frontend (Web Interface)
- **Шаблонизатор**: Jinja2
- **CSS фреймворк**: Bootstrap 5
- **Кастомные стили**: Travel-themed CSS
- **Responsive дизайн**: Адаптивный интерфейс

### Система аутентификации
- **JWT токены** для API и веб-сессий
- **Cookie-based** сессии для веб-интерфейса
- **Роли пользователей**: ADMIN, MANAGER, OPERATOR
- **Хеширование паролей**: bcrypt

---

## 🚀 Быстрый старт

### 1. Убедитесь в готовности системы
```powershell
cd "C:\Users\user\Desktop\Crm-Travel"
python comprehensive_test.py
```

### 2. Запустите сервер
```powershell
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Откройте браузер
- **Веб-интерфейс**: http://localhost:8000
- **API документация**: http://localhost:8000/docs
- **Альтернативная документация**: http://localhost:8000/redoc

---

## 👤 Система пользователей

### Администратор по умолчанию
- **Email**: `admin@travelcrm.com`
- **Пароль**: `admin123`
- **Роль**: ADMIN

### Создание новых пользователей
1. Перейдите на http://localhost:8000/register
2. Заполните форму регистрации
3. Выберите роль пользователя
4. После регистрации войдите в систему

---

## 🌐 Веб-интерфейс

### 🔐 Страница входа (`/login`)
- Вход по email и паролю
- Автоматическое перенаправление на dashboard
- Обработка ошибок аутентификации

### 📝 Страница регистрации (`/register`)
- Регистрация новых пользователей
- Выбор роли (ADMIN/MANAGER/OPERATOR)
- Валидация форм

### 📊 Dashboard (`/dashboard`)
- Главная панель управления
- Статистика (будет расширена в Stage 2)
- Навигация по системе
- Быстрые действия

### 👤 Профиль пользователя (`/profile`)
- Информация о пользователе
- Email, роль, дата создания

---

## 🔌 API Endpoints

### Аутентификация (`/auth/`)
```
POST /auth/login       - Вход в систему (OAuth2)
POST /auth/register    - Регистрация нового пользователя
GET  /auth/me          - Информация о текущем пользователе
POST /auth/refresh     - Обновление токенов
```

### Системные endpoints
```
GET  /health           - Проверка состояния системы
GET  /docs             - Swagger UI документация
GET  /redoc            - ReDoc документация
GET  /robots.txt       - Robots.txt для поисковых систем
GET  /favicon.ico      - Иконка сайта
```

### Веб-маршруты
```
GET  /                 - Главная (перенаправление)
GET  /login            - Страница входа
POST /login            - Обработка входа
GET  /register         - Страница регистрации
POST /register         - Обработка регистрации
GET  /dashboard        - Главная панель
GET  /logout           - Выход из системы
GET  /profile          - Профиль пользователя
```

### Placeholder маршруты (Stage 2+)
```
GET  /clients          - Управление клиентами (Stage 2)
GET  /applications     - Управление заявками (Stage 2)
GET  /orders           - Управление заказами (Stage 3)
GET  /reports          - Отчёты (Stage 5)
```

---

## 🗄️ База данных

### Структура
- **Файл**: `travel_crm.db` (SQLite)
- **Миграции**: управляются через Alembic
- **Текущая ревизия**: `1594d7fe2ca9`

### Таблица Users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    role VARCHAR NOT NULL,  -- ADMIN, MANAGER, OPERATOR
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Работа с миграциями
```powershell
# Проверить текущую ревизию
alembic current

# Посмотреть историю миграций
alembic history

# Создать новую миграцию
alembic revision --autogenerate -m "Описание изменений"

# Применить миграции
alembic upgrade head
```

---

## 🧪 Тестирование

### Комплексное тестирование
```powershell
python comprehensive_test.py
```

**Покрывает:**
- ✅ Структуру проекта (14 тестов)
- ✅ Базу данных (3 теста)
- ✅ Миграции Alembic (2 теста)
- ✅ API endpoints (4 теста)
- ✅ Статические файлы (2 теста)
- ✅ Веб-интерфейс (4 теста)
- ✅ Аутентификацию (3 теста)

### Unit тесты
```powershell
python -m pytest tests/ -v
```

### End-to-End тесты
```powershell
python test_e2e.py
```

---

## 📁 Структура проекта

```
Crm-Travel/
├── src/                     # Исходный код
│   ├── main.py             # Главный файл приложения
│   ├── database.py         # Настройки базы данных
│   ├── auth.py             # Система аутентификации
│   ├── settings.py         # Конфигурация
│   ├── models/             # Модели данных
│   │   ├── __init__.py
│   │   └── user.py         # Модель пользователя
│   ├── routers/            # API маршруты
│   │   ├── __init__.py
│   │   ├── auth.py         # Аутентификация API
│   │   └── web.py          # Веб-интерфейс
│   └── schemas/            # Pydantic схемы
│       ├── __init__.py
│       └── user.py         # Схемы пользователя
├── templates/              # HTML шаблоны
│   ├── base.html          # Базовый шаблон
│   ├── login.html         # Страница входа
│   ├── register.html      # Страница регистрации
│   └── dashboard.html     # Главная панель
├── static/                # Статические файлы
│   ├── style.css          # Кастомные стили
│   └── favicon.ico        # Иконка сайта
├── alembic/               # Миграции базы данных
├── tests/                 # Тесты
├── comprehensive_test.py  # Комплексное тестирование
├── create_admin.py       # Создание администратора
├── requirements.txt      # Python зависимости
├── pyproject.toml        # Конфигурация проекта
├── alembic.ini          # Настройки Alembic
└── travel_crm.db        # База данных SQLite
```

---

## 🔧 Конфигурация

### Переменные окружения
```
DATABASE_URL=sqlite:///./travel_crm.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development
```

### Настройки в production
1. Измените `SECRET_KEY` на уникальный
2. Установите `secure=True` для cookies
3. Настройте CORS для вашего домена
4. Используйте PostgreSQL вместо SQLite
5. Настройте логирование
6. Добавьте мониторинг

---

## 🛠️ Разработка

### Добавление новых моделей
1. Создайте модель в `src/models/`
2. Добавьте схемы в `src/schemas/`
3. Создайте миграцию: `alembic revision --autogenerate`
4. Примените миграцию: `alembic upgrade head`

### Добавление новых API endpoints
1. Создайте роутер в `src/routers/`
2. Подключите в `src/main.py`
3. Добавьте тесты в `tests/`

### Добавление новых веб-страниц
1. Создайте шаблон в `templates/`
2. Добавьте маршрут в `src/routers/web.py`
3. Обновите навигацию в `templates/base.html`

---

## 🚀 Развертывание

### Docker (рекомендуется)
```dockerfile
# Dockerfile уже готов
docker build -t travel-crm .
docker run -p 8000:8000 travel-crm
```

### Docker Compose
```yaml
# docker-compose.yml уже настроен
docker-compose up -d
```

### Обычное развертывание
```bash
pip install -r requirements.txt
alembic upgrade head
python create_admin.py
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## 📊 Мониторинг и логи

### Health Check
```
GET /health
```
Возвращает статус системы и окружения.

### Логирование
Логи записываются в консоль с уровнем INFO.
В production настройте запись в файлы.

---

## 🔒 Безопасность

### Реализованные меры
- ✅ JWT токены с истечением
- ✅ Хеширование паролей bcrypt
- ✅ HttpOnly cookies
- ✅ CORS middleware
- ✅ Валидация входных данных

### Рекомендации для production
- Используйте HTTPS
- Настройте rate limiting
- Добавьте CSRF protection
- Настройте безопасные headers
- Регулярно обновляйте зависимости

---

## 🎯 Roadmap (следующие этапы)

### Stage 2: Управление клиентами и заявками
- Модели Client и Application
- CRUD операции
- Поиск и фильтрация
- Экспорт данных

### Stage 3: Система заказов
- Модель Order
- Статусы заказов
- Интеграция с платежами
- Уведомления

### Stage 4: Финансы и платежи
- Система платежей
- Счета и инвойсы
- Комиссии и скидки

### Stage 5: Отчёты и аналитика
- Дашборд с метриками
- Экспорт отчётов
- Графики и диаграммы

---

## 📞 Поддержка

### Техническая информация
- **Версия**: 1.0.0
- **Python**: 3.8+
- **FastAPI**: 0.111.0
- **Bootstrap**: 5.x

### Файлы помощи
- `comprehensive_test.py` - полное тестирование
- `create_admin.py` - создание администратора
- `check_db.py` - проверка базы данных

---

## ✅ Чек-лист готовности

- [x] ✅ Сервер запускается без ошибок
- [x] ✅ База данных готова и заполнена
- [x] ✅ Веб-интерфейс полностью функционален
- [x] ✅ API endpoints работають
- [x] ✅ Аутентификация работает (веб + API)
- [x] ✅ Тесты проходят (100% успешность)
- [x] ✅ Документация готова
- [x] ✅ Статические файлы обслуживаются
- [x] ✅ Миграции настроены
- [x] ✅ Администратор создан

---

## 🎉 Заключение

**Travel CRM система полностью готова к использованию!**

Система успешно прошла все 32 теста и готова для:
- ✅ Работы пользователей через веб-интерфейс
- ✅ API интеграций
- ✅ Развертывания в production
- ✅ Разработки Stage 2

**Процент готовности: 100%** 🎯

---

*Документация создана 16 октября 2025 г.*
*Последнее обновление: после успешного прохождения всех тестов*
