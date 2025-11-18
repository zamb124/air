from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.models.twogis import HotelListResponse, RouteMapResponse
from app.services.twogis import search_hotels, get_route_map

router = APIRouter(prefix="/twogis", tags=["twogis"])


@router.get("/hotels", response_model=HotelListResponse)
async def get_hotels(
    city: str = Query(..., description="Название города"),
    date_from: Optional[str] = Query(None, description="Дата заезда (формат: YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Дата выезда (формат: YYYY-MM-DD)")
):
    try:
        hotels = await search_hotels(city, date_from, date_to)
        return HotelListResponse(hotels=hotels, total=len(hotels))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching hotels: {str(e)}")


@router.get("/route-map", response_model=RouteMapResponse)
async def get_route_map_endpoint(
    lat_from: float = Query(..., description="Широта точки отправления"),
    lon_from: float = Query(..., description="Долгота точки отправления"),
    lat_to: float = Query(..., description="Широта точки назначения"),
    lon_to: float = Query(..., description="Долгота точки назначения")
):
    try:
        map_url = await get_route_map(lat_from, lon_from, lat_to, lon_to)
        return RouteMapResponse(map_url=map_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting route map: {str(e)}")

