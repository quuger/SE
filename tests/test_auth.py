"""
Интеграционные тесты для аутентификации
"""
import sys
import os
import pytest
from httpx import AsyncClient

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas import AuthRequest


class TestAuthentication:
    """Тесты для эндпоинтов аутентификации"""
    
    async def test_register_success(self, client: AsyncClient):
        """Тест успешной регистрации пользователя"""
        user_data = {
            "email": "newuser@example.com",
            "password": "pass123",
            "username": "newuser"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Проверяем структуру ответа
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        
        # Проверяем данные пользователя
        user = data["user"]
        assert user["email"] == user_data["email"]
        assert user["username"] == user_data["username"]
        assert user["account_type"] == "free"
        assert "id" in user
        assert "created_at" in user
        
        # Проверяем токены
        assert data["access_token"] is not None
        assert data["refresh_token"] is not None
    
    async def test_register_without_username(self, client: AsyncClient):
        """Тест регистрации без указания username (должен генерироваться из email)"""
        user_data = {
            "email": "autouser@example.com",
            "password": "pass123"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        user = data["user"]
        assert user["username"] == "autouser"  # Из email autouser@example.com
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Тест регистрации с уже существующим email"""
        user_data = {
            "email": test_user.email,
            "password": "pass123",
            "username": "differentuser"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Тест регистрации с уже существующим username"""
        user_data = {
            "email": "different@example.com",
            "password": "pass123",
            "username": test_user.username
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 409
        assert "Username already taken" in response.json()["detail"]
    
    async def test_register_invalid_email(self, client: AsyncClient):
        """Тест регистрации с невалидным email"""
        user_data = {
            "email": "invalid-email",
            "password": "pass123",
            "username": "testuser"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    async def test_register_short_password(self, client: AsyncClient):
        """Тест регистрации с коротким паролем"""
        user_data = {
            "email": "test@example.com",
            "password": "123",
            "username": "testuser"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    async def test_register_short_username(self, client: AsyncClient):
        """Тест регистрации с коротким username"""
        user_data = {
            "email": "test@example.com",
            "password": "pass123",
            "username": "ab"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    async def test_login_success(self, client: AsyncClient, test_user):
        """Тест успешного входа"""
        login_data = {
            "email": test_user.email,
            "password": "pass123"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем структуру ответа
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        
        # Проверяем данные пользователя
        user = data["user"]
        assert user["email"] == test_user.email
        assert user["username"] == test_user.username
        assert user["id"] == str(test_user.id)
    
    async def test_login_wrong_email(self, client: AsyncClient):
        """Тест входа с неверным email"""
        login_data = {
            "email": "wrong@example.com",
            "password": "pass123"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Тест входа с неверным паролем"""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    async def test_login_invalid_email_format(self, client: AsyncClient):
        """Тест входа с невалидным форматом email"""
        login_data = {
            "email": "invalid-email",
            "password": "pass123"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 422
    
    async def test_login_short_password(self, client: AsyncClient):
        """Тест входа с коротким паролем"""
        login_data = {
            "email": "test@example.com",
            "password": "123"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 422
    
    async def test_login_missing_fields(self, client: AsyncClient):
        """Тест входа с отсутствующими полями"""
        # Без email
        response = await client.post("/auth/login", json={"password": "pass123"})
        assert response.status_code == 422
        
        # Без password
        response = await client.post("/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422
    
    async def test_register_missing_fields(self, client: AsyncClient):
        """Тест регистрации с отсутствующими полями"""
        # Без email
        response = await client.post("/auth/register", json={
            "password": "pass123",
            "username": "testuser"
        })
        assert response.status_code == 422
        
        # Без password
        response = await client.post("/auth/register", json={
            "email": "test@example.com",
            "username": "testuser"
        })
        assert response.status_code == 422
