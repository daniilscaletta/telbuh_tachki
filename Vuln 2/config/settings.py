import os
from typing import Optional
from dotenv import load_dotenv

# Завантаження змінних середовища з .env файлу
load_dotenv()

class Settings:
    """Налаштування додатку"""
    
    # Основні налаштування
    APP_NAME: str = "Система управління енергосистемою України"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Налаштування сервера
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "9000"))
    
    # Налаштування бази даних
    DATABASE_URL: str = os.getenv("DATABASE_URL", "energy_system.db")
    
    # Налаштування безпеки
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ukr_energy_system_2024_secret_key")
    
    # Налаштування шаблонів
    TEMPLATES_DIR: str = "templates"
    STATIC_DIR: str = "app/static"
    
    # Системний флаг
    TASK_FLAG_NAME: str = "TASK_COMPLETED"
    TASK_FLAG_VALUE: str = "UKR_ENERGY_SYSTEM_2024"
    
    @classmethod
    def get_database_path(cls) -> str:
        """Отримати шлях до бази даних"""
        return cls.DATABASE_URL

settings = Settings()
