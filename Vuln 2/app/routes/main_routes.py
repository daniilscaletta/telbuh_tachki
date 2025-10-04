from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database.database import DatabaseManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
db = DatabaseManager()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница системы управления энергосистемой"""
    stats = db.get_system_statistics()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats
    })

@router.get("/stations", response_class=HTMLResponse)
async def stations_page(request: Request):
    """Страница с информацией об электростанциях"""
    stations = db.get_all_stations()
    stats = db.get_system_statistics()
    return templates.TemplateResponse("stations.html", {
        "request": request, 
        "stations": stations,
        "stats": stats
    })

@router.get("/consumption", response_class=HTMLResponse)
async def consumption_page(request: Request):
    """Страница с данными о потреблении энергии"""
    consumption = db.get_all_consumption()
    stats = db.get_system_statistics()
    return templates.TemplateResponse("consumption.html", {
        "request": request, 
        "consumption": consumption,
        "stats": stats
    })

@router.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    """Страница с системными уведомлениями"""
    alerts = db.get_all_alerts()
    return templates.TemplateResponse("alerts.html", {
        "request": request, 
        "alerts": alerts
    })