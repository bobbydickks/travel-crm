# 🚂 Развертывание на Railway

## Шаги развертывания:

### 1. Подготовка проекта

Убедитесь, что в корне проекта есть:
- `requirements.txt` ✅
- `Dockerfile` ✅
- Файл `railway.json` (создадим)

### 2. Создайте файл railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "python create_admin.py && alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health"
  }
}
```

### 3. Настройка переменных окружения

В Railway добавьте переменные:
```
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=sqlite:///./travel_crm.db
ENVIRONMENT=production
```

### 4. Ссылки

1. Перейдите на https://railway.app
2. Войдите через GitHub
3. Нажмите "New Project"
4. Выберите "Deploy from GitHub repo"
5. Выберите ваш репозitorий с проектом

### 5. После развертывания

Railway автоматически даст вам ссылку вида:
`https://your-project-name.railway.app`

Эту ссылку можно дать клиенту!

### 6. Логи и мониторинг

В панели Railway вы сможете:
- Смотреть логи приложения
- Перезапускать сервис
- Настраивать домен
- Мониторить использование ресурсов
