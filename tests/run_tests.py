"""
Главный файл для запуска всех интеграционных тестов
"""
import pytest
import asyncio
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Переопределяем конфигурацию базы данных для тестов
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"


def run_basic_tests():
    """Запуск базовых тестов API"""
    print("🚀 Запуск базовых тестов API...")
    pytest.main([
        "tests/test_basic_api.py",
        "-v",  # Подробный вывод
        "--tb=short",  # Короткий traceback
        "--asyncio-mode=auto",  # Автоматический режим asyncio
        "--disable-warnings",  # Отключение предупреждений
        "-s" # debug print
    ])


def run_all_tests():
    """Запуск всех тестов (может не работать из-за проблем с UUID в SQLite)"""
    print("🚀 Запуск всех интеграционных тестов...")
    pytest.main([
        "tests/",
        "-v",  # Подробный вывод
        "--tb=short",  # Короткий traceback
        "--asyncio-mode=auto",  # Автоматический режим asyncio
        "--disable-warnings",  # Отключение предупреждений
    ])


if __name__ == "__main__":
    # run_basic_tests()
    run_all_tests()
