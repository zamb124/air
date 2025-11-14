from fastapi import FastAPI
import asyncio
import logging
from contextlib import asynccontextmanager
from app.db import init_db
from app.services.aviaradar import update_flights_data
from app.routers import flights, weather

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPDATE_INTERVAL_SECONDS = 60


async def background_updater():
    logger.info("Фоновая задача обновления рейсов запущена")
    while True:
        try:
            logger.info("Начало обновления данных о рейсах")
            await update_flights_data()
            logger.info("Обновление данных о рейсах завершено")
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных о рейсах: {e}", exc_info=True)
        await asyncio.sleep(UPDATE_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(background_updater())
    yield
    task.cancel()


app = FastAPI(
    title="MCP-like REST API",
    version="2.0.0",
    description="REST API сервер с различными функциями для получения информации",
    lifespan=lifespan
)

app.include_router(flights.router)
app.include_router(weather.router)


@app.get("/")
async def root():
    return {
        "name": "MCP-like REST API",
        "version": "2.0.0",
        "description": "REST API сервер с различными функциями для получения информации",
        "docs": "/docs",
        "endpoints": {
            "flights": {
                "description": "Данные о рейсах",
                "endpoints": {
                    "GET /flights": {
                        "description": "Получить все рейсы",
                        "query_params": {
                            "flight_number": "Опционально. Фильтр по номеру рейса (например: SU123)",
                            "has_delay": "Опционально. Фильтр по наличию задержки (true/false)"
                        },
                        "example": "GET /flights?flight_number=SU&has_delay=true"
                    },
                    "GET /flights/all": {
                        "description": "Получить все рейсы (аналогично /flights)",
                        "example": "GET /flights/all?flight_number=DP"
                    },
                    "GET /flights/departures": {
                        "description": "Получить вылеты",
                        "example": "GET /flights/departures?has_delay=false"
                    },
                    "GET /flights/arrivals": {
                        "description": "Получить прилеты",
                        "example": "GET /flights/arrivals"
                    },
                    "POST /flights/update": {
                        "description": "Запустить обновление данных о рейсах",
                        "example": "POST /flights/update"
                    }
                }
            },
            "weather": {
                "description": "Данные о погоде",
                "endpoints": {
                    "GET /weather": {
                        "description": "Получить прогноз погоды на диапазон дат",
                        "query_params": {
                            "city": "Название города (обязательно)",
                            "date_from": "Дата начала в формате YYYY-MM-DD (обязательно)",
                            "date_to": "Дата окончания в формате YYYY-MM-DD (обязательно)"
                        },
                        "example": "GET /weather?city=Moscow&date_from=2025-01-15&date_to=2025-01-20"
                    }
                }
            }
        }
    }
