from fastapi import APIRouter, Query, BackgroundTasks
from typing import Optional
from datetime import datetime
from app.models.flights import Flight, FlightListResponse
from app.services.aviaradar import update_flights_data, get_flights_from_db

router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("", response_model=FlightListResponse)
async def get_flights(
    flight_number: Optional[str] = Query(None, description="Фильтр по номеру рейса"),
    has_delay: Optional[bool] = Query(None, description="Фильтр по наличию задержки")
):
    flights = get_flights_from_db("flight", flight_number, has_delay)
    flights = sorted(flights, key=lambda x: x.scheduled_time if x.scheduled_time else datetime.min)
    return FlightListResponse(flights=flights, total=len(flights))


@router.post("/update")
async def manual_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_flights_data)
    return {"message": "Обновление запущено"}


@router.get("/all", response_model=FlightListResponse)
async def get_all_flights(
    flight_number: Optional[str] = Query(None, description="Фильтр по номеру рейса"),
    has_delay: Optional[bool] = Query(None, description="Фильтр по наличию задержки")
):
    flights = get_flights_from_db("flight", flight_number, has_delay)
    flights = sorted(flights, key=lambda x: x.scheduled_time if x.scheduled_time else datetime.min)
    return FlightListResponse(flights=flights, total=len(flights))


@router.get("/departures", response_model=FlightListResponse)
async def get_departures(
    flight_number: Optional[str] = Query(None, description="Фильтр по номеру рейса"),
    has_delay: Optional[bool] = Query(None, description="Фильтр по наличию задержки")
):
    flights = get_flights_from_db("flight", flight_number, has_delay)
    flights = sorted(flights, key=lambda x: x.scheduled_time if x.scheduled_time else datetime.min)
    return FlightListResponse(flights=flights, total=len(flights))


@router.get("/arrivals", response_model=FlightListResponse)
async def get_arrivals(
    flight_number: Optional[str] = Query(None, description="Фильтр по номеру рейса"),
    has_delay: Optional[bool] = Query(None, description="Фильтр по наличию задержки")
):
    flights = get_flights_from_db("flight", flight_number, has_delay)
    flights = sorted(flights, key=lambda x: x.scheduled_time if x.scheduled_time else datetime.min)
    return FlightListResponse(flights=flights, total=len(flights))

