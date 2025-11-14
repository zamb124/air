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
- `GET /weather/current?city=Москва` - текущая погода

## Добавление нового модуля

1. Создать роутер: `app/routers/your_module.py`
2. Добавить в `main.py`: `app.include_router(your_module.router)`
