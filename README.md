# Табло аэропорта Шереметьево

FastAPI сервис для получения данных о рейсах из aviaradar.ru API.

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Сервер: http://localhost:8000
Документация: http://localhost:8000/docs

## API Endpoints

- `GET /flights` - все рейсы
- `GET /departures` - все рейсы
- `GET /arrivals` - все рейсы
- `POST /update` - ручное обновление данных

Параметры:
- `flight_number` - фильтр по номеру рейса
- `has_delay` - фильтр по задержке (true/false)

## Данные

Данные загружаются из aviaradar.ru API и сохраняются в SQLite БД. Автоматическое обновление каждые 60 секунд.
