from pydantic import BaseModel, Field
from typing import List, Optional

class WeatherData(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Apparent temperature in Celsius")
    humidity: int = Field(..., description="Relative humidity percentage")
    wind_speed: float = Field(..., description="Wind speed in km/h")
    rain_probability: int = Field(..., description="Precipitation probability percentage")
    uv_index: float = Field(..., description="UV Index")
    weather_code: int = Field(..., description="WMO Weather condition code")
    weather_condition: str = Field(..., description="Human readable condition string")
    weather_icon: str = Field(..., description="Icon identifier")
    is_day: bool = Field(True, description="True if day time")
    source: str = Field("open-meteo", description="Data source used")

class AirQualityData(BaseModel):
    aqi: int = Field(..., description="US Air Quality Index")
    aqi_status: str = Field(..., description="Category: Good, Moderate, Unhealthy for Sensitive Groups, Unhealthy, Very Unhealthy, Hazardous")
    aqi_color: str = Field(..., description="Color hex code matching status")
    pm2_5: float = Field(..., description="PM2.5 particulate matter in µg/m³")
    pm10: float = Field(..., description="PM10 particulate matter in µg/m³")
    carbon_monoxide: Optional[float] = Field(None, description="CO in µg/m³")
    nitrogen_dioxide: Optional[float] = Field(None, description="NO2 in µg/m³")
    ozone: Optional[float] = Field(None, description="O3 in µg/m³")

class LocationInfo(BaseModel):
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    admin1: Optional[str] = None

class ForecastDay(BaseModel):
    date: str
    day_name: str
    temp_max: float
    temp_min: float
    rain_probability: int
    uv_index: float
    weather_code: int
    weather_condition: str

class TrendPoint(BaseModel):
    date: str
    label: str
    temperature: Optional[float] = None
    aqi: Optional[int] = None
    pm2_5: Optional[float] = None

class HistoricalTrend(BaseModel):
    trends: List[TrendPoint]
