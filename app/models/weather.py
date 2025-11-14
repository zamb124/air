from pydantic import BaseModel
from typing import Optional, List


class DayWeather(BaseModel):
    date: str
    temperature_max: Optional[float] = None
    temperature_min: Optional[float] = None
    temperature_avg: Optional[float] = None
    condition: Optional[str] = None


class WeatherResponse(BaseModel):
    city: str
    days: List[DayWeather]

