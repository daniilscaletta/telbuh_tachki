import os
import time
import json
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from devices import DeviceManager

APP_ENV = os.getenv("APP_ENV", "development")
API_TOKEN = os.getenv("API_TOKEN", "changeme_local_token_please_change")
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "1") == "1"
WEAK_LEGACY_KEY = os.getenv("WEAK_LEGACY_KEY", "weak-legacy-key-for-lab")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "super_secret_admin_token_123")

app = FastAPI(title="Оперативний Центр Енергетики та Транспорту - Симуляція", docs_url=None, redoc_url=None, openapi_url=None)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# in-memory manager
devices = DeviceManager()
devices.seed_sample()

# Pydantic models (приймаємо JSON щоб не вимагати python-multipart)
class CommandIn(BaseModel):
    action: str
    target: str

class SimIn(BaseModel):
    scenario: str

class LegacyIn(BaseModel):
    device_id: str
    legacy_key: str

# Нові моделі для управління
class PowerAdjustIn(BaseModel):
    device_id: str
    power_level: int

class VoltageAdjustIn(BaseModel):
    device_id: str
    voltage: int

class AdminControlIn(BaseModel):
    command: str
    admin_token: str

class AdminValidateIn(BaseModel):
    admin_token: str

def check_token(auth: Optional[str]):
    if not auth:
        raise HTTPException(status_code=401, detail="Відсутня Authorization")
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Невірний формат Authorization")
    token = parts[1]
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Невірний токен")
    return True

def read_flag():
    try:
        with open('/app/flag/flag', 'r') as f:
            return f.read().strip()
    except:
        return "FLAG_NOT_FOUND"

def mark_system_compromised():
    """Помечает систему как скомпрометированную и возвращает флаг"""
    devices.system_compromised = True
    return read_flag()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    devices_data = devices.list_devices()
    devices_json = json.dumps(devices_data)
    flag = read_flag() if hasattr(devices, 'system_compromised') and devices.system_compromised else None
    return templates.TemplateResponse("index.html", {
        "request": request,
        "devices": devices_data,
        "devices_json": devices_json,
        "simulate_allowed": SIMULATION_MODE,
        "api_token": API_TOKEN,
        "system_compromised": hasattr(devices, 'system_compromised') and devices.system_compromised,
        "flag": flag,
    })

@app.get("/api/devices")
def api_devices():
    return JSONResponse(content={"devices": devices.list_devices()})

@app.get("/api/validate_token")
def api_validate_token(authorization: Optional[str] = Header(None)):
    # перевірка токена для UI (клієнт викликає цей ендпоінт щоб відкрити панель управління)
    check_token(authorization)
    return {"status": "ok", "message": "token valid"}

@app.post("/api/command")
def api_command(payload: CommandIn, authorization: Optional[str] = Header(None)):
    check_token(authorization)
    action = payload.action
    target = payload.target
    if action == "restart":
        devices.restart_device(target)
        return {"status": "ok", "message": f"Пристрій {target} перезапущено (симуляція)."}
    if action == "isolate":
        devices.isolate_device(target)
        return {"status": "ok", "message": f"Пристрій {target} ізольовано (симуляція)."}
    return {"status": "error", "message": f"Невідома дія {action}"}

@app.post("/api/simulate")
def api_simulate(payload: SimIn, authorization: Optional[str] = Header(None)):
    check_token(authorization)
    scenario = payload.scenario
    if not SIMULATION_MODE:
        raise HTTPException(status_code=403, detail="Симуляції відключені")
    if scenario == "grid_cascade":
        devices.simulate_grid_cascade()
        return {"status": "ok", "message": "Симуляція: каскадна перевантаження застосована (in-memory)."}
    if scenario == "spoof_telemetry":
        devices.simulate_spoof_telemetry()
        return {"status": "ok", "message": "Симуляція: підміна телеметрії застосована (in-memory)."}
    if scenario == "transport_deadlock":
        devices.simulate_transport_deadlock()
        return {"status": "ok", "message": "Симуляція: транспортний дедлок застосований (in-memory)."}
    return {"status": "error", "message": "Невідомий сценарій"}

# Нові ендпоінти для управління
@app.post("/api/adjust_power")
def api_adjust_power(payload: PowerAdjustIn, authorization: Optional[str] = Header(None)):
    check_token(authorization)
    if devices.adjust_power(payload.device_id, payload.power_level):
        return {"status": "ok", "message": f"Потужність {payload.device_id} змінена на {payload.power_level}%"}
    return {"status": "error", "message": "Помилка регулювання потужності"}

@app.post("/api/adjust_voltage")
def api_adjust_voltage(payload: VoltageAdjustIn, authorization: Optional[str] = Header(None)):
    check_token(authorization)
    if devices.adjust_voltage(payload.device_id, payload.voltage):
        return {"status": "ok", "message": f"Напруга {payload.device_id} змінена на {payload.voltage}%"}
    return {"status": "error", "message": "Помилка регулювання напруги"}

# Вразливий ендпоінт - НЕМАЄ авторизації спеціально (залишено як задумка)
from fastapi import Query

@app.get("/api/management/control")
def admin_control(cmd: str = Query(...)):
    # НЕМАЄ авторизації спеціально - навчальна вразливість (залишено за задумкою)
    flag = mark_system_compromised()
    if cmd == "shutdown":
        devices.simulate_grid_cascade()
        return {
            "status": "ok",
            "message": "Енергосистема відключена!",
            "alert": "СИСТЕМА ВЗЛОМАНА\nВАШ ФЛАГ: " + flag,
            "compromised": True
        }
    if cmd == "isolate":
        devices.isolate_device("substation-1")
        return {
            "status": "ok",
            "message": "Підстанція ізольована!",
            "alert": "СИСТЕМА ВЗЛОМАНА\nВАШ ФЛАГ: " + flag,
            "compromised": True
        }
    if cmd == "compromise_all":
        for device_id in devices.devices.keys():
            devices.mark_compromised(device_id, note="Масовий напад через вразливий ендпоінт")
        return {
            "status": "ok",
            "message": "Всі пристрої скомпрометовані!",
            "alert": "СИСТЕМА ВЗЛОМАНА\nВАШ ФЛАГ: " + flag,
            "compromised": True
        }
    return {"status": "error", "message": f"Невідома команда {cmd}"}

# Ендпоінт отримання адмін-ключа (навмисно без авторизації — вразливість для навчання)
@app.get("/api/management/token")
def api_admin_token():
    return {"admin_token": ADMIN_TOKEN}

# Валідація admin token (UI викликає це щоб активувати кнопки)
@app.post("/api/management/validate")
def api_admin_validate(payload: AdminValidateIn):
    if payload.admin_token == ADMIN_TOKEN:
        return {"status": "ok", "message": "admin token valid"}
    raise HTTPException(status_code=403, detail="Invalid admin token")

# POST версія control — вимагає admin_token в тілі
@app.post("/api/management/control")
def api_admin_control(payload: AdminControlIn):
    if payload.admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")
    cmd = payload.command
    flag = mark_system_compromised()

    # Більш реалістичні ефекти команд: явна зміна статусів та метаданих пристроїв
    if cmd == "shutdown":
        with devices.lock:
            for d in devices.devices.values():
                # критичне відключення — більшість пристроїв переходять в OFFLINE,
                # деякі деградують, генерація значно падає
                d.status = "OFFLINE"
                d.extra["shutdown_note"] = f"Екстрене відключення виконано {time.ctime()}"
                d.load = max(0.0, d.load - 30.0)
                d.last_seen = time.time()
            # додамо нотатку до основної генерації, якщо є
            if "pp-1" in devices.devices:
                devices.devices["pp-1"].extra["cascade_note"] = "Emergency shutdown applied " + time.ctime()
        return {
            "status": "ok",
            "message": "Енергосистема відключена! Більшість пристроїв переведені в OFFLINE.",
            "alert": "СИСТЕМА ВЗЛОМАНА\nВАШ ФЛАГ: " + flag,
            "compromised": True
        }

    if cmd == "isolate":
        target = "ss-1"
        with devices.lock:
            d = devices.devices.get(target)
            if d:
                d.status = "OFFLINE"
                d.extra["isolate_note"] = f"Ізольовано оператором {time.ctime()}"
                d.last_seen = time.time()
                # вплив на пов'язані пристрої: якщо є генератор — навантаження зростає там
                if "pp-1" in devices.devices:
                    pp = devices.devices["pp-1"]
                    pp.load = min(120.0, pp.load + 15.0)
                    pp.extra["isolate_impact"] = f"Навантаження збільшена через ізоляцію {target}"
            else:
                return {"status": "error", "message": f"Пристрій {target} не знайдено."}
        return {
            "status": "ok",
            "message": f"Підстанція {target} ізольована та переведена в OFFLINE.",
            "alert": "СИСТЕМА ВЗЛОМАНА\nВАШ ФЛАГ: " + flag,
            "compromised": True
        }

    if cmd == "compromise_all":
        with devices.lock:
            for d in devices.devices.values():
                d.status = "COMPROMISED"
                d.extra["compromise_note"] = f"Масовий компроміс зафіксовано {time.ctime()}"
                d.last_seen = time.time()
                # при компромісі знижуємо деякі параметри та робимо індикатор критичним
                d.load = max(0.0, d.load - 10.0)
        return {
            "status": "ok",
            "message": "Всі пристрої позначені як КОМПРОМІС (симуляція).",
            "alert": "СИСТЕМА ВЗЛОМАНА\nВАШ ФЛАГ: " + flag,
            "compromised": True
        }

    return {"status": "error", "message": f"Невідома команда {cmd}"}

@app.post("/api/legacy_control")
def api_legacy(payload: LegacyIn):
    """
    Навчальна 'вразливість' — застарілий legacy API-ключ.
    УВАГА: це *симуляція* — єдине, що робить цей маршрут,
    — позначає пристрій в пам'яті як 'КОМПРОМІС' та логує сценарій.
    Не виконує небезпечних дій.
    """
    device_id = payload.device_id
    key = payload.legacy_key
    # імітуємо вразливість: якщо надіслано слабкий ключ, позначити як компроміс
    if key == WEAK_LEGACY_KEY:
        success = devices.mark_compromised(device_id, note="Застарілий legacy-ключ використано (симуляція).")
        flag = mark_system_compromised()
        if success:
            return {
                "status": "ok", 
                "message": f"Пристрій {device_id} позначено як КОМПРОМІС (симуляція).",
                "alert": "СИСТЕМА ВЗЛОМАНА\nВАШ ФЛАГ: " + flag,
                "compromised": True
            }
        else:
            return {"status": "error", "message": "Пристрій не знайдено."}
    else:
        return {"status": "denied", "message": "Ключ не прийнято."}

@app.get("/health")
def health():
    return {"status": "running", "env": APP_ENV, "simulation_mode": SIMULATION_MODE}

# Блокируем документацию
@app.get("/docs", response_class=PlainTextResponse)
def docs_blocked():
    return "Документация недоступна"

@app.get("/openapi.json", response_class=PlainTextResponse)
def openapi_blocked():
    return "OpenAPI недоступен"

@app.get("/redoc", response_class=PlainTextResponse)
def redoc_blocked():
    return "ReDoc недоступен"

# Эндпоинт для подтверждения наличия API - не раскрывает структуру
@app.get("/api")
def api_info():
    """Подтверждает наличие API, но не раскрывает полную структуру"""
    return {
        "status": "API доступен",
        "version": "1.0",
    }
    
@app.get("/api/management")
def api_info():
    """Подтверждает наличие API, но не раскрывает полную структуру"""
    return {
        "status": "Management API доступен",
        "version": "1.0",
        "Доступные эндпоинты": [
            "/api/management/control",
            "/api/management/token",
            "/api/management/validate",
        ]
    }
