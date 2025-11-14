from fastapi import APIRouter, Query, HTTPException
from app.models.weather import WeatherResponse
from app.services.openmeteo import get_weather_by_city_and_dates

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("", response_model=WeatherResponse)
async def get_weather(
    city: str = Query(..., description="Название города"),
    date_from: str = Query(..., description="Дата начала (формат: YYYY-MM-DD)"),
    date_to: str = Query(..., description="Дата окончания (формат: YYYY-MM-DD)")
):
    try:
        return await get_weather_by_city_and_dates(city, date_from, date_to)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

