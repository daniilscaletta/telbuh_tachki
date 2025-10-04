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
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )