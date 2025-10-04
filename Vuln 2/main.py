#!/usr/bin/env python3
"""
Главный файл системы управления энергосистемой Украины
"""

import sys
import os

# Добавление текущей директории к пути
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from config.settings import settings

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Запуск {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📍 Сервер: http://{settings.HOST}:{settings.PORT}")
    print(f"🔧 Debug режим: {'Включен' if settings.DEBUG else 'Выключен'}")
    print("⚠️  ВНИМАНИЕ: Это демонстрационный проект с учебными уязвимостями!")
    print("🔓 Для получения флага используйте SQL injection уязвимость")
    print("📖 Инструкция: http://localhost:9000/search")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )