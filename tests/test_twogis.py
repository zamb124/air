import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.twogis import search_hotels, get_route_map
from app.config import get_config_value

client = TestClient(app)


@pytest.mark.asyncio
async def test_search_hotels_success():
    api_key = get_config_value("twogis.api_key")
    if not api_key:
        pytest.skip("2GIS API key not configured")
    
    hotels = await search_hotels("Москва")
    
    assert isinstance(hotels, list)
    assert len(hotels) > 0, "Список отелей не должен быть пустым"
    
    hotel = hotels[0]
    assert hotel.id
    assert hotel.name
    assert isinstance(hotel.name, str)


@pytest.mark.asyncio
async def test_search_hotels_with_dates():
    api_key = get_config_value("twogis.api_key")
    if not api_key:
        pytest.skip("2GIS API key not configured")
    
    hotels = await search_hotels("Москва", "2025-01-15", "2025-01-20")
    
    assert isinstance(hotels, list)


@pytest.mark.asyncio
async def test_search_hotels_different_city():
    api_key = get_config_value("twogis.api_key")
    if not api_key:
        pytest.skip("2GIS API key not configured")
    
    hotels = await search_hotels("Санкт-Петербург")
    
    assert isinstance(hotels, list)


@pytest.mark.asyncio
async def test_get_route_map_success():
    api_key = get_config_value("twogis.api_key")
    if not api_key:
        pytest.skip("2GIS API key not configured")
    
    lat_from = 55.7522
    lon_from = 37.6156
    lat_to = 55.7558
    lon_to = 37.6173
    
    map_url = await get_route_map(lat_from, lon_from, lat_to, lon_to)
    
    assert isinstance(map_url, str)
    assert "static.maps.2gis.com" in map_url


@pytest.mark.asyncio
async def test_get_route_map_different_points():
    api_key = get_config_value("twogis.api_key")
    if not api_key:
        pytest.skip("2GIS API key not configured")
    
    lat_from = 59.9343
    lon_from = 30.3351
    lat_to = 59.9375
    lon_to = 30.3086
    
    map_url = await get_route_map(lat_from, lon_from, lat_to, lon_to)
    
    assert isinstance(map_url, str)
    assert "static.maps.2gis.com" in map_url


def test_get_hotels_endpoint_success():
    api_key = get_config_value("twogis.api_key")
    if not api_key:
        pytest.skip("2GIS API key not configured")
    
    response = client.get("/twogis/hotels?city=Москва")
    
    assert response.status_code == 200
    data = response.json()
    assert "hotels" in data
    assert "total" in data
    assert isinstance(data["hotels"], list)
    assert isinstance(data["total"], int)
    assert data["total"] == len(data["hotels"])


def test_get_hotels_endpoint_with_dates():
    api_key = get_config_value("twogis.api_key")
    if not api_key:
        pytest.skip("2GIS API key not configured")
    
    response = client.get("/twogis/hotels?city=Москва&date_from=2025-01-15&date_to=2025-01-20")
    
    assert response.status_code == 200
    data = response.json()
    assert "hotels" in data
    assert "total" in data


def test_get_hotels_endpoint_missing_city():
    response = client.get("/twogis/hotels")
    
    assert response.status_code == 422


def test_get_route_map_endpoint_success():
    api_key = get_config_value("twogis.api_key")
    if not api_key:
        pytest.skip("2GIS API key not configured")
    
    response = client.get("/twogis/route-map?lat_from=55.7522&lon_from=37.6156&lat_to=55.7558&lon_to=37.6173")
    
    assert response.status_code == 200
    data = response.json()
    assert "map_url" in data
    assert isinstance(data["map_url"], str)
    assert "static.maps.2gis.com" in data["map_url"]


def test_get_route_map_endpoint_missing_params():
    response = client.get("/twogis/route-map?lat_from=55.7522&lon_from=37.6156")
    
    assert response.status_code == 422


def test_get_route_map_endpoint_all_params():
    api_key = get_config_value("twogis.api_key")
    if not api_key:
        pytest.skip("2GIS API key not configured")
    
    response = client.get("/twogis/route-map?lat_from=59.9343&lon_from=30.3351&lat_to=59.9375&lon_to=30.3086")
    
    assert response.status_code == 200
    data = response.json()
    assert "map_url" in data
    assert isinstance(data["map_url"], str)


@pytest.mark.asyncio
async def test_search_hotels_empty_result():
    api_key = get_config_value("twogis.api_key")
    if not api_key:
        pytest.skip("2GIS API key not configured")
    
    with pytest.raises(ValueError, match="не найден"):
        await search_hotels("НесуществующийГород12345")


@pytest.mark.asyncio
async def test_get_route_map_invalid_coordinates():
    api_key = get_config_value("twogis.api_key")
    if not api_key:
        pytest.skip("2GIS API key not configured")
    
    map_url = await get_route_map(0.0, 0.0, 0.0, 0.0)
    assert isinstance(map_url, str)
    assert "static.maps.2gis.com" in map_url

