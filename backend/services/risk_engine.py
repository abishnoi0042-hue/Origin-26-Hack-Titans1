from typing import Dict, Any, List, Tuple
from models.weather import WeatherData, AirQualityData
from models.profile import UserProfile
from models.advisory import RiskAssessment

def compute_risk_score(
    weather: WeatherData,
    aqi_data: AirQualityData,
    profile: UserProfile
) -> RiskAssessment:
    """
    Computes a personalized environmental health risk score from 0 to 100
    by cross-referencing environmental hazards with personal vulnerability factors.
    """
    primary_factors: List[str] = []

    # 1. Base AQI Stress (0 - 100 scale)
    aqi = aqi_data.aqi
    if aqi <= 50:
        aqi_stress = (aqi / 50.0) * 20.0
    elif aqi <= 100:
        aqi_stress = 20.0 + ((aqi - 50.0) / 50.0) * 25.0
    elif aqi <= 150:
        aqi_stress = 45.0 + ((aqi - 100.0) / 50.0) * 25.0
    elif aqi <= 200:
        aqi_stress = 70.0 + ((aqi - 150.0) / 50.0) * 15.0
    else:
        aqi_stress = 85.0 + min(15.0, ((aqi - 200.0) / 100.0) * 15.0)

    # 2. Temperature Thermal Stress (0 - 100 scale)
    feels_like = weather.feels_like
    if 18.0 <= feels_like <= 25.0:
        temp_stress = 5.0  # Comfortable thermal zone
    elif feels_like > 25.0:
        # Heat stress ramps up steeply above 32°C
        if feels_like <= 32.0:
            temp_stress = 10.0 + ((feels_like - 25.0) / 7.0) * 25.0
        elif feels_like <= 38.0:
            temp_stress = 35.0 + ((feels_like - 32.0) / 6.0) * 35.0
        else:
            temp_stress = 70.0 + min(30.0, ((feels_like - 38.0) / 10.0) * 30.0)
    else:
        # Cold stress ramps up below 10°C
        if feels_like >= 10.0:
            temp_stress = 10.0 + ((18.0 - feels_like) / 8.0) * 20.0
        elif feels_like >= 0.0:
            temp_stress = 30.0 + ((10.0 - feels_like) / 10.0) * 35.0
        else:
            temp_stress = 65.0 + min(35.0, (abs(feels_like) / 20.0) * 35.0)

    # 3. UV Stress (0 - 100 scale)
    uv = weather.uv_index
    if uv <= 2.0:
        uv_stress = uv * 7.5  # 0-15
    elif uv <= 5.0:
        uv_stress = 15.0 + ((uv - 2.0) / 3.0) * 25.0  # 15-40
    elif uv <= 7.0:
        uv_stress = 40.0 + ((uv - 5.0) / 2.0) * 30.0  # 40-70
    elif uv <= 10.0:
        uv_stress = 70.0 + ((uv - 7.0) / 3.0) * 20.0  # 70-90
    else:
        uv_stress = 95.0

    # 4. Wind & Rain Stress (0 - 100 scale)
    wind_stress = min(100.0, (weather.wind_speed / 60.0) * 100.0)
    rain_stress = float(weather.rain_probability)

    # Combined base environmental stress (unweighted baseline: 0-100)
    base_env = (
        0.45 * aqi_stress +
        0.25 * temp_stress +
        0.18 * uv_stress +
        0.12 * ((wind_stress + rain_stress) / 2.0)
    )

    # 5. Personal Vulnerability Modifiers
    aqi_multiplier = 1.0
    temp_multiplier = 1.0
    uv_multiplier = 1.0
    overall_multiplier = 1.0

    # Health conditions
    has_asthma = profile.has_condition("Asthma")
    has_heart = profile.has_condition("Heart Disease")
    has_resp = profile.has_condition("Respiratory Problems")
    has_allergies = profile.has_condition("Allergies")

    if has_asthma:
        aqi_multiplier += 0.55
        if aqi > 50 or aqi_data.pm2_5 > 25:
            primary_factors.append("Asthma sensitivity to particulate matter & AQI")
    if has_resp:
        aqi_multiplier += 0.50
        temp_multiplier += 0.25
        if aqi > 50:
            primary_factors.append("Respiratory vulnerability under current ambient conditions")
    if has_heart:
        temp_multiplier += 0.55
        aqi_multiplier += 0.35
        if feels_like > 32 or feels_like < 5 or aqi > 75:
            primary_factors.append("Cardiovascular strain from temperature/air quality")
    if has_allergies:
        aqi_multiplier += 0.25
        if weather.wind_speed > 15 or aqi > 70:
            primary_factors.append("Allergy susceptibility exacerbated by wind and airborne particulates")

    # Age Group
    if profile.age_group == "Child":
        aqi_multiplier += 0.30
        uv_multiplier += 0.25
        if aqi > 50:
            primary_factors.append("Developing pediatric pulmonary system needs protection")
    elif profile.age_group == "Elderly":
        temp_multiplier += 0.45
        aqi_multiplier += 0.35
        if feels_like > 30 or feels_like < 10:
            primary_factors.append("Elderly thermoregulation risk during extreme temperatures")
    elif profile.age_group == "Teen":
        aqi_multiplier += 0.05

    # Occupation Exposure
    if profile.occupation == "Outdoor Worker":
        uv_multiplier += 0.45
        temp_multiplier += 0.40
        aqi_multiplier += 0.35
        primary_factors.append("Prolonged ambient occupational exposure")
    elif profile.occupation == "Athlete":
        aqi_multiplier += 0.30
        temp_multiplier += 0.25
        primary_factors.append("Elevated ventilation rate and exposure during athletic exertion")
    elif profile.occupation == "Student":
        aqi_multiplier += 0.05
    elif profile.occupation == "Indoor Worker":
        overall_multiplier *= 0.90

    # Activity Level (Higher ventilation = more air inhaled)
    if profile.activity_level == "High":
        aqi_multiplier += 0.25
        temp_multiplier += 0.20
    elif profile.activity_level == "Low":
        overall_multiplier *= 0.92

    # Weighted personal environmental composite
    personalized_aqi_stress = min(100.0, aqi_stress * aqi_multiplier)
    personalized_temp_stress = min(100.0, temp_stress * temp_multiplier)
    personalized_uv_stress = min(100.0, uv_stress * uv_multiplier)

    composite_score = (
        0.45 * personalized_aqi_stress +
        0.25 * personalized_temp_stress +
        0.18 * personalized_uv_stress +
        0.12 * ((wind_stress + rain_stress) / 2.0)
    ) * overall_multiplier

    final_score = int(round(max(0.0, min(100.0, composite_score))))

    # Determine Risk Level Category
    if final_score <= 25:
        level = "Low"
        color = "#10b981"  # Green
        if not primary_factors:
            primary_factors.append("Favorable environmental conditions for your profile")
    elif final_score <= 50:
        level = "Moderate"
        color = "#f59e0b"  # Amber
        if not primary_factors:
            primary_factors.append("Moderate ambient factors require mild precautions")
    elif final_score <= 75:
        level = "High"
        color = "#f97316"  # Orange
        if not primary_factors:
            primary_factors.append("Significant environmental stress relative to your health profile")
    else:
        level = "Severe"
        color = "#ef4444"  # Red
        if not primary_factors:
            primary_factors.append("Hazardous environmental conditions posing immediate health risks")

    effective_multiplier = round(final_score / max(1.0, base_env), 2)

    return RiskAssessment(
        score=final_score,
        level=level,
        color=color,
        primary_factors=primary_factors[:4],
        environmental_score=int(round(base_env)),
        vulnerability_multiplier=effective_multiplier
    )
