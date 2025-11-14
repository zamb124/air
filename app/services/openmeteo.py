import httpx
from typing import Tuple, List
from datetime import datetime, date
from app.models.weather import WeatherResponse, DayWeather

GEOCODING_API_BASE = "https://geocoding-api.open-meteo.com/v1"
WEATHER_API_BASE = "https://api.open-meteo.com/v1"

WEATHER_CODES = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Изморозь",
    51: "Легкая морось",
    53: "Умеренная морось",
    55: "Сильная морось",
    56: "Легкая ледяная морось",
    57: "Сильная ледяная морось",
    61: "Небольшой дождь",
    63: "Умеренный дождь",
    65: "Сильный дождь",
    66: "Легкий ледяной дождь",
    67: "Сильный ледяной дождь",
    71: "Небольшой снег",
    73: "Умеренный снег",
    75: "Сильный снег",
    77: "Снежные зерна",
    80: "Небольшой ливень",
    81: "Умеренный ливень",
    82: "Сильный ливень",
    85: "Небольшой снегопад",
    86: "Сильный снегопад",
    95: "Гроза",
    96: "Гроза с градом",
    99: "Сильная гроза с градом"
}


async def _get_city_coordinates(city_name: str) -> Tuple[float, float]:
    url = f"{GEOCODING_API_BASE}/search"
    params = {
        "name": city_name,
        "count": 1,
        "language": "ru"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        if not results:
            raise ValueError(f"Город '{city_name}' не найден")
        
        city_data = results[0]
        latitude = city_data.get("latitude")
        longitude = city_data.get("longitude")
        
        if latitude is None or longitude is None:
            raise ValueError(f"Не удалось получить координаты для города '{city_name}'")
        
        return latitude, longitude


async def get_weather_by_city_and_dates(city: str, date_from: str, date_to: str) -> WeatherResponse:
    latitude, longitude = await _get_city_coordinates(city)
    
    today = date.today()
    try:
        from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
        to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Неверный формат даты. Используйте YYYY-MM-DD")
    
    if from_date > to_date:
        raise ValueError("Дата начала должна быть раньше или равна дате окончания")
    
    url = f"{WEATHER_API_BASE}/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }
    
    if from_date >= today:
        params["start_date"] = date_from
        params["end_date"] = date_to
    else:
        forecast_days = (to_date - today).days + 1
        if forecast_days > 0:
            params["forecast_days"] = min(forecast_days, 16)
        else:
            raise ValueError("Указанные даты находятся в прошлом. Open-Meteo API поддерживает только прогноз на будущее (до 16 дней)")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        if response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get("reason", "Ошибка запроса к API погоды")
            raise ValueError(f"Ошибка API: {error_msg}")
        response.raise_for_status()
        data = response.json()
        
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        temperature_max = daily.get("temperature_2m_max", [])
        temperature_min = daily.get("temperature_2m_min", [])
        weathercode = daily.get("weathercode", [])
        
        days: List[DayWeather] = []
        
        for i, date_str in enumerate(dates):
            day_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            if day_date < from_date or day_date > to_date:
                continue
            
            temp_max = temperature_max[i] if i < len(temperature_max) else None
            temp_min = temperature_min[i] if i < len(temperature_min) else None
            temp_avg = None
            if temp_max is not None and temp_min is not None:
                temp_avg = (temp_max + temp_min) / 2
            
            code = weathercode[i] if i < len(weathercode) else None
            condition = WEATHER_CODES.get(code, f"Код погоды: {code}") if code is not None else None
            
            days.append(DayWeather(
                date=date_str,
                temperature_max=temp_max,
                temperature_min=temp_min,
                temperature_avg=temp_avg,
                condition=condition
            ))
        
        return WeatherResponse(
            city=city,
            days=days
        )

