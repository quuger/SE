"""
Интеграционные тесты для лимитов бесплатных аккаунтов
"""
import sys
import os
import pytest
from httpx import AsyncClient

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import User, AccountType
from app.auth import get_password_hash
import uuid


class TestFreeAccountLimits:
    """Тесты для лимитов бесплатных аккаунтов"""
    
    async def test_bookmark_limit_free_account(self, client: AsyncClient, auth_headers):
        """Тест лимита закладок для бесплатного аккаунта"""
        # Создаем 100 закладок (лимит для бесплатного аккаунта)
        for i in range(100):
            bookmark_data = {
                "url": f"https://limit{i}.com",
                "title": f"Limit Bookmark {i}"
            }
            
            response = await client.post("/bookmarks/", json=bookmark_data, headers=auth_headers)
            assert response.status_code == 201
        
        # Попытка создать 101-ю закладку должна завершиться ошибкой
        bookmark_data = {
            "url": "https://limit101.com",
            "title": "Limit Bookmark 101"
        }
        
        response = await client.post("/bookmarks/", json=bookmark_data, headers=auth_headers)
        assert response.status_code == 400
        assert "Bookmark limit exceeded for free account" in response.json()["detail"]
    
    async def test_import_limit_free_account(self, client: AsyncClient, auth_headers):
        """Тест лимита импорта для бесплатного аккаунта"""
        # Создаем 100 закладок
        for i in range(100):
            bookmark_data = {
                "url": f"https://limit{i}.com",
                "title": f"Limit Bookmark {i}"
            }
            
            response = await client.post("/bookmarks/", json=bookmark_data, headers=auth_headers)
            assert response.status_code == 201
        
        # Попытка импорта должна завершиться ошибкой
        import_data = {
            "format": "json",
            "data": '{"bookmarks": [{"url": "https://import.com", "title": "Import Bookmark"}]}'
        }
        
        response = await client.post("/import/json", json=import_data, headers=auth_headers)
        assert response.status_code == 400
        assert "Import limit exceeded for free account" in response.json()["detail"]
    
    async def test_premium_account_no_limits(self, client: AsyncClient, test_db):
        """Тест отсутствия лимитов для премиум аккаунта"""
        # Создаем премиум пользователя
        premium_user = User(
            id=uuid.uuid4(),
            username="premiumuser",
            email="premium@example.com",
            hashed_password=get_password_hash("pass123"),
            account_type=AccountType.PREMIUM
        )
        
        test_db.add(premium_user)
        await test_db.commit()
        await test_db.refresh(premium_user)
        
        # Логинимся как премиум пользователь
        login_data = {
            "email": premium_user.email,
            "password": "pass123"
        }
        
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        premium_auth_headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
        
        # Создаем больше 100 закладок
        for i in range(105):
            bookmark_data = {
                "url": f"https://premium{i}.com",
                "title": f"Premium Bookmark {i}"
            }
            
            response = await client.post("/bookmarks/", json=bookmark_data, headers=premium_auth_headers)
            assert response.status_code == 201
        
        # Проверяем, что все закладки созданы
        response = await client.get("/bookmarks/", headers=premium_auth_headers)
        assert response.status_code == 200
        assert response.json()["total_count"] == 105
