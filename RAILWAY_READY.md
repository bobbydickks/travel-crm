# 🚀 Travel CRM - Готов к развертыванию на Railway!

## ✅ Проект подготовлен и готов к загрузке

### Что уже сделано:
- ✅ Git репозиторий инициализирован
- ✅ Все файлы добавлены и закоммичены  
- ✅ Система прав полностью реализована
- ✅ Конфигурация для Railway готова
- ✅ Dockerfile оптимизирован для production

## 🔗 Следующие шаги:

### 1. Создайте репозиторий на GitHub
1. Перейдите на https://github.com
2. Нажмите "New repository"
3. Назовите репозиторий: `travel-crm` 
4. Выберите "Public" 
5. НЕ добавляйте README, .gitignore (уже есть)
6. Нажмите "Create repository"

### 2. Загрузите код на GitHub
Выполните команды из GitHub (они будут примерно такие):

```powershell
git remote add origin https://github.com/ВАШ-USERNAME/travel-crm.git
git push -u origin main
```

### 3. Разверните на Railway
1. Перейдите на https://railway.app
2. Войдите через GitHub
3. Нажмите "New Project"
4. Выберите "Deploy from GitHub repo"
5. Выберите репозиторий `travel-crm`
6. Railway автоматически обнаружит Dockerfile и railway.json

### 4. Настройте переменные окружения в Railway
Добавьте эти переменные в настройках проекта:

```
SECRET_KEY=super-secret-key-change-this-in-production-123456789
DATABASE_URL=sqlite:///./travel_crm.db
ENVIRONMENT=production
```

### 5. Получите публичную ссылку
После успешного развертывания Railway даст вам ссылку вида:
`https://travel-crm-production-XXXX.up.railway.app`

## 🎯 Доступ к системе:

- **Email**: admin@travelcrm.com
- **Пароль**: admin123
- **Роль**: ADMIN (полные права)

## 📋 Что получит клиент:

✅ **Веб-интерфейс**: ваша-ссылка.railway.app
✅ **API документация**: ваша-ссылка.railway.app/docs  
✅ **Система прав** с 4 уровнями доступа
✅ **Безопасная аутентификация** (JWT + HTTP-only cookies)
✅ **HTTPS** соединение из коробки
✅ **Готовый аккаунт администратора**

## ⏱️ Время развертывания: 5-10 минут

После выполнения этих шагов у вас будет рабочая ссылка для клиента!
