# Интеграционные тесты для Bookmark Management Service

## ✅ Статус: РАБОТАЕТ!

Интеграционные тесты успешно созданы и работают. Базовые тесты проверяют работоспособность всех эндпоинтов API.

## 🚀 Быстрый запуск

```bash
python3 tests/run_tests.py
```

## 📋 Результаты тестирования

## 🎯 Покрываемые эндпоинты

### ✅ Аутентификация (`/auth`)
- `POST /auth/register` - Регистрация пользователя
- `POST /auth/login` - Вход пользователя

### ✅ Закладки (`/bookmarks`)
- `GET /bookmarks/` - Получение списка с пагинацией
- `POST /bookmarks/` - Создание закладки
- `PUT /bookmarks/{id}` - Обновление закладки
- `DELETE /bookmarks/{id}` - Удаление закладки

### ✅ Экспорт (`/export`)
- `GET /export/json` - Экспорт в JSON
- `GET /export/html` - Экспорт в HTML
- `GET /export/csv` - Экспорт в CSV

### ✅ Импорт (`/import`)
- `POST /import/json` - Импорт из JSON
- `POST /import/html` - Импорт из HTML
- `POST /import/csv` - Импорт из CSV

### ✅ Базовые эндпоинты
- `GET /` - Корневой эндпоинт
- `GET /docs` - Swagger документация
- `GET /redoc` - ReDoc документация

## 🧪 Структура тестов

```
tests/
├── test_basic_api.py
├── conftest_basic.py          
├── test_auth.py
├── test_bookmarks.py
├── test_import_export.py     
├── test_base.py     
├── test_limits.py        
├── test_security_performance.py 
├── run_tests.py           
├── requirements.txt        
└── test_models.py            
```

## 🔧 Установка и запуск

### 1. Автоматический запуск
```bash
./run_integration_tests.sh
```

### 2. Ручная установка
```bash
# Создание виртуального окружения
python3 -m venv test_env
source test_env/bin/activate

# Установка зависимостей
pip install -r tests/requirements.txt
pip install fastapi sqlalchemy passlib bcrypt==4.0.1 python-jose python-multipart pydantic pydantic-settings email-validator greenlet

# Запуск тестов
python tests/run_tests.py
```

### 3. Запуск конкретных тестов
```bash
# Только базовые тесты
pytest tests/test_basic_api.py -v

# Все тесты 
pytest tests/ -v
```

