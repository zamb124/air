from typing import Optional, List
from datetime import datetime, timezone
import httpx
import aiosqlite
import logging
from app.db import get_db_connection
from app.models.flights import Flight

logger = logging.getLogger(__name__)

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


async def save_flight_to_db(conn: aiosqlite.Connection, flight_data: dict, flight_type: str):
    flight_id = flight_data.get("id", "")
    flight_number = flight_data.get("number", "") or flight_data.get("callsign", "")
    
    if not flight_id or not flight_number:
        logger.warning(f"Пропуск рейса: нет flight_id или flight_number. flight_id={flight_id}, flight_number={flight_number}")
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
    
    cursor = await conn.execute("""
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
    
    if cursor.rowcount == 0:
        logger.warning(f"Не удалось сохранить рейс {flight_number} (flight_id={flight_id})")


async def update_flights_data():
    conn = None
    try:
        conn = await get_db_connection()
        aircrafts = await fetch_aircrafts_feed()
        logger.info(f"Получено {len(aircrafts)} самолетов из API")
        
        saved_count = 0
        skipped_count = 0
        skipped_no_flight_id = 0
        skipped_no_details = 0
        skipped_no_airports = 0
        
        for aircraft in aircrafts:
            flight_id = aircraft.get("flight_id")
            if not flight_id:
                skipped_no_flight_id += 1
                skipped_count += 1
                continue
            
            flight_details = await fetch_flight_details(flight_id)
            if not flight_details:
                skipped_no_details += 1
                skipped_count += 1
                continue
            
            destination = flight_details.get("destination_airport", {}).get("iata")
            origin = flight_details.get("origin_airport", {}).get("iata")
            
            if not destination and not origin:
                skipped_no_airports += 1
                skipped_count += 1
                continue
            
            flight_number = flight_details.get("number") or flight_details.get("callsign", "")
            await save_flight_to_db(conn, flight_details, "flight")
            saved_count += 1
            if saved_count <= 3:
                logger.info(f"Сохранен рейс: {flight_number}, origin={origin}, destination={destination}")
            
            if saved_count % 10 == 0:
                await conn.commit()
                logger.debug(f"Промежуточный коммит: сохранено {saved_count} рейсов")
        
        await conn.commit()
        logger.info(f"Коммит транзакции выполнен. Обработано рейсов: сохранено {saved_count}, пропущено {skipped_count} (нет flight_id: {skipped_no_flight_id}, нет деталей: {skipped_no_details}, нет аэропортов: {skipped_no_airports})")
    except Exception as e:
        logger.error(f"Ошибка при обновлении данных о рейсах: {e}", exc_info=True)
        if conn:
            await conn.rollback()
    finally:
        if conn:
            await conn.close()


async def get_flights_from_db(
    flight_type: str,
    flight_number: Optional[str] = None,
    has_delay: Optional[bool] = None
) -> List[Flight]:
    conn = await get_db_connection()
    
    try:
        query = "SELECT * FROM flights WHERE flight_type = ?"
        params = [flight_type]
        
        if flight_number:
            query += " AND flight_number LIKE ?"
            params.append(f"%{flight_number.upper()}%")
        
        query += " ORDER BY scheduled_time ASC"
        
        cursor = await conn.execute(query, params)
        rows = await cursor.fetchall()
        
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
    finally:
        await conn.close()
