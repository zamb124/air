from fastapi import FastAPI, Query, BackgroundTasks
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel
import httpx
import sqlite3
import asyncio
from contextlib import asynccontextmanager

async def background_updater():
    while True:
        await update_flights_data()
        await asyncio.sleep(UPDATE_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await update_flights_data()
    task = asyncio.create_task(background_updater())
    yield
    task.cancel()


app = FastAPI(
    title="Аэропорт Шереметьево - Табло рейсов",
    version="2.0.0",
    lifespan=lifespan
)

DB_PATH = "flights.db"
UPDATE_INTERVAL_SECONDS = 60
AVIARADAR_API_BASE = "https://aviaradar-client-api.arbina.com"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en,ru;q=0.9,he;q=0.8,en-US;q=0.7,en-GB;q=0.6",
    "cache-control": "no-cache",
    "origin": "https://aviaradar.ru",
    "pragma": "no-cache",
    "referer": "https://aviaradar.ru/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
}


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


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            flight_id TEXT PRIMARY KEY,
            flight_number TEXT NOT NULL,
            destination TEXT,
            origin TEXT,
            scheduled_time TEXT,
            actual_time TEXT,
            status TEXT NOT NULL,
            gate TEXT,
            terminal TEXT,
            delay_minutes INTEGER,
            flight_type TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_flight_type ON flights(flight_type)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_updated_at ON flights(updated_at)
    """)
    
    conn.commit()
    conn.close()


def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


async def fetch_aircrafts_feed() -> List[dict]:
    url = f"{AVIARADAR_API_BASE}/api/aircrafts/feed"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()


async def fetch_flight_details(flight_id: str) -> Optional[dict]:
    url = f"{AVIARADAR_API_BASE}/api/flights/{flight_id}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=HEADERS)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def calculate_delay(scheduled: Optional[datetime], actual: Optional[datetime]) -> Optional[int]:
    if scheduled and actual:
        diff = actual - scheduled
        return int(diff.total_seconds() / 60)
    return None


def save_flight_to_db(conn: sqlite3.Connection, flight_data: dict, flight_type: str):
    cursor = conn.cursor()
    
    flight_id = flight_data.get("id", "")
    flight_number = flight_data.get("number", "") or flight_data.get("callsign", "")
    
    if not flight_id or not flight_number:
        return
    
    destination_airport = flight_data.get("destination_airport", {})
    origin_airport = flight_data.get("origin_airport", {})
    
    destination = destination_airport.get("name") or destination_airport.get("iata")
    origin = origin_airport.get("name") or origin_airport.get("iata")
    
    scheduled_time = parse_datetime(flight_data.get("first_message_received_at"))
    actual_time = parse_datetime(flight_data.get("last_message_received_at"))
    
    status_obj = flight_data.get("status", {})
    status = "live" if status_obj.get("live") else "completed"
    
    delay_minutes = calculate_delay(scheduled_time, actual_time)
    updated_at = datetime.now(timezone.utc).isoformat()
    
    cursor.execute("""
        INSERT OR REPLACE INTO flights 
        (flight_id, flight_number, destination, origin, scheduled_time, actual_time,
         status, gate, terminal, delay_minutes, flight_type, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        flight_id, flight_number, destination, origin,
        scheduled_time.isoformat() if scheduled_time else None,
        actual_time.isoformat() if actual_time else None,
        status, None, None, delay_minutes, flight_type, updated_at
    ))


async def update_flights_data():
    conn = get_db_connection()
    aircrafts = await fetch_aircrafts_feed()
    
    for aircraft in aircrafts:
        flight_id = aircraft.get("flight_id")
        if not flight_id:
            continue
        
        flight_details = await fetch_flight_details(flight_id)
        if not flight_details:
            continue
        
        destination = flight_details.get("destination_airport", {}).get("iata")
        origin = flight_details.get("origin_airport", {}).get("iata")
        
        if not destination and not origin:
            continue
        
        save_flight_to_db(conn, flight_details, "flight")
        await asyncio.sleep(0.05)
    
    conn.commit()
    conn.close()


def get_flights_from_db(
    flight_type: str,
    flight_number: Optional[str] = None,
    has_delay: Optional[bool] = None
) -> List[Flight]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM flights WHERE flight_type = ?"
    params = [flight_type]
    
    if flight_number:
        query += " AND flight_number LIKE ?"
        params.append(f"%{flight_number.upper()}%")
    
    query += " ORDER BY scheduled_time ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    flights = []
    for row in rows:
        flight_id, flight_number_db, destination, origin, scheduled_str, actual_str, \
        status, gate, terminal, delay_minutes, _, updated_at = row
        
        scheduled_time = parse_datetime(scheduled_str) if scheduled_str else None
        actual_time = parse_datetime(actual_str) if actual_str else None
        
        if has_delay is not None:
            if has_delay and (not delay_minutes or delay_minutes <= 0):
                continue
            if not has_delay and delay_minutes and delay_minutes > 0:
                continue
        
        flight = Flight(
            flight_id=flight_id,
            flight_number=flight_number_db,
            destination=destination,
            origin=origin,
            scheduled_time=scheduled_time,
            actual_time=actual_time,
            status=status,
            gate=gate,
            terminal=terminal,
            delay_minutes=delay_minutes
        )
        flights.append(flight)
    
    return flights


@app.post("/update")
async def manual_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_flights_data)
    return {"message": "Обновление запущено"}


@app.get("/departures", response_model=FlightListResponse)
async def get_departures(
    flight_number: Optional[str] = Query(None, description="Фильтр по номеру рейса"),
    has_delay: Optional[bool] = Query(None, description="Фильтр по наличию задержки")
):
    flights = get_flights_from_db("flight", flight_number, has_delay)
    flights = sorted(flights, key=lambda x: x.scheduled_time if x.scheduled_time else datetime.min)
    return FlightListResponse(flights=flights, total=len(flights))


@app.get("/arrivals", response_model=FlightListResponse)
async def get_arrivals(
    flight_number: Optional[str] = Query(None, description="Фильтр по номеру рейса"),
    has_delay: Optional[bool] = Query(None, description="Фильтр по наличию задержки")
):
    flights = get_flights_from_db("flight", flight_number, has_delay)
    flights = sorted(flights, key=lambda x: x.scheduled_time if x.scheduled_time else datetime.min)
    return FlightListResponse(flights=flights, total=len(flights))


@app.get("/flights", response_model=FlightListResponse)
async def get_all_flights(
    flight_number: Optional[str] = Query(None, description="Фильтр по номеру рейса"),
    has_delay: Optional[bool] = Query(None, description="Фильтр по наличию задержки")
):
    flights = get_flights_from_db("flight", flight_number, has_delay)
    flights = sorted(flights, key=lambda x: x.scheduled_time if x.scheduled_time else datetime.min)
    return FlightListResponse(flights=flights, total=len(flights))


@app.get("/")
async def root():
    return {
        "name": "Аэропорт Шереметьево - Табло рейсов",
        "version": "2.0.0",
        "source": "aviaradar.ru API",
        "endpoints": {
            "all_flights": "/flights - все рейсы",
            "departures": "/departures - все рейсы",
            "arrivals": "/arrivals - все рейсы",
            "update": "/update (POST - ручное обновление)",
            "docs": "/docs"
        }
    }
