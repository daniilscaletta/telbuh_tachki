from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sys

# Додавання поточної директорії до шляху
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Імпорт налаштувань
from config.settings import settings

# Імпорт маршрутів
from app.routes import main_routes, search_routes, api_routes

# Створення FastAPI додатку
app = FastAPI(
    title=settings.APP_NAME,
    description="Демонстраційний проект з навчальними уразливостями",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Підключення статичних файлів
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Підключення маршрутів
app.include_router(main_routes.router)
app.include_router(search_routes.router)
app.include_router(api_routes.router)

@app.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    return {"status": "healthy", "service": "energy_system"}

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
