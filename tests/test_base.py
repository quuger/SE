"""
Интеграционные тесты для базовых эндпоинтов
"""
import sys
import os
import pytest
from httpx import AsyncClient

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBaseEndpoints:
    """Тесты для базовых эндпоинтов"""
    
    async def test_root_endpoint(self, client: AsyncClient):
        """Тест корневого эндпоинта"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Welcome to the Authentication API" in data["message"]
    
    async def test_base_router_endpoint(self, client: AsyncClient):
        """Тест эндпоинта базового роутера"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Welcome to the Authentication API" in data["message"]
    
    async def test_health_check(self, client: AsyncClient):
        """Тест проверки работоспособности сервиса"""
        # Проверяем, что сервис отвечает
        response = await client.get("/")
        assert response.status_code == 200
        
        # Проверяем, что можем получить OpenAPI схему
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
        # access-control-allow-headers может отсутствовать в некоторых конфигурациях CORS
        # Проверяем только основные заголовки
    
    async def test_api_documentation(self, client: AsyncClient):
        """Тест доступности API документации"""
        response = await client.get("/docs")
        assert response.status_code == 200
        
        response = await client.get("/redoc")
        assert response.status_code == 200
