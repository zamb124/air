from typing import Optional, List
import httpx
import logging
from urllib.parse import urlencode
from app.config import get_config_value
from app.models.twogis import Hotel

logger = logging.getLogger(__name__)

CATALOG_API_BASE = "https://catalog.api.2gis.com"
ROUTING_API_BASE = "https://routing.api.2gis.com"
STATIC_API_BASE = "http://static.maps.2gis.com"


def _get_api_key() -> str:
    return get_config_value("twogis.api_key", "")


async def _get_city_coordinates(city: str) -> tuple[float, float]:
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("2GIS API key not configured")
    
    geocoder_url = f"{CATALOG_API_BASE}/3.0/items"
    params = {
        "q": city,
        "key": api_key,
        "page_size": 1,
        "fields": "items.point"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(geocoder_url, params=params)
        if response.status_code != 200:
            logger.error(f"2GIS Geocoder API error: {response.status_code}, response: {response.text}")
        response.raise_for_status()
        data = response.json()
        
        result = data.get("result", {})
        items = result.get("items", [])
        if not items:
            raise ValueError(f"Город '{city}' не найден")
        
        city_item = None
        for item in items:
            if item.get("type") == "adm_div" and item.get("subtype") == "city":
                city_item = item
                break
        
        if not city_item:
            city_item = items[0]
        
        point = city_item.get("point", {})
        lat = point.get("lat")
        lon = point.get("lon")
        
        if lat is None or lon is None:
            raise ValueError(f"Не удалось получить координаты для города '{city}'")
        
        return lat, lon


async def search_hotels(city: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[Hotel]:
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("2GIS API key not configured")
    
    lat, lon = await _get_city_coordinates(city)
    
    hotels = []
    target_count = 50
    page_size = 10
    page = 1
    seen_ids = set()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while len(hotels) < target_count:
            url = f"{CATALOG_API_BASE}/3.0/items"
            params = {
                "q": "отели",
                "location": f"{lon},{lat}",
                "radius": 50000,
                "key": api_key,
                "page_size": page_size,
                "page": page,
                "fields": "items.point,items.address_name,items.address,items.rating,items.contact_groups,items.flags"
            }
            
            response = await client.get(url, params=params)
            if response.status_code != 200:
                logger.error(f"2GIS API error: {response.status_code}, response: {response.text}")
            response.raise_for_status()
            data = response.json()
            
            result = data.get("result", {})
            items = result.get("items", [])
            total = result.get("total", 0)
            
            if not items:
                break
            
            # Если это первая страница и total меньше целевого количества, используем total
            if page == 1 and total < target_count:
                target_count = total
            
            for item in items:
                hotel_id = item.get("id", "")
                name = item.get("name", "")
                
                if not hotel_id or not name:
                    logger.warning(f"Пропуск элемента без id или name: {item}")
                    continue
                
                # Пропускаем дубликаты
                if hotel_id in seen_ids:
                    continue
                seen_ids.add(hotel_id)
                
                # Если уже набрали нужное количество, выходим
                if len(hotels) >= target_count:
                    break
        
                address_obj = item.get("address_name", "")
                if not address_obj and "address" in item:
                    address_components = item.get("address", {}).get("components", [])
                    address_parts = []
                    for comp in address_components:
                        street = comp.get("street", "")
                        number = comp.get("number", "")
                        if street:
                            address_parts.append(street)
                        if number:
                            address_parts.append(number)
                    address_obj = ", ".join(address_parts) if address_parts else ""
                
                point = item.get("point", {})
                item_lat = point.get("lat") if point else None
                item_lon = point.get("lon") if point else None
                
                rating_obj = item.get("rating", {})
                rating = rating_obj.get("rating", None) if rating_obj else None
                
                contacts = item.get("contact_groups", [])
                phone = None
                website = None
                for contact_group in contacts:
                    contact_type = contact_group.get("type", "")
                    if contact_type == "phone":
                        contacts_list = contact_group.get("contacts", [])
                        if contacts_list:
                            phone = contacts_list[0].get("value", "")
                    elif contact_type == "website":
                        contacts_list = contact_group.get("contacts", [])
                        if contacts_list:
                            website = contacts_list[0].get("value", "")
                
                hotel_url = f"https://2gis.ru/firm/{hotel_id}"
                
                photos = None
                flags = item.get("flags", {})
                if flags.get("photos"):
                    try:
                        photos_url = f"{CATALOG_API_BASE}/3.0/items/byid"
                        photos_params = {
                            "id": hotel_id,
                            "key": api_key,
                            "fields": "items.photos"
                        }
                        async with httpx.AsyncClient(timeout=10.0) as photos_client:
                            photos_response = await photos_client.get(photos_url, params=photos_params)
                            if photos_response.status_code == 200:
                                photos_data = photos_response.json()
                                photos_items = photos_data.get("result", {}).get("items", [])
                                if photos_items:
                                    hotel_photos = photos_items[0].get("photos", [])
                                    if hotel_photos:
                                        photos = []
                                        for photo in hotel_photos:
                                            photo_url = photo.get("url") or photo.get("thumbnail_url") or photo.get("image_url") or photo.get("href")
                                            if photo_url:
                                                if not photo_url.startswith("http"):
                                                    photo_url = f"https://photo.2gis.com{photo_url}" if photo_url.startswith("/") else f"https://photo.2gis.com/{photo_url}"
                                                photos.append(photo_url)
                                        if not photos:
                                            photos = None
                    except Exception as e:
                        logger.debug(f"Не удалось получить фотографии для отеля {hotel_id}: {e}")
                        photos = None
                
                hotel = Hotel(
                    id=hotel_id,
                    name=name,
                    address=address_obj if address_obj else None,
                    lat=item_lat,
                    lon=item_lon,
                    rating=rating,
                    phone=phone,
                    website=website,
                    url=hotel_url,
                    photos=photos
                )
                hotels.append(hotel)
            
            # Если набрали нужное количество или больше нет страниц, выходим
            if len(hotels) >= target_count or len(items) < page_size:
                break
            
            page += 1
    
    return hotels


async def get_route_map(lat_from: float, lon_from: float, lat_to: float, lon_to: float) -> str:
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("2GIS API key not configured")
    
    center_lat = (lat_from + lat_to) / 2
    center_lon = (lon_from + lon_to) / 2
    
    static_params = {
        "s": "600x400",
        "c": f"{center_lat},{center_lon}",
        "z": "15",
        "pt": f"{lat_from},{lon_from}~{lat_to},{lon_to}"
    }
    
    map_url = f"{STATIC_API_BASE}/1.0?{urlencode(static_params)}"
    
    return map_url

