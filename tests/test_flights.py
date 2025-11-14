import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_all_flights():
    response = client.get("/flights/all")
    assert response.status_code == 200
    data = response.json()
    assert "flights" in data
    assert "total" in data
    assert isinstance(data["flights"], list)
    assert isinstance(data["total"], int)


def test_get_departures():
    response = client.get("/flights/departures")
    assert response.status_code == 200
    data = response.json()
    assert "flights" in data
    assert "total" in data
    assert isinstance(data["flights"], list)
    assert isinstance(data["total"], int)


def test_get_arrivals():
    response = client.get("/flights/arrivals")
    assert response.status_code == 200
    data = response.json()
    assert "flights" in data
    assert "total" in data
    assert isinstance(data["flights"], list)
    assert isinstance(data["total"], int)


def test_get_all_flights_with_flight_number_filter():
    response = client.get("/flights/all?flight_number=SU")
    assert response.status_code == 200
    data = response.json()
    assert "flights" in data
    assert "total" in data


def test_get_all_flights_with_delay_filter():
    response = client.get("/flights/all?has_delay=false")
    assert response.status_code == 200
    data = response.json()
    assert "flights" in data
    assert "total" in data


def test_get_departures_with_filters():
    response = client.get("/flights/departures?flight_number=SU&has_delay=true")
    assert response.status_code == 200
    data = response.json()
    assert "flights" in data
    assert "total" in data


def test_get_arrivals_with_filters():
    response = client.get("/flights/arrivals?flight_number=DP&has_delay=false")
    assert response.status_code == 200
    data = response.json()
    assert "flights" in data
    assert "total" in data


@patch('app.routers.flights.update_flights_data')
def test_manual_update(mock_update):
    async def mock_update_func():
        pass
    mock_update.side_effect = mock_update_func
    response = client.post("/flights/update")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_flight_response_structure():
    response = client.get("/flights/all")
    assert response.status_code == 200
    data = response.json()
    
    if data["total"] > 0 and len(data["flights"]) > 0:
        flight = data["flights"][0]
        assert "flight_number" in flight
        assert "status" in flight
        assert "destination" in flight
        assert "origin" in flight
        assert isinstance(flight["flight_number"], str)

