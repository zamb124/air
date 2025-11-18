from pydantic import BaseModel
from typing import Optional, List


class Hotel(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    rating: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    url: Optional[str] = None
    photos: Optional[List[str]] = None


class HotelListResponse(BaseModel):
    hotels: List[Hotel]
    total: int


class RouteMapResponse(BaseModel):
    map_url: str

