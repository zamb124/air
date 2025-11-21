from fastapi import FastAPI
import asyncio
import logging
from contextlib import asynccontextmanager
from app.services.aviaradar import update_flights_data, delete_old_flights
from app.routers import flights, weather, twogis, widgets, openrouter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPDATE_INTERVAL_SECONDS = 120
CLEANUP_INTERVAL_SECONDS = 3600


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


async def background_cleaner():
    logger.info("Фоновая задача очистки старых рейсов запущена")
    await asyncio.sleep(60)
    while True:
        try:
            await delete_old_flights()
        except Exception as e:
            logger.error(f"Ошибка при очистке старых рейсов: {e}", exc_info=True)
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db import init_db
    await init_db()
    updater_task = asyncio.create_task(background_updater())
    cleaner_task = asyncio.create_task(background_cleaner())
    yield
    updater_task.cancel()
    cleaner_task.cancel()


app = FastAPI(
    title="MCP-like REST API",
    version="2.0.0",
    description="REST API сервер с различными функциями для получения информации",
    lifespan=lifespan
)

app.include_router(flights.router)
app.include_router(weather.router)
app.include_router(twogis.router)
app.include_router(widgets.router)
app.include_router(openrouter.router)


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
            },
            "twogis": {
                "description": "Данные от 2GIS API",
                "endpoints": {
                    "GET /twogis/hotels": {
                        "description": "Поиск отелей в городе",
                        "query_params": {
                            "city": "Название города (обязательно)",
                            "date_from": "Опционально. Дата заезда (формат: YYYY-MM-DD)",
                            "date_to": "Опционально. Дата выезда (формат: YYYY-MM-DD)"
                        },
                        "example": "GET /twogis/hotels?city=Москва&date_from=2025-01-15&date_to=2025-01-20"
                    },
                    "GET /twogis/route-map": {
                        "description": "Получить URL статической карты с маршрутом между двумя точками",
                        "query_params": {
                            "lat_from": "Широта точки отправления (обязательно)",
                            "lon_from": "Долгота точки отправления (обязательно)",
                            "lat_to": "Широта точки назначения (обязательно)",
                            "lon_to": "Долгота точки назначения (обязательно)"
                        },
                        "example": "GET /twogis/route-map?lat_from=55.7522&lon_from=37.6156&lat_to=55.7558&lon_to=37.6173"
                    }
                }
            },
            "widgets": {
                "description": "API для виджетов",
                "endpoints": {
                    "GET /widgets/view": {
                        "description": "Получить представление с виджетами",
                        "query_params": {
                            "goal_id": "Опционально. Идентификатор цели",
                            "context": "Опционально. Контекст использования (travel, savings)"
                        },
                        "example": "GET /widgets/view?goal_id=123&context=travel"
                    },
                    "POST /widgets/action": {
                        "description": "Выполнить действие от виджета",
                        "example": "POST /widgets/action"
                    }
                }
            },
            "openrouter": {
                "description": "Прокси для OpenRouter API",
                "note": "Все эндпоинты требуют заголовок X-API-Token с токеном из конфигурации",
                "endpoints": {
                    "POST /openrouter/chat/completions": {
                        "description": "Создает completion для списка сообщений чата. Проксирует запрос в OpenRouter API",
                        "headers": {
                            "X-API-Token": "Токен для доступа (обязательно)",
                            "Content-Type": "application/json"
                        },
                        "example": "POST /openrouter/chat/completions\nHeaders: X-API-Token: your-token\nBody: {\"model\": \"x-ai/grok-code-fast-1\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello\"}]}"
                    },
                    "GET /openrouter/models": {
                        "description": "Получает список доступных моделей. Проксирует запрос в OpenRouter API",
                        "headers": {
                            "X-API-Token": "Токен для доступа (обязательно)"
                        },
                        "example": "GET /openrouter/models\nHeaders: X-API-Token: your-token"
                    },
                    "POST /openrouter/{path}": {
                        "description": "Универсальный эндпоинт для проксирования POST запросов в OpenRouter API",
                        "headers": {
                            "X-API-Token": "Токен для доступа (обязательно)"
                        },
                        "example": "POST /openrouter/chat/completions\nHeaders: X-API-Token: your-token"
                    },
                    "GET /openrouter/{path}": {
                        "description": "Универсальный эндпоинт для проксирования GET запросов в OpenRouter API",
                        "headers": {
                            "X-API-Token": "Токен для доступа (обязательно)"
                        },
                        "example": "GET /openrouter/models\nHeaders: X-API-Token: your-token"
                    }
                }
            }
        }
    }
