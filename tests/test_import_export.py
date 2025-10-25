"""
Интеграционные тесты для экспорта и импорта закладок
"""
import sys
import os
import pytest
import json
import base64
from httpx import AsyncClient

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestExport:
    """Тесты для экспорта закладок"""
    
    async def test_export_unauthorized(self, client: AsyncClient):
        """Тест экспорта без авторизации"""
        response = await client.get("/export/json")
        
        assert response.status_code == 403
    
    async def test_export_json_empty(self, client: AsyncClient, auth_headers):
        """Тест экспорта пустого списка в JSON"""
        response = await client.get("/export/json", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "bookmarks" in data
        assert data["bookmarks"] == []
    
    async def test_export_json_with_data(self, client: AsyncClient, auth_headers, multiple_bookmarks):
        """Тест экспорта закладок в JSON"""
        response = await client.get("/export/json", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "bookmarks" in data
        assert len(data["bookmarks"]) == 5
        
        # Проверяем структуру экспортированной закладки
        bookmark = data["bookmarks"][0]
        assert "id" in bookmark
        assert "url" in bookmark
        assert "title" in bookmark
        assert "description" in bookmark
        assert "access_level" in bookmark
        assert "status" in bookmark
        assert "created_at" in bookmark
        assert "updated_at" in bookmark
    
    async def test_export_html_empty(self, client: AsyncClient, auth_headers):
        """Тест экспорта пустого списка в HTML"""
        response = await client.get("/export/html", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        
        content = response.text
        assert "Bookmarks Export" in content
        assert "Total bookmarks: 0" in content
    
    async def test_export_html_with_data(self, client: AsyncClient, auth_headers, multiple_bookmarks):
        """Тест экспорта закладок в HTML"""
        response = await client.get("/export/html", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        
        content = response.text
        assert "Bookmarks Export" in content
        assert "Total bookmarks: 5" in content
        
        # Проверяем наличие закладок в HTML
        for i in range(5):
            assert f"Test Bookmark {i}" in content
            assert f"https://example{i}.com" in content
    
    async def test_export_csv_empty(self, client: AsyncClient, auth_headers):
        """Тест экспорта пустого списка в CSV"""
        response = await client.get("/export/csv", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        
        content = response.text
        assert "Title,URL,Description,Status,Access Level,Created At,Updated At" in content
    
    async def test_export_csv_with_data(self, client: AsyncClient, auth_headers, multiple_bookmarks):
        """Тест экспорта закладок в CSV"""
        response = await client.get("/export/csv", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        
        content = response.text
        lines = content.strip().split('\n')
        
        # Проверяем заголовок
        assert "Title,URL,Description,Status,Access Level,Created At,Updated At" in lines[0]
        
        # Проверяем количество строк данных
        assert len(lines) == 6  # 1 заголовок + 5 закладок
        
        # Проверяем наличие данных закладок
        for i in range(5):
            assert f"Test Bookmark {i}" in content
            assert f"https://example{i}.com" in content
    
    async def test_export_unsupported_format(self, client: AsyncClient, auth_headers):
        """Тест экспорта в неподдерживаемом формате"""
        response = await client.get("/export/xml", headers=auth_headers)
        
        assert response.status_code == 400
        assert "Unsupported export format" in response.json()["detail"]


class TestImport:
    """Тесты для импорта закладок"""
    
    async def test_import_unauthorized(self, client: AsyncClient):
        """Тест импорта без авторизации"""
        import_data = {
            "format": "json",
            "data": json.dumps({"bookmarks": []})
        }
        
        response = await client.post("/import/json", json=import_data)
        
        assert response.status_code == 403
    
    async def test_import_json_success(self, client: AsyncClient, auth_headers):
        """Тест успешного импорта JSON"""
        bookmarks_data = {
            "bookmarks": [
                {
                    "url": "https://imported1.com",
                    "title": "Imported Bookmark 1",
                    "description": "Imported description 1",
                    "access_level": "private"
                },
                {
                    "url": "https://imported2.com",
                    "title": "Imported Bookmark 2",
                    "description": "Imported description 2",
                    "access_level": "public"
                }
            ]
        }
        
        import_data = {
            "format": "json",
            "data": json.dumps(bookmarks_data)
        }
        
        response = await client.post("/import/json", json=import_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["imported_count"] == 2
        assert data["failed_count"] == 0
        assert data["errors"] == []
        
        # Проверяем, что закладки действительно импортированы
        response = await client.get("/bookmarks/", headers=auth_headers)
        bookmarks = response.json()["bookmarks"]
        
        assert len(bookmarks) == 2
        assert bookmarks[0]["title"] == "Imported Bookmark 1"
        assert bookmarks[1]["title"] == "Imported Bookmark 2"
    
    async def test_import_json_array_format(self, client: AsyncClient, auth_headers):
        """Тест импорта JSON в формате массива"""
        bookmarks_data = [
            {
                "url": "https://array1.com",
                "title": "Array Bookmark 1"
            },
            {
                "url": "https://array2.com",
                "title": "Array Bookmark 2"
            }
        ]
        
        import_data = {
            "format": "json",
            "data": json.dumps(bookmarks_data)
        }
        
        response = await client.post("/import/json", json=import_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["imported_count"] == 2
        assert data["failed_count"] == 0
    
    async def test_import_json_single_bookmark(self, client: AsyncClient, auth_headers):
        """Тест импорта одной закладки в JSON"""
        bookmark_data = {
            "url": "https://single.com",
            "title": "Single Bookmark"
        }
        
        import_data = {
            "format": "json",
            "data": json.dumps(bookmark_data)
        }
        
        response = await client.post("/import/json", json=import_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["imported_count"] == 1
        assert data["failed_count"] == 0
    
    async def test_import_json_with_errors(self, client: AsyncClient, auth_headers):
        """Тест импорта JSON с ошибками"""
        bookmarks_data = {
            "bookmarks": [
                {
                    "url": "https://valid.com",
                    "title": "Valid Bookmark"
                },
                {
                    "url": "invalid-url",  # Невалидный URL
                    "title": "Invalid Bookmark"
                },
                {
                    "title": "Missing URL"  # Отсутствует URL
                }
            ]
        }
        
        import_data = {
            "format": "json",
            "data": json.dumps(bookmarks_data)
        }
        
        response = await client.post("/import/json", json=import_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["imported_count"] == 1
        assert data["failed_count"] == 2
        assert len(data["errors"]) == 2
    
    async def test_import_json_invalid_format(self, client: AsyncClient, auth_headers):
        """Тест импорта невалидного JSON"""
        import_data = {
            "format": "json",
            "data": "invalid json"
        }
        
        response = await client.post("/import/json", json=import_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Invalid JSON format" in response.json()["detail"]
    
    async def test_import_html_success(self, client: AsyncClient, auth_headers):
        """Тест успешного импорта HTML"""
        html_content = """
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
        <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
        <TITLE>Bookmarks</TITLE>
        <H1>Bookmarks</H1>
        <DL><p>
            <DT><A HREF="https://html1.com">HTML Bookmark 1</A>
            <DT><A HREF="https://html2.com">HTML Bookmark 2</A>
        </DL><p>
        """
        
        import_data = {
            "format": "html",
            "data": html_content
        }
        
        response = await client.post("/import/html", json=import_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["imported_count"] == 2
        assert data["failed_count"] == 0
        
        # Проверяем импортированные закладки
        response = await client.get("/bookmarks/", headers=auth_headers)
        bookmarks = response.json()["bookmarks"]
        
        assert len(bookmarks) == 2
        assert bookmarks[0]["title"] == "HTML Bookmark 1"
        assert bookmarks[1]["title"] == "HTML Bookmark 2"
    
    async def test_import_csv_success(self, client: AsyncClient, auth_headers):
        """Тест успешного импорта CSV"""
        csv_content = """Title,URL,Description,Access Level
CSV Bookmark 1,https://csv1.com,CSV Description 1,private
CSV Bookmark 2,https://csv2.com,CSV Description 2,public"""
        
        import_data = {
            "format": "csv",
            "data": csv_content
        }
        
        response = await client.post("/import/csv", json=import_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["imported_count"] == 2
        assert data["failed_count"] == 0
        
        # Проверяем импортированные закладки
        response = await client.get("/bookmarks/", headers=auth_headers)
        bookmarks = response.json()["bookmarks"]
        
        assert len(bookmarks) == 2
        assert bookmarks[0]["title"] == "CSV Bookmark 1"
        assert bookmarks[1]["title"] == "CSV Bookmark 2"
    
    async def test_import_csv_missing_required_field(self, client: AsyncClient, auth_headers):
        """Тест импорта CSV с отсутствующим обязательным полем"""
        csv_content = """Title,Description,Access Level
CSV Bookmark 1,CSV Description 1,private"""
        
        import_data = {
            "format": "csv",
            "data": csv_content
        }
        
        response = await client.post("/import/csv", json=import_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["imported_count"] == 0
        assert data["failed_count"] == 1
        assert len(data["errors"]) == 1
    
    async def test_import_unsupported_format(self, client: AsyncClient, auth_headers):
        """Тест импорта в неподдерживаемом формате"""
        import_data = {
            "format": "xml",
            "data": "<bookmarks></bookmarks>"
        }
        
        response = await client.post("/import/xml", json=import_data, headers=auth_headers)

        print(response.text)

        assert response.status_code == 422
        assert "String should match pattern" in response.json()["detail"][0]["msg"]
    
    async def test_import_base64_data(self, client: AsyncClient, auth_headers):
        """Тест импорта с base64 данными"""
        bookmarks_data = {
            "bookmarks": [
                {
                    "url": "https://base64.com",
                    "title": "Base64 Bookmark"
                }
            ]
        }
        
        json_data = json.dumps(bookmarks_data)
        base64_data = base64.b64encode(json_data.encode()).decode()
        
        import_data = {
            "format": "json",
            "data": f"data:application/json;base64,{base64_data}"
        }
        
        response = await client.post("/import/json", json=import_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["imported_count"] == 1
        assert data["failed_count"] == 0
    
    async def test_import_missing_fields(self, client: AsyncClient, auth_headers):
        """Тест импорта с отсутствующими полями"""
        # Без format
        response = await client.post("/import/json", json={"data": "test"}, headers=auth_headers)
        assert response.status_code == 422
        
        # Без data
        response = await client.post("/import/json", json={"format": "json"}, headers=auth_headers)
        assert response.status_code == 422
