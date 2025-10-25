"""
Простой тест для проверки основных эндпоинтов
"""
import sys
import os
import pytest
from httpx import AsyncClient

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Переопределяем конфигурацию базы данных для тестов
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app


class TestBasicEndpoints:
    """Базовые тесты для проверки работоспособности API"""
    
    async def test_root_endpoint(self, client: AsyncClient):
        """Тест корневого эндпоинта"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Welcome to the Authentication API" in data["message"]
    
    async def test_openapi_docs(self, client: AsyncClient):
        """Тест доступности OpenAPI документации"""
        response = await client.get("/docs")
        assert response.status_code == 200
        
        response = await client.get("/redoc")
        assert response.status_code == 200
    
    async def test_openapi_json(self, client: AsyncClient):
        """Тест доступности OpenAPI JSON схемы"""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        assert "openapi" in openapi_data
        assert "info" in openapi_data
        assert "paths" in openapi_data
    
    async def test_cors_headers(self, client: AsyncClient):
        """Тест CORS заголовков"""
        response = await client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        
        # CORS заголовки должны присутствовать
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        # access-control-allow-headers может отсутствовать в некоторых конфигурациях
    
    async def test_register_endpoint_exists(self, client: AsyncClient):
        """Тест существования эндпоинта регистрации"""
        # Проверяем, что эндпоинт существует (должен вернуть ошибку валидации, а не 404)
        response = await client.post("/auth/register", json={})
        assert response.status_code == 422  # Ошибка валидации, а не 404
    
    async def test_login_endpoint_exists(self, client: AsyncClient):
        """Тест существования эндпоинта входа"""
        # Проверяем, что эндпоинт существует (должен вернуть ошибку валидации, а не 404)
        response = await client.post("/auth/login", json={})
        assert response.status_code == 422  # Ошибка валидации, а не 404
    
    async def test_bookmarks_endpoint_exists(self, client: AsyncClient):
        """Тест существования эндпоинта закладок"""
        # Проверяем, что эндпоинт существует (должен вернуть ошибку авторизации, а не 404)
        response = await client.get("/bookmarks/")
        assert response.status_code in [401, 403]  # Ошибка авторизации, а не 404
    
    async def test_export_endpoint_exists(self, client: AsyncClient):
        """Тест существования эндпоинта экспорта"""
        # Проверяем, что эндпоинт существует (должен вернуть ошибку авторизации, а не 404)
        response = await client.get("/export/json")
        assert response.status_code in [401, 403]  # Ошибка авторизации, а не 404
    
    async def test_import_endpoint_exists(self, client: AsyncClient):
        """Тест существования эндпоинта импорта"""
        # Проверяем, что эндпоинт существует (должен вернуть ошибку авторизации, а не 404)
        response = await client.post("/import/json", json={})
        assert response.status_code in [401, 403]  # Ошибка авторизации, а не 404
    
    async def test_invalid_endpoint_returns_404(self, client: AsyncClient):
        """Тест несуществующего эндпоинта"""
        response = await client.get("/nonexistent")
        assert response.status_code == 404
    
    async def test_api_structure(self, client: AsyncClient):
        """Тест структуры API"""
        response = await client.get("/openapi.json")
        openapi_data = response.json()
        
        # Проверяем наличие основных путей
        paths = openapi_data["paths"]
        
        # Основные эндпоинты должны существовать
        assert "/" in paths
        assert "/auth/register" in paths
        assert "/auth/login" in paths
        assert "/bookmarks/" in paths
        assert "/export/{format}" in paths
        assert "/import/{format}" in paths
        
        # Проверяем методы
        assert "get" in paths["/"]
        assert "post" in paths["/auth/register"]
        assert "post" in paths["/auth/login"]
        assert "get" in paths["/bookmarks/"]
        assert "post" in paths["/bookmarks/"]
        assert "get" in paths["/export/{format}"]
        assert "post" in paths["/import/{format}"]
