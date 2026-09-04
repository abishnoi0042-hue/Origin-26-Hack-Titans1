import os
import httpx
from typing import Dict, Any, List, Optional
from models.weather import WeatherData, AirQualityData, LocationInfo, ForecastDay, HistoricalTrend, TrendPoint

# WMO Weather interpretation code (WW)
WMO_WEATHER_MAP = {
    0: ("Clear sky", "sun", True),
    1: ("Mainly clear", "sun", True),
    2: ("Partly cloudy", "cloud-sun", True),
    3: ("Overcast", "cloud", False),
    45: ("Fog", "cloud-fog", False),
    48: ("Depositing rime fog", "cloud-fog", False),
    51: ("Light drizzle", "cloud-drizzle", False),
    53: ("Moderate drizzle", "cloud-drizzle", False),
    55: ("Dense drizzle", "cloud-drizzle", False),
    56: ("Light freezing drizzle", "cloud-hail", False),
    57: ("Dense freezing drizzle", "cloud-hail", False),
    61: ("Slight rain", "cloud-rain", False),
    63: ("Moderate rain", "cloud-rain", False),
    65: ("Heavy rain", "cloud-rain-heavy", False),
    66: ("Light freezing rain", "cloud-snow", False),
    67: ("Heavy freezing rain", "cloud-snow", False),
    71: ("Slight snow fall", "snowflake", False),
    73: ("Moderate snow fall", "snowflake", False),
    75: ("Heavy snow fall", "snowflake", False),
    77: ("Snow grains", "snowflake", False),
    80: ("Slight rain showers", "cloud-sun-rain", True),
    81: ("Moderate rain showers", "cloud-rain", False),
    82: ("Violent rain showers", "cloud-lightning-rain", False),
    85: ("Slight snow showers", "cloud-snow", False),
    86: ("Heavy snow showers", "cloud-snow", False),
    95: ("Thunderstorm", "cloud-lightning", False),
    96: ("Thunderstorm with slight hail", "cloud-lightning", False),
    99: ("Thunderstorm with heavy hail", "cloud-lightning", False),
}

def get_aqi_info(aqi_val: int) -> tuple[str, str]:
    """Return status label and color hex code for US AQI value."""
    if aqi_val <= 50:
        return "Good", "#10b981"  # Emerald Green
    elif aqi_val <= 100:
        return "Moderate", "#f59e0b"  # Amber Yellow
    elif aqi_val <= 150:
        return "Unhealthy for Sensitive Groups", "#f97316"  # Orange
    elif aqi_val <= 200:
        return "Unhealthy", "#ef4444"  # Red
    elif aqi_val <= 300:
        return "Very Unhealthy", "#8b5cf6"  # Purple
    else:
        return "Hazardous", "#7f1d1d"  # Deep Maroon

class WeatherService:
    def __init__(self):
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()

    async def get_current_weather(self, lat: float, lon: float) -> WeatherData:
        """Fetch live weather metrics from Open-Meteo."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,weather_code,wind_speed_10m,uv_index,is_day"
                f"&timezone=auto"
            )
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            curr = data.get("current", {})

            w_code = int(curr.get("weather_code", 0))
            cond_desc, icon_name, _ = WMO_WEATHER_MAP.get(w_code, ("Clear sky", "sun", True))
            is_day = bool(curr.get("is_day", 1))

            return WeatherData(
                temperature=round(float(curr.get("temperature_2m", 20.0)), 1),
                feels_like=round(float(curr.get("apparent_temperature", curr.get("temperature_2m", 20.0))), 1),
                humidity=int(curr.get("relative_humidity_2m", 50)),
                wind_speed=round(float(curr.get("wind_speed_10m", 5.0)), 1),
                rain_probability=int(curr.get("precipitation_probability", 0)),
                uv_index=round(float(curr.get("uv_index", 1.0)), 1),
                weather_code=w_code,
                weather_condition=cond_desc,
                weather_icon=icon_name,
                is_day=is_day,
                source="open-meteo"
            )

    async def get_air_quality(self, lat: float, lon: float) -> AirQualityData:
        """Fetch live AQI and pollutant concentrations from Open-Meteo Air Quality API."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality"
                f"?latitude={lat}&longitude={lon}"
                f"&current=us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone"
                f"&timezone=auto"
            )
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            curr = data.get("current", {})

            raw_aqi = curr.get("us_aqi")
            pm25 = float(curr.get("pm2_5", 15.0) or 15.0)
            pm10 = float(curr.get("pm10", 30.0) or 30.0)

            # If US AQI is None from API, compute empirical EPA approximation from PM2.5
            if raw_aqi is not None and raw_aqi > 0:
                aqi = int(raw_aqi)
            else:
                # EPA PM2.5 to AQI linear piecewise approximation
                if pm25 <= 12.0:
                    aqi = int((50 / 12.0) * pm25)
                elif pm25 <= 35.4:
                    aqi = int(51 + ((100 - 51) / (35.4 - 12.1)) * (pm25 - 12.1))
                elif pm25 <= 55.4:
                    aqi = int(101 + ((150 - 101) / (55.4 - 35.5)) * (pm25 - 35.5))
                elif pm25 <= 150.4:
                    aqi = int(151 + ((200 - 151) / (150.4 - 55.5)) * (pm25 - 55.5))
                else:
                    aqi = int(201 + ((300 - 201) / (250.4 - 150.5)) * (min(pm25, 250.0) - 150.5))

            status, color = get_aqi_info(aqi)

            return AirQualityData(
                aqi=aqi,
                aqi_status=status,
                aqi_color=color,
                pm2_5=round(pm25, 1),
                pm10=round(pm10, 1),
                carbon_monoxide=round(float(curr.get("carbon_monoxide") or 0.0), 1) if curr.get("carbon_monoxide") is not None else None,
                nitrogen_dioxide=round(float(curr.get("nitrogen_dioxide") or 0.0), 1) if curr.get("nitrogen_dioxide") is not None else None,
                ozone=round(float(curr.get("ozone") or 0.0), 1) if curr.get("ozone") is not None else None,
            )

    async def get_7day_trends(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Fetch 7-day weather and environmental trends."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&daily=temperature_2m_max,temperature_2m_min,uv_index_max,precipitation_probability_max,weather_code"
                f"&past_days=3&forecast_days=4"
                f"&timezone=auto"
            )
            aqi_url = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality"
                f"?latitude={lat}&longitude={lon}"
                f"&daily=pm10_max,pm2_5_max,us_aqi_max"
                f"&past_days=3&forecast_days=4"
                f"&timezone=auto"
            )

            # Concurrent fetch
            w_resp, aqi_resp = await client.get(weather_url), await client.get(aqi_url)
            w_data = w_resp.json().get("daily", {})
            aqi_data = aqi_resp.json().get("daily", {})

            dates = w_data.get("time", [])
            trends = []

            for i, d in enumerate(dates):
                t_max = w_data.get("temperature_2m_max", [25.0])[i] if i < len(w_data.get("temperature_2m_max", [])) else 25.0
                t_min = w_data.get("temperature_2m_min", [18.0])[i] if i < len(w_data.get("temperature_2m_min", [])) else 18.0
                avg_temp = round((t_max + t_min) / 2.0, 1)

                aqi_val = None
                if "us_aqi_max" in aqi_data and i < len(aqi_data["us_aqi_max"]) and aqi_data["us_aqi_max"][i] is not None:
                    aqi_val = int(aqi_data["us_aqi_max"][i])
                
                pm25_val = None
                if "pm2_5_max" in aqi_data and i < len(aqi_data["pm2_5_max"]) and aqi_data["pm2_5_max"][i] is not None:
                    pm25_val = round(float(aqi_data["pm2_5_max"][i]), 1)

                if aqi_val is None and pm25_val is not None:
                    # Estimate AQI from PM2.5 if missing
                    aqi_val = int(min(300, max(20, pm25_val * 2.2)))
                elif aqi_val is None:
                    aqi_val = 55  # default moderate

                import datetime
                try:
                    dt = datetime.date.fromisoformat(d)
                    label = dt.strftime("%a %d")
                except Exception:
                    label = d

                trends.append({
                    "date": d,
                    "label": label,
                    "temperature": avg_temp,
                    "temp_max": t_max,
                    "temp_min": t_min,
                    "aqi": aqi_val,
                    "pm2_5": pm25_val if pm25_val is not None else 18.0,
                    "uv_index": w_data.get("uv_index_max", [2.0])[i] if i < len(w_data.get("uv_index_max", [])) else 2.0,
                    "rain_probability": w_data.get("precipitation_probability_max", [0])[i] if i < len(w_data.get("precipitation_probability_max", [])) else 0,
                })

            return trends

    async def search_cities(self, query: str) -> List[LocationInfo]:
        """Search cities using Open-Meteo Geocoding API."""
        if not query or len(query.strip()) < 2:
            return []

        async with httpx.AsyncClient(timeout=8.0) as client:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={query.strip()}&count=6&language=en&format=json"
            response = await client.get(url)
            if response.status_code != 200:
                return []
            data = response.json()
            results = data.get("results", [])
            locations = []
            for r in results:
                locations.append(LocationInfo(
                    name=r.get("name", "Unknown"),
                    latitude=r.get("latitude", 0.0),
                    longitude=r.get("longitude", 0.0),
                    country=r.get("country"),
                    admin1=r.get("admin1"),
                ))
            return locations

    async def reverse_geocode(self, lat: float, lon: float) -> LocationInfo:
        """Determine human-friendly city/region name from coordinates."""
        # 1. If OpenWeather API key available, query OpenWeather geocoding
        if self.openweather_api_key:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    ow_url = f"https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={self.openweather_api_key}"
                    resp = await client.get(ow_url)
                    if resp.status_code == 200:
                        items = resp.json()
                        if items:
                            first = items[0]
                            return LocationInfo(
                                name=first.get("name", "Live Location"),
                                latitude=lat,
                                longitude=lon,
                                country=first.get("country"),
                                admin1=first.get("state"),
                            )
            except Exception:
                pass

        # 2. Query OpenStreetMap Nominatim with proper user-agent
        try:
            async with httpx.AsyncClient(timeout=5.0, headers={"User-Agent": "AeroHealthAI/1.0"}) as client:
                nom_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
                resp = await client.get(nom_url)
                if resp.status_code == 200:
                    data = resp.json()
                    addr = data.get("address", {})
                    city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or addr.get("state_district") or "Live Location"
                    country = addr.get("country")
                    state = addr.get("state")
                    return LocationInfo(
                        name=city,
                        latitude=lat,
                        longitude=lon,
                        country=country,
                        admin1=state
                    )
        except Exception:
            pass

        return LocationInfo(name="Live Location", latitude=lat, longitude=lon)

weather_service = WeatherService()
