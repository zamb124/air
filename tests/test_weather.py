import pytest
from datetime import datetime, date, timedelta
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from main import app
from app.services.openmeteo import get_weather_by_city_and_dates, _get_city_coordinates

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_city_coordinates_success():
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={
        "results": [
            {
                "id": 1,
                "name": "Moscow",
                "latitude": 55.7558,
                "longitude": 37.6173,
                "country": "Russia"
            }
        ]
    })
    mock_response.raise_for_status = MagicMock()
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        lat, lon = await _get_city_coordinates("Moscow")
        
        assert lat == 55.7558
        assert lon == 37.6173


@pytest.mark.asyncio
async def test_get_city_coordinates_city_not_found():
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={"results": []})
    mock_response.raise_for_status = MagicMock()
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        with pytest.raises(ValueError, match="не найден"):
            await _get_city_coordinates("NonExistentCity")


@pytest.mark.asyncio
async def test_get_city_coordinates_missing_coordinates():
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={
        "results": [
            {
                "id": 1,
                "name": "City",
                "latitude": None,
                "longitude": None
            }
        ]
    })
    mock_response.raise_for_status = MagicMock()
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        with pytest.raises(ValueError, match="Не удалось получить координаты"):
            await _get_city_coordinates("City")


@pytest.mark.asyncio
async def test_get_weather_by_city_and_dates_success():
    today = date.today()
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    
    geocoding_response = MagicMock()
    geocoding_response.json = MagicMock(return_value={
        "results": [
            {
                "id": 1,
                "name": "Moscow",
                "latitude": 55.7558,
                "longitude": 37.6173
            }
        ]
    })
    geocoding_response.raise_for_status = MagicMock()
    
    weather_response = MagicMock()
    weather_response.json = MagicMock(return_value={
        "daily": {
            "time": [date_from, (today + timedelta(days=1)).strftime("%Y-%m-%d"), date_to],
            "temperature_2m_max": [15.5, 16.0, 17.2],
            "temperature_2m_min": [5.0, 6.0, 7.0],
            "weathercode": [0, 1, 2]
        }
    })
    weather_response.status_code = 200
    weather_response.raise_for_status = MagicMock()
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(side_effect=[geocoding_response, weather_response])
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await get_weather_by_city_and_dates("Moscow", date_from, date_to)
        
        assert result.city == "Moscow"
        assert len(result.days) == 3
        
        day = result.days[0]
        assert day.date == date_from
        assert day.temperature_max == 15.5
        assert day.temperature_min == 5.0
        assert day.temperature_avg == 10.25
        assert day.condition == "Ясно"


@pytest.mark.asyncio
async def test_get_weather_by_city_and_dates_invalid_date_format():
    with pytest.raises(ValueError, match="Неверный формат даты"):
        await get_weather_by_city_and_dates("Moscow", "invalid-date", "2025-01-20")


@pytest.mark.asyncio
async def test_get_weather_by_city_and_dates_date_from_after_date_to():
    today = date.today()
    date_from = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    date_to = today.strftime("%Y-%m-%d")
    
    with pytest.raises(ValueError, match="Дата начала должна быть раньше"):
        await get_weather_by_city_and_dates("Moscow", date_from, date_to)


@pytest.mark.asyncio
async def test_get_weather_by_city_and_dates_past_dates():
    past_date = (date.today() - timedelta(days=5)).strftime("%Y-%m-%d")
    past_date_to = (date.today() - timedelta(days=3)).strftime("%Y-%m-%d")
    
    geocoding_response = MagicMock()
    geocoding_response.json = MagicMock(return_value={
        "results": [
            {
                "id": 1,
                "name": "Moscow",
                "latitude": 55.7558,
                "longitude": 37.6173
            }
        ]
    })
    geocoding_response.raise_for_status = MagicMock()
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=geocoding_response)
        
        with pytest.raises(ValueError, match="прошлом"):
            await get_weather_by_city_and_dates("Moscow", past_date, past_date_to)


@pytest.mark.asyncio
async def test_get_weather_by_city_and_dates_weather_api_error():
    today = date.today()
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    geocoding_response = MagicMock()
    geocoding_response.json = MagicMock(return_value={
        "results": [
            {
                "id": 1,
                "name": "Moscow",
                "latitude": 55.7558,
                "longitude": 37.6173
            }
        ]
    })
    geocoding_response.raise_for_status = MagicMock()
    
    weather_response = MagicMock()
    weather_response.status_code = 400
    weather_response.json = MagicMock(return_value={
        "reason": "Invalid date range"
    })
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(side_effect=[geocoding_response, weather_response])
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        with pytest.raises(ValueError, match="Ошибка API"):
            await get_weather_by_city_and_dates("Moscow", date_from, date_to)


@pytest.mark.asyncio
async def test_get_weather_by_city_and_dates_missing_temperature_data():
    today = date.today()
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    geocoding_response = MagicMock()
    geocoding_response.json = MagicMock(return_value={
        "results": [
            {
                "id": 1,
                "name": "Moscow",
                "latitude": 55.7558,
                "longitude": 37.6173
            }
        ]
    })
    geocoding_response.raise_for_status = MagicMock()
    
    weather_response = MagicMock()
    weather_response.json = MagicMock(return_value={
        "daily": {
            "time": [date_from, date_to],
            "temperature_2m_max": [],
            "temperature_2m_min": [],
            "weathercode": [0, 1]
        }
    })
    weather_response.status_code = 200
    weather_response.raise_for_status = MagicMock()
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(side_effect=[geocoding_response, weather_response])
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await get_weather_by_city_and_dates("Moscow", date_from, date_to)
        
        assert len(result.days) == 2
        assert result.days[0].temperature_max is None
        assert result.days[0].temperature_min is None
        assert result.days[0].temperature_avg is None


@pytest.mark.asyncio
async def test_get_weather_by_city_and_dates_unknown_weather_code():
    today = date.today()
    date_from = today.strftime("%Y-%m-%d")
    date_to = today.strftime("%Y-%m-%d")
    
    geocoding_response = MagicMock()
    geocoding_response.json = MagicMock(return_value={
        "results": [
            {
                "id": 1,
                "name": "Moscow",
                "latitude": 55.7558,
                "longitude": 37.6173
            }
        ]
    })
    geocoding_response.raise_for_status = MagicMock()
    
    weather_response = MagicMock()
    weather_response.json = MagicMock(return_value={
        "daily": {
            "time": [date_from],
            "temperature_2m_max": [15.0],
            "temperature_2m_min": [5.0],
            "weathercode": [999]
        }
    })
    weather_response.status_code = 200
    weather_response.raise_for_status = MagicMock()
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(side_effect=[geocoding_response, weather_response])
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await get_weather_by_city_and_dates("Moscow", date_from, date_to)
        
        assert result.days[0].condition == "Код погоды: 999"


def test_get_weather_endpoint_success():
    today = date.today()
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    
    geocoding_response = MagicMock()
    geocoding_response.json = MagicMock(return_value={
        "results": [
            {
                "id": 1,
                "name": "Moscow",
                "latitude": 55.7558,
                "longitude": 37.6173
            }
        ]
    })
    geocoding_response.raise_for_status = MagicMock()
    
    weather_response = MagicMock()
    weather_response.json = MagicMock(return_value={
        "daily": {
            "time": [date_from, (today + timedelta(days=1)).strftime("%Y-%m-%d"), date_to],
            "temperature_2m_max": [15.5, 16.0, 17.2],
            "temperature_2m_min": [5.0, 6.0, 7.0],
            "weathercode": [0, 1, 2]
        }
    })
    weather_response.status_code = 200
    weather_response.raise_for_status = MagicMock()
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(side_effect=[geocoding_response, weather_response])
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        response = client.get(f"/weather?city=Moscow&date_from={date_from}&date_to={date_to}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Moscow"
        assert len(data["days"]) == 3


def test_get_weather_endpoint_missing_city():
    today = date.today()
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    response = client.get(f"/weather?date_from={date_from}&date_to={date_to}")
    assert response.status_code == 422


def test_get_weather_endpoint_missing_date_from():
    today = date.today()
    date_to = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    response = client.get(f"/weather?city=Moscow&date_to={date_to}")
    assert response.status_code == 422


def test_get_weather_endpoint_missing_date_to():
    today = date.today()
    date_from = today.strftime("%Y-%m-%d")
    
    response = client.get(f"/weather?city=Moscow&date_from={date_from}")
    assert response.status_code == 422


def test_get_weather_endpoint_invalid_date_format():
    today = date.today()
    date_to = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    response = client.get(f"/weather?city=Moscow&date_from=invalid-date&date_to={date_to}")
    assert response.status_code == 400
    assert "Неверный формат даты" in response.json()["detail"]


def test_get_weather_endpoint_date_from_after_date_to():
    today = date.today()
    date_from = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    date_to = today.strftime("%Y-%m-%d")
    
    response = client.get(f"/weather?city=Moscow&date_from={date_from}&date_to={date_to}")
    assert response.status_code == 400
    assert "Дата начала должна быть раньше" in response.json()["detail"]


def test_get_weather_endpoint_city_not_found():
    today = date.today()
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    geocoding_response = MagicMock()
    geocoding_response.json = MagicMock(return_value={"results": []})
    geocoding_response.raise_for_status = MagicMock()
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=geocoding_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        response = client.get(f"/weather?city=NonExistentCity12345&date_from={date_from}&date_to={date_to}")
        
        assert response.status_code == 400
        assert "не найден" in response.json()["detail"]


def test_get_weather_endpoint_past_dates():
    past_date = (date.today() - timedelta(days=5)).strftime("%Y-%m-%d")
    past_date_to = (date.today() - timedelta(days=3)).strftime("%Y-%m-%d")
    
    geocoding_response = MagicMock()
    geocoding_response.json = MagicMock(return_value={
        "results": [
            {
                "id": 1,
                "name": "Moscow",
                "latitude": 55.7558,
                "longitude": 37.6173
            }
        ]
    })
    geocoding_response.raise_for_status = MagicMock()
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=geocoding_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        response = client.get(f"/weather?city=Moscow&date_from={past_date}&date_to={past_date_to}")
        
        assert response.status_code == 400
        assert "прошлом" in response.json()["detail"]


def test_get_weather_endpoint_response_structure():
    today = date.today()
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    geocoding_response = MagicMock()
    geocoding_response.json = MagicMock(return_value={
        "results": [
            {
                "id": 1,
                "name": "London",
                "latitude": 51.5074,
                "longitude": -0.1278
            }
        ]
    })
    geocoding_response.raise_for_status = MagicMock()
    
    weather_response = MagicMock()
    weather_response.json = MagicMock(return_value={
        "daily": {
            "time": [date_from, date_to],
            "temperature_2m_max": [12.5, 13.0],
            "temperature_2m_min": [5.0, 6.0],
            "weathercode": [1, 2]
        }
    })
    weather_response.status_code = 200
    weather_response.raise_for_status = MagicMock()
    
    with patch("app.services.openmeteo.httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(side_effect=[geocoding_response, weather_response])
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        response = client.get(f"/weather?city=London&date_from={date_from}&date_to={date_to}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "city" in data
        assert "days" in data
        assert data["city"] == "London"
        assert isinstance(data["days"], list)
        assert len(data["days"]) == 2
        
        day = data["days"][0]
        assert "date" in day
        assert isinstance(day["date"], str)
        assert day["temperature_max"] == 12.5
        assert day["temperature_min"] == 5.0
        assert day["temperature_avg"] == 8.75
        assert isinstance(day["condition"], str)
