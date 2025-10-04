from fastapi import APIRouter
from app.database.database import DatabaseManager

router = APIRouter()
db = DatabaseManager()

@router.get("/api/stations")
async def api_stations():
    """API endpoint для получения списка станций"""
    stations = db.get_all_stations()
    return {"stations": stations}

@router.get("/api/consumption")
async def api_consumption():
    """API endpoint для получения данных потребления"""
    consumption = db.get_all_consumption()
    return {"consumption": consumption}

@router.get("/api/alerts")
async def api_alerts():
    """API endpoint для получения уведомлений"""
    alerts = db.get_all_alerts()
    return {"alerts": alerts}

@router.get("/api/statistics")
async def api_statistics():
    """API endpoint для получения статистики системы"""
    stats = db.get_system_statistics()
    return {"statistics": stats}

@router.get("/api/schema")
async def api_schema():
    """API endpoint для получения схемы базы данных"""
    schema = db.get_database_schema()
    return {"schema": schema}

@router.get("/api/tables")
async def api_tables():
    """API endpoint для получения списка таблиц"""
    schema = db.get_database_schema()
    return {"tables": list(schema.keys())}

