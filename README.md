# MCP-like REST API

Модульный REST API сервер с различными функциями для получения информации (рейсы, погода и т.д.).

## Структура проекта

```
app/
├── routers/       # API роутеры (flights, weather, ...)
├── models/        # Pydantic модели
├── services/      # Бизнес-логика и работа с внешними API
└── db.py          # Работа с базой данных
main.py            # Точка входа приложения
```

## Установка

```bash
# Установка зависимостей
uv sync

# Или для установки с dev-зависимостями (для тестов)
uv sync --extra dev
```

## Запуск

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Сервер: http://localhost:8000
Документация: http://localhost:8000/docs

## Тесты

Тесты находятся в директории `tests/`. Для запуска:

```bash
# Запуск всех тестов
uv run pytest -v

# Запуск конкретного файла
uv run pytest tests/test_flights.py -v
```

## Модули

### Flights (Рейсы)
- `GET /flights/all` - все рейсы
- `GET /flights/departures` - вылеты
- `GET /flights/arrivals` - прилеты
- `POST /flights/update` - обновление данных

### Weather (Погода)
- `GET /weather?city=Moscow&date_from=2025-01-15&date_to=2025-01-20` - прогноз погоды

### 2GIS
- `GET /twogis/hotels?city=Москва` - поиск отелей в городе
- `GET /twogis/route-map?lat_from=55.7522&lon_from=37.6156&lat_to=55.7558&lon_to=37.6173` - карта маршрута

## Примеры запросов

```bash
# Поиск отелей в Москве
curl "http://localhost:8000/twogis/hotels?city=Москва"

# Поиск отелей с датами
curl "http://localhost:8000/twogis/hotels?city=Москва&date_from=2025-01-15&date_to=2025-01-20"

# Карта маршрута
curl "http://localhost:8000/twogis/route-map?lat_from=55.7522&lon_from=37.6156&lat_to=55.7558&lon_to=37.6173"
```

## Добавление нового модуля

1. Создать роутер: `app/routers/your_module.py`
2. Добавить в `main.py`: `app.include_router(your_module.router)`
