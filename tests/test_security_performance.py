"""
Интеграционные тесты для безопасности и производительности
"""
import sys
import os
import pytest
import asyncio
import json
import time
from httpx import AsyncClient
from uuid import uuid4

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSecurity:
    """Тесты безопасности"""
    
    async def test_sql_injection_protection(self, client: AsyncClient, auth_headers):
        """Тест защиты от SQL инъекций"""
        # Попытка SQL инъекции в параметрах запроса
        malicious_params = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'hacker@evil.com', 'password'); --"
        ]
        
        for param in malicious_params:
            response = await client.get(f"/bookmarks/?limit={param}", headers=auth_headers)
            # Должен вернуть ошибку валидации, а не выполнить SQL
            assert response.status_code in [422, 400]
    

    
    async def test_token_tampering(self, client: AsyncClient, auth_headers):
        """Тест защиты от подделки токенов"""
        # Подделанный токен
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        fake_headers = {"Authorization": f"Bearer {fake_token}"}
        
        response = await client.get("/bookmarks/", headers=fake_headers)
        assert response.status_code == 401


class TestPerformance:
    """Тесты производительности"""    
    async def test_response_time(self, client: AsyncClient, auth_headers):
        """Тест времени ответа API"""
        import time
        
        # Тест времени ответа для получения закладок
        start_time = time.time()
        response = await client.get("/bookmarks/", headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Ответ должен быть быстрее 1 секунды
        
        # Тест времени ответа для создания закладки
        bookmark_data = {
            "url": "https://performance.com",
            "title": "Performance Test"
        }
        
        start_time = time.time()
        response = await client.post("/bookmarks/", json=bookmark_data, headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 201
        assert (end_time - start_time) < 1.0


class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    async def test_invalid_json_format(self, client: AsyncClient, auth_headers):
        """Тест обработки невалидного JSON"""
        response = await client.post(
            "/bookmarks/",
            json={"invalid": "json"},
            headers=auth_headers
        )
        
        # Должен вернуть ошибку валидации
        assert response.status_code == 422
    
    async def test_malformed_requests(self, client: AsyncClient, auth_headers):
        """Тест обработки некорректных запросов"""
        # Пустое тело запроса
        response = await client.post("/bookmarks/", json={}, headers=auth_headers)
        assert response.status_code == 422
        
        # Неправильный Content-Type
        response = await client.post(
            "/bookmarks/",
            data="not json",
            headers={**auth_headers, "Content-Type": "text/plain"}
        )
        assert response.status_code == 422
    
    async def test_rate_limiting_simulation(self, client: AsyncClient, auth_headers):
        """Тест симуляции ограничения скорости (если реализовано)"""
        # Отправляем много запросов подряд
        for i in range(100):
            bookmark_data = {
                "url": f"https://rate{i}.com",
                "title": f"Rate Test {i}"
            }
            
            response = await client.post("/bookmarks/", json=bookmark_data, headers=auth_headers)
            
            # Если есть rate limiting, некоторые запросы могут быть отклонены
            # Но для текущей реализации все должны проходить
            assert response.status_code in [201, 429]  # 429 - Too Many Requests
