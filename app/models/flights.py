from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class Flight(BaseModel):
    flight_number: str
    destination: Optional[str] = None
    origin: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    actual_time: Optional[datetime] = None
    status: str
    gate: Optional[str] = None
    terminal: Optional[str] = None
    delay_minutes: Optional[int] = None
    flight_id: Optional[str] = None


class FlightListResponse(BaseModel):
    flights: List[Flight]
    total: int

