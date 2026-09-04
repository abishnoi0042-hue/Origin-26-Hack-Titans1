import asyncio
import httpx
import json
from services.weather_service import weather_service
from services.risk_engine import compute_risk_score
from services.fallback_advisory import generate_fallback_advisory
from services.ai_advisory_service import ai_advisory_service
from models.profile import UserProfile

async def run_verification():
    print("==================================================")
    print("AEROHEALTH AI – SYSTEM VERIFICATION TEST SUITE")
    print("==================================================")

    # 1. Test Geocoding Search
    print("\n[1/5] Testing Open-Meteo Geocoding for 'Indore' and 'Tokyo'...")
    cities_indore = await weather_service.search_cities("Indore")
    assert len(cities_indore) > 0, "Indore search should return results"
    print(f"  -> Found {len(cities_indore)} matches: {cities_indore[0].name}, {cities_indore[0].country}")

    cities_tokyo = await weather_service.search_cities("Tokyo")
    assert len(cities_tokyo) > 0, "Tokyo search should return results"
    print(f"  -> Found {len(cities_tokyo)} matches: {cities_tokyo[0].name}, {cities_tokyo[0].country}")

    # 2. Test Live Weather Telemetry
    print("\n[2/5] Testing Real-Time Weather Fetch for Indore (22.72, 75.83)...")
    weather = await weather_service.get_current_weather(22.7179, 75.8333)
    print(f"  -> Temp: {weather.temperature}°C, Feels: {weather.feels_like}°C, Humidity: {weather.humidity}%, Condition: {weather.weather_condition}")
    assert weather.temperature is not None

    # 3. Test Live Air Quality
    print("\n[3/5] Testing Real-Time Air Quality Fetch...")
    aqi = await weather_service.get_air_quality(22.7179, 75.8333)
    print(f"  -> US AQI: {aqi.aqi} ({aqi.aqi_status}), PM2.5: {aqi.pm2_5} µg/m³, PM10: {aqi.pm10} µg/m³")
    assert aqi.aqi >= 0

    # 4. Test 7-Day Trends
    print("\n[4/5] Testing 7-Day Environmental Trends Fetch...")
    trends = await weather_service.get_7day_trends(22.7179, 75.8333)
    print(f"  -> Retrieved {len(trends)} daily trend data points.")
    assert len(trends) > 0

    # 5. Test Risk Engine & AI Advisory for 4 Scenarios
    print("\n[5/5] Testing Risk Engine & AI Advisories across 4 Personas:")
    
    personas = [
        ("Healthy Adult", UserProfile(name="Alex", age_group="Adult", health_conditions=["None"], occupation="Indoor Worker", activity_level="Moderate")),
        ("Asthma Patient", UserProfile(name="Maya", age_group="Teen", health_conditions=["Asthma"], occupation="Student", activity_level="High")),
        ("Outdoor Worker", UserProfile(name="Carlos", age_group="Adult", health_conditions=["Allergies"], occupation="Outdoor Worker", activity_level="High")),
        ("Elderly Person", UserProfile(name="Eleanor", age_group="Elderly", health_conditions=["Heart Disease", "Respiratory Problems"], occupation="Other", activity_level="Low")),
    ]

    for title, prof in personas:
        risk = compute_risk_score(weather, aqi, prof)
        advisory = await ai_advisory_service.generate_advisory(weather, aqi, prof)
        print(f"\n  Persona: {title} ({prof.name})")
        print(f"    - Risk Score: {risk.score}/100 [{risk.level}]")
        print(f"    - Engine Used: {advisory.ai_provider}")
        print(f"    - Primary Drivers: {risk.primary_factors}")
        print(f"    - Summary: {advisory.summary[:100]}...")
        print(f"    - Outdoor Rec: {advisory.outdoor_activity}")
        print(f"    - Precautions: {len(advisory.health_precautions)} health, {len(advisory.weather_precautions)} weather")
        print(f"    - Best Window: {advisory.best_time_outside}")

    print("\n==================================================")
    print("ALL 5 BACKEND VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
