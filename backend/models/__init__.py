# Models package for AeroHealth AI
from .weather import WeatherData, AirQualityData, LocationInfo, ForecastDay, HistoricalTrend
from .profile import UserProfile
from .advisory import AdvisoryResponse, RiskAssessment

__all__ = [
    "WeatherData",
    "AirQualityData",
    "LocationInfo",
    "ForecastDay",
    "HistoricalTrend",
    "UserProfile",
    "AdvisoryResponse",
    "RiskAssessment",
]
