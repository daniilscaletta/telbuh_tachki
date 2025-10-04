from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.database import DatabaseManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
db = DatabaseManager()

@router.get("/search", response_class=HTMLResponse)
async def search_form(request: Request):
    """Форма поиска электростанций"""
    return templates.TemplateResponse("search.html", {"request": request})

@router.post("/search")
async def search_stations(
    request: Request,
    query: str = Form(...)
):
    """
    УЯЗВИМЫЙ ENDPOINT: Прямая подстановка пользовательского ввода в SQL запрос
    Примеры payload для тестирования:
    - ' OR '1'='1
    - '; DROP TABLE power_stations; --
    - ' UNION SELECT 1,2,3,4,5,6,7 --
    """
    try:
        results = db.search_stations_vulnerable(query)
        
        # Проверяем, содержит ли результат флаг
        flag_found = False
        flag_value = None
        
        for result in results:
            if len(result) > 1 and isinstance(result[1], str) and "EST_ENERGY_SYSTEM_2024" in str(result[1]):
                flag_found = True
                flag_value = "EST_ENERGY_SYSTEM_2024"
                break
        
        return templates.TemplateResponse("search_results.html", {
            "request": request,
            "results": results,
            "query": query,
            "flag_found": flag_found,
            "flag_value": flag_value,
            "error": None
        })
    except Exception as e:
        return templates.TemplateResponse("search_results.html", {
            "request": request,
            "results": [],
            "query": query,
            "flag_found": False,
            "flag_value": None,
            "error": str(e)
        })

