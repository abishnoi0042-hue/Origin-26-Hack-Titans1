from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
import asyncio
from models.weather import WeatherData, AirQualityData, LocationInfo
from services.weather_service import weather_service

router = APIRouter(prefix="/api/weather", tags=["weather"])

@router.get("/current", response_model=WeatherData)
async def get_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    try:
        return await weather_service.get_current_weather(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")

@router.get("/air-quality", response_model=AirQualityData)
async def get_air_quality(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    try:
        return await weather_service.get_air_quality(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch air quality data: {str(e)}")

@router.get("/all")
async def get_all_weather_data(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    location_name: str = Query(None, description="Optional city name")
):
    """Combined endpoint for lightning-fast dashboard load."""
    try:
        # 1. Fetch weather and AQI concurrently
        weather, aqi = await asyncio.gather(
            weather_service.get_current_weather(lat, lon),
            weather_service.get_air_quality(lat, lon)
        )

        resolved_location = location_name or "Live Location"
        country = None
        admin1 = None

        # 2. If no location name provided, resolve location with quick 1.5s timeout so it never blocks
        if not location_name or location_name == "Live Location":
            try:
                loc = await asyncio.wait_for(weather_service.reverse_geocode(lat, lon), timeout=1.5)
                resolved_location = loc.name
                country = loc.country
                admin1 = loc.admin1
            except Exception:
                pass

        return {
            "weather": weather,
            "air_quality": aqi,
            "location": {
                "name": resolved_location,
                "latitude": lat,
                "longitude": lon,
                "country": country,
                "admin1": admin1
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch environmental data: {str(e)}")

@router.get("/trends")
async def get_trends(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    try:
        trends = await weather_service.get_7day_trends(lat, lon)
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")

@router.get("/search", response_model=List[LocationInfo])
async def search_cities(
    q: str = Query(..., min_length=2, description="City search query")
):
    try:
        return await weather_service.search_cities(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding search failed: {str(e)}")

@router.get("/reverse-geocode", response_model=LocationInfo)
async def reverse_geocode(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    try:
        return await weather_service.reverse_geocode(lat, lon)
    except Exception as e:
        return LocationInfo(name="Live Location", latitude=lat, longitude=lon)
