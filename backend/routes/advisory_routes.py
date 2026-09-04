from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from models.weather import WeatherData, AirQualityData
from models.profile import UserProfile
from models.advisory import AdvisoryResponse
from services.weather_service import weather_service
from services.ai_advisory_service import ai_advisory_service
from services.risk_engine import compute_risk_score

router = APIRouter(prefix="/api/advisory", tags=["advisory"])

@router.post("/generate", response_model=AdvisoryResponse)
async def generate_advisory(payload: Dict[str, Any] = Body(...)):
    """
    Generates personalized health advisory.
    Can accept:
    1. Pre-fetched `weather`, `air_quality`, and `profile` objects, OR
    2. `latitude`, `longitude`, and `profile` to fetch on-the-fly.
    """
    try:
        profile_dict = payload.get("profile", {})
        profile = UserProfile(**profile_dict)

        if "weather" in payload and "air_quality" in payload:
            weather = WeatherData(**payload["weather"])
            aqi_data = AirQualityData(**payload["air_quality"])
        else:
            lat = float(payload.get("latitude", 22.7196))
            lon = float(payload.get("longitude", 75.8577))
            import asyncio
            weather, aqi_data = await asyncio.gather(
                weather_service.get_current_weather(lat, lon),
                weather_service.get_air_quality(lat, lon)
            )

        advisory = await ai_advisory_service.generate_advisory(weather, aqi_data, profile)
        return advisory
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advisory generation failed: {str(e)}")

@router.post("/risk-score")
async def get_risk_score(payload: Dict[str, Any] = Body(...)):
    """Computes only the personalized risk score from 0-100 without invoking full advisory."""
    try:
        profile = UserProfile(**payload.get("profile", {}))
        weather = WeatherData(**payload["weather"])
        aqi_data = AirQualityData(**payload["air_quality"])
        risk = compute_risk_score(weather, aqi_data, profile)
        return risk
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk calculation failed: {str(e)}")
