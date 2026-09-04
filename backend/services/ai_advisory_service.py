import os
import json
import logging
import httpx
from typing import Dict, Any, Optional
from models.weather import WeatherData, AirQualityData
from models.profile import UserProfile
from models.advisory import AdvisoryResponse, RiskAssessment
from services.risk_engine import compute_risk_score
from services.fallback_advisory import generate_fallback_advisory

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are AeroHealth AI, a personalized environmental health advisory assistant.

Your task is to analyze weather conditions, air quality data, and a user's personal profile to generate a clear and practical health advisory.

Consider:
- Temperature
- Humidity
- UV Index
- Wind
- Rain
- AQI
- PM2.5
- PM10
- Age Group
- Health Conditions
- Occupation
- Activity Level

Generate personalized recommendations.
Use simple plain English.
Do not diagnose diseases.
Do not cause unnecessary fear.
Clearly explain WHY a recommendation is being made.

Return structured JSON with:
{
  "risk_level": "Low" | "Moderate" | "High" | "Severe",
  "summary": "Clear, personalized explanation explaining WHY",
  "outdoor_activity": "Concrete recommendation regarding outdoor time",
  "health_precautions": ["precaution 1", "precaution 2"],
  "weather_precautions": ["precaution 1", "precaution 2"],
  "best_time_outside": "specific time window recommendation",
  "things_to_avoid": ["item 1", "item 2"]
}
Only output valid JSON, no conversational markdown or backticks."""

class AIAdvisoryService:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()

    def _format_user_prompt(
        self,
        weather: WeatherData,
        aqi_data: AirQualityData,
        profile: UserProfile,
        risk: RiskAssessment
    ) -> str:
        conditions_str = ", ".join(profile.health_conditions) if profile.health_conditions else "None"
        return f"""Environmental & Profile Context:
- Location Weather: Temp {weather.temperature}°C (Feels like {weather.feels_like}°C), Humidity {weather.humidity}%, Wind {weather.wind_speed} km/h, Rain Prob {weather.rain_probability}%, UV Index {weather.uv_index}, Condition: {weather.weather_condition}
- Air Quality: US AQI {aqi_data.aqi} ({aqi_data.aqi_status}), PM2.5 {aqi_data.pm2_5} µg/m³, PM10 {aqi_data.pm10} µg/m³
- User Profile: Age Group: {profile.age_group}, Health Conditions: {conditions_str}, Occupation: {profile.occupation}, Activity Level: {profile.activity_level}
- Calculated Environmental Risk Score: {risk.score}/100 (Calculated Level: {risk.level})
- Primary Stress Factors: {', '.join(risk.primary_factors)}

Generate the personalized health advisory following the required JSON schema."""

    async def generate_advisory(
        self,
        weather: WeatherData,
        aqi_data: AirQualityData,
        profile: UserProfile
    ) -> AdvisoryResponse:
        # First, compute algorithmic risk assessment
        risk = compute_risk_score(weather, aqi_data, profile)

        # 1. Try Google Gemini if key provided
        if self.gemini_key:
            try:
                advisory = await self._call_gemini(weather, aqi_data, profile, risk)
                if advisory:
                    return advisory
            except Exception as e:
                logger.warning(f"Gemini API call failed, trying fallback: {e}")

        # 2. Try Groq if key provided
        if self.groq_key:
            try:
                advisory = await self._call_groq(weather, aqi_data, profile, risk)
                if advisory:
                    return advisory
            except Exception as e:
                logger.warning(f"Groq API call failed, trying fallback: {e}")

        # 3. Always succeed with comprehensive smart rule-based generator
        return generate_fallback_advisory(weather, aqi_data, profile, risk)

    async def _call_gemini(
        self,
        weather: WeatherData,
        aqi_data: AirQualityData,
        profile: UserProfile,
        risk: RiskAssessment
    ) -> Optional[AdvisoryResponse]:
        user_prompt = self._format_user_prompt(weather, aqi_data, profile, risk)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": SYSTEM_PROMPT + "\n\n" + user_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                res_data = resp.json()
                raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(raw_text)
                return self._build_response(parsed, risk, "gemini")
        return None

    async def _call_groq(
        self,
        weather: WeatherData,
        aqi_data: AirQualityData,
        profile: UserProfile,
        risk: RiskAssessment
    ) -> Optional[AdvisoryResponse]:
        user_prompt = self._format_user_prompt(weather, aqi_data, profile, risk)
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                res_data = resp.json()
                raw_text = res_data["choices"][0]["message"]["content"]
                parsed = json.loads(raw_text)
                return self._build_response(parsed, risk, "groq")
        return None

    def _build_response(self, data: Dict[str, Any], risk: RiskAssessment, provider: str) -> AdvisoryResponse:
        risk_level = data.get("risk_level", risk.level)
        if risk_level not in ["Low", "Moderate", "High", "Severe"]:
            risk_level = risk.level

        return AdvisoryResponse(
            risk_level=risk_level,
            risk_score=risk.score,
            summary=data.get("summary", ""),
            outdoor_activity=data.get("outdoor_activity", ""),
            health_precautions=data.get("health_precautions", []),
            weather_precautions=data.get("weather_precautions", []),
            best_time_outside=data.get("best_time_outside", ""),
            things_to_avoid=data.get("things_to_avoid", []),
            risk_breakdown={
                "environmental_stress": risk.environmental_score,
                "vulnerability_multiplier": risk.vulnerability_multiplier,
                "primary_factors": risk.primary_factors
            },
            ai_provider=provider
        )

ai_advisory_service = AIAdvisoryService()
