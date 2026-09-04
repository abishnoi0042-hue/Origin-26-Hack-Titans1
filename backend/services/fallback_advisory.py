from typing import Dict, Any, List
from models.weather import WeatherData, AirQualityData
from models.profile import UserProfile
from models.advisory import AdvisoryResponse, RiskAssessment
from services.risk_engine import compute_risk_score

def generate_fallback_advisory(
    weather: WeatherData,
    aqi_data: AirQualityData,
    profile: UserProfile,
    risk: RiskAssessment
) -> AdvisoryResponse:
    """
    Intelligent, rule-based clinical advisory generator that constructs personalized,
    context-aware health advisories when an external LLM API is unavailable or disabled.
    """
    has_asthma = profile.has_condition("Asthma")
    has_heart = profile.has_condition("Heart Disease")
    has_resp = profile.has_condition("Respiratory Problems")
    has_allergies = profile.has_condition("Allergies")
    is_outdoor = profile.occupation in ["Outdoor Worker", "Athlete"]
    is_elderly = profile.age_group == "Elderly"
    is_child = profile.age_group == "Child"

    health_precautions: List[str] = []
    weather_precautions: List[str] = []
    things_to_avoid: List[str] = []

    # 1. Summary Generation Logic based on primary risk drivers
    summary_parts = []

    if has_asthma and (aqi_data.aqi > 70 or aqi_data.pm2_5 > 25):
        summary_parts.append(
            f"Because you have asthma and the current AQI is {aqi_data.aqi} with PM2.5 at {aqi_data.pm2_5} µg/m³, "
            f"your airway is particularly susceptible to bronchospasm and irritation today. Limit prolonged outdoor exertion."
        )
    elif has_resp and aqi_data.aqi > 60:
        summary_parts.append(
            f"Given your respiratory sensitivity and an elevated AQI of {aqi_data.aqi}, particulate matter can trigger coughing "
            f"or shortness of breath. Ensure indoor spaces remain well-filtered."
        )
    elif has_heart and (weather.feels_like > 32 or weather.feels_like < 5):
        summary_parts.append(
            f"As someone managing heart disease, current thermal stress ({weather.feels_like}°C feels-like) "
            f"puts increased workload on your cardiovascular system. Avoid strenuous physical activity outdoors."
        )
    elif is_outdoor and (weather.uv_index >= 6 or weather.feels_like > 30):
        summary_parts.append(
            f"You are an {profile.occupation.lower()} exposed to continuous outdoor conditions. With a high UV index of {weather.uv_index} "
            f"and temperatures around {weather.temperature}°C, active heat and radiation protection is essential."
        )
    elif is_elderly and (weather.feels_like > 30 or aqi_data.aqi > 80):
        summary_parts.append(
            f"For older adults, the combination of temperature ({weather.temperature}°C) and air quality (AQI {aqi_data.aqi}) "
            f"can cause accelerated fatigue and dehydration. Stay in climate-controlled environments when possible."
        )
    elif aqi_data.aqi <= 50 and weather.feels_like <= 28 and weather.uv_index <= 5:
        summary_parts.append(
            f"Environmental conditions are currently clean (AQI {aqi_data.aqi}) and temperature is comfortable at {weather.temperature}°C. "
            f"It is a great day for outdoor activities, work, and exercise."
        )
    else:
        summary_parts.append(
            f"Current conditions show an AQI of {aqi_data.aqi} ({aqi_data.aqi_status}) with temperatures around {weather.temperature}°C. "
            f"Based on your profile as an {profile.age_group.lower()} with {profile.activity_level.lower()} activity, maintain standard precautions."
        )

    summary = " ".join(summary_parts)

    # 2. Outdoor Activity Recommendation
    if risk.level == "Severe":
        outdoor_activity = "Avoid all non-essential outdoor activities. Stay indoors with air filtration and sealed windows."
    elif risk.level == "High":
        if is_outdoor:
            outdoor_activity = "Mandate frequent rest breaks in shaded or indoor areas. Shorten shift intensity and wear protective gear."
        else:
            outdoor_activity = "Significantly reduce outdoor exertion. Relocate workouts and meetings indoors."
    elif risk.level == "Moderate":
        outdoor_activity = "Moderate outdoor activities are generally safe, but take regular breaks and avoid heavy cardiovascular workouts during peak hours."
    else:
        outdoor_activity = "Ideal conditions for outdoor walks, sports, commuting, and recreational activities."

    # 3. Health Precautions
    if has_asthma:
        health_precautions.append("Keep your fast-acting rescue inhaler readily accessible at all times.")
        if aqi_data.aqi > 60:
            health_precautions.append("Wear a well-fitted N95/FFP2 respirator mask if spending more than 15 minutes outdoors.")
    if has_heart:
        health_precautions.append("Monitor blood pressure and pulse; rest immediately if experiencing palpitations or lightheadedness.")
    if has_allergies and (weather.wind_speed > 12 or aqi_data.pm10 > 40):
        health_precautions.append("Take prescribed antihistamines if needed, and rinse your eyes/face after returning indoors to remove allergens.")
    if is_elderly:
        health_precautions.append("Drink water at regular scheduled intervals even if you do not feel thirsty.")
    if is_child:
        health_precautions.append("Ensure hydration during play and schedule outdoor recess during early morning hours.")
    if not health_precautions:
        health_precautions.append("Maintain routine healthy hydration (at least 2.5 - 3 liters throughout the day).")
        health_precautions.append("Monitor for dry eyes, throat tickle, or minor fatigue during extended periods outside.")

    # 4. Weather Precautions
    if weather.uv_index >= 6:
        weather_precautions.append(f"Apply broad-spectrum SPF 50+ sunscreen, wear UV-blocking sunglasses, and don a wide-brim hat (UV Index: {weather.uv_index}).")
    elif weather.uv_index >= 3:
        weather_precautions.append("Apply SPF 30+ sunscreen if outdoors for longer than 30 minutes.")

    if weather.temperature >= 33 or weather.feels_like >= 35:
        weather_precautions.append("High heat danger: Drink cool electrolyte-rich fluids and seek air-conditioned shelter frequently.")
    elif weather.temperature <= 10 or weather.feels_like <= 8:
        weather_precautions.append("Cold stress: Dress in warm breathable layers and protect extremities from chill.")

    if weather.rain_probability >= 50:
        weather_precautions.append(f"High precipitation probability ({weather.rain_probability}%): Carry waterproof gear and anticipate slick surfaces.")

    if weather.wind_speed >= 25:
        weather_precautions.append(f"Brisk winds ({weather.wind_speed} km/h) can disperse surface dust and pollen. Protect sensitive eyes.")

    if not weather_precautions:
        weather_precautions.append("Mild atmospheric conditions: standard comfortable seasonal attire is recommended.")

    # 5. Best Time Outside
    if weather.uv_index >= 6 or weather.temperature >= 32:
        best_time_outside = "Early morning (before 8:30 AM) or evening (after 5:30 PM) when solar radiation and temperatures diminish."
    elif aqi_data.aqi > 100:
        best_time_outside = "Early morning or late afternoon when industrial and vehicular rush-hour emissions settle."
    else:
        best_time_outside = "Late morning to early afternoon (10:00 AM – 3:00 PM) offers the most pleasant conditions today."

    # 6. Things to Avoid
    if aqi_data.aqi > 80:
        things_to_avoid.append("Jogging or cycling along busy roadways and high-traffic corridors.")
        things_to_avoid.append("Opening windows during peak rush-hour traffic.")
    if weather.uv_index >= 6:
        things_to_avoid.append("Unprotected sunbathing or direct exposure between 11:00 AM and 3:00 PM.")
    if weather.temperature >= 32:
        things_to_avoid.append("Excessive caffeine or sugary energy drinks that accelerate dehydration.")
    if has_asthma or has_resp:
        things_to_avoid.append("Wood smoke, burning incense, or vigorous outdoor sprints.")
    if not things_to_avoid:
        things_to_avoid.append("Prolonged sedentary indoor screen time; take advantage of clean ambient conditions.")

    return AdvisoryResponse(
        risk_level=risk.level,
        risk_score=risk.score,
        summary=summary,
        outdoor_activity=outdoor_activity,
        health_precautions=health_precautions,
        weather_precautions=weather_precautions,
        best_time_outside=best_time_outside,
        things_to_avoid=things_to_avoid,
        risk_breakdown={
            "environmental_stress": risk.environmental_score,
            "vulnerability_multiplier": risk.vulnerability_multiplier,
            "primary_factors": risk.primary_factors
        },
        ai_provider="rule_based_fallback"
    )
