# 🌍 AeroHealth AI – Personalized Weather & AQI Health Advisory System

> *"Because environmental risk is personal."*

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Bundler-Vite-646CFF?style=flat&logo=vite)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/Styling-Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css)](https://tailwindcss.com/)
[![Open-Meteo](https://img.shields.io/badge/Weather_&_AQI-Open--Meteo-blue?style=flat)](https://open-meteo.com/)
[![Free LLMs](https://img.shields.io/badge/AI-Gemini_%2F_Groq_%2F_Fallback-purple?style=flat)](https://aistudio.google.com/)

---

## 📌 Problem Statement

Traditional weather applications and municipal Air Quality Index (AQI) alerts broadcast generic, one-size-fits-all warnings (e.g., *"Air quality is Moderate today"*). However, human environmental vulnerability is fundamentally uneven:

- **An individual with Asthma** experiences bronchial spasms and airway inflammation at PM2.5 levels that a healthy adult can safely tolerate.
- **An Outdoor Worker** (e.g., construction, transit, agriculture) faces 8+ hours of continuous solar UV radiation, thermal heat strain, and airborne particulate inhalation.
- **An Elderly Person** or someone with **Heart Disease** possesses reduced thermoregulatory and cardiovascular reserve, making extreme temperatures dangerous.
- **A Healthy Adult** requires sensible hydration rather than restrictive outdoor bans.

Generic alerts fail to explain **why** conditions are hazardous for a specific individual, leading to either complacency or unnecessary fear.

---

## 💡 The AeroHealth AI Solution

**AeroHealth AI** bridges real-time meteorological and atmospheric telemetry with an individual's personal physiological profile. It synthesizes:

$$\text{Live Weather Data} + \text{Live AQI Pollutants} + \text{Personal Health Profile} \longrightarrow \text{Personalized AI Health Advisory}$$

Instead of abstract numbers, users receive actionable, plain-English guidance explaining the exact biological mechanisms at play and practical steps to safeguard their health.

---

## ✨ Core Features

1. **Location-Based Live Weather Dashboard**
   - Instant city search with debounced autocomplete (Open-Meteo Geocoding).
   - One-click HTML5 GPS Geolocation with reverse geocoding.
   - Live telemetry: Temperature, Apparent ("Feels Like") Temperature, Humidity, Wind Speed, Rain Probability, UV Index, and WMO Weather Condition icons.

2. **Real-Time Air Quality Dashboard & Attractive AQI Gauge**
   - US Air Quality Index (AQI) with color-coded status categories:
     - 🟢 **0–50:** Good
     - 🟡 **51–100:** Moderate
     - 🟠 **101–150:** Unhealthy for Sensitive Groups
     - 🔴 **151–200:** Unhealthy
     - 🟣 **201–300:** Very Unhealthy
     - 🟤 **300+:** Hazardous
   - Radial semi-circle gauge with glow accents.
   - Precise pollutant concentrations: **PM2.5**, **PM10**, **Carbon Monoxide (CO)**, **Nitrogen Dioxide (NO₂)**, and **Ozone (O₃)**.

3. **User Personalization Profile**
   - **Age Group:** Child, Teen, Adult, Elderly.
   - **Health Conditions:** None, Asthma, Heart Disease, Respiratory Problems, Allergies (multi-condition support).
   - **Occupation:** Indoor Worker, Outdoor Worker, Student, Athlete, Other.
   - **Activity Level:** Low, Moderate, High (adjusts minute ventilation / inhalation volume).
   - Persistent storage in browser `localStorage`.

4. **🤖 AI Personalized Health Advisory (Main Feature)**
   - Dual-engine architecture:
     - **Free Cloud LLM:** Google Gemini 1.5/2.0 Flash or Groq LLaMA 3.3.
     - **Clinical Rule-Based Fallback Engine:** Built-in heuristic engine guaranteeing 100% uptime with zero API keys required.
   - Structured guidance includes:
     - Overall Personal Risk Level (Low, Moderate, High, Severe).
     - Personalized Summary explaining **WHY**.
     - Outdoor Activity Guidance.
     - Health & Medical Precautions.
     - Weather & Thermal Precautions.
     - Best Time Window to Go Outside.
     - Specific Things to Avoid.
     - Mandatory Medical Disclaimer.

5. **0–100 Composite Personal Risk Scoring Engine**
   - Mathematical algorithm combining base environmental stress with personalized biological multipliers.
   - Interactive circular SVG progress gauge with live score transitions.
   - Transparent breakdown of primary risk drivers (e.g., *"Asthma sensitivity to particulate matter"*, *"Occupational UV exposure"*).

6. **🎨 Dynamic Reactive Weather Backgrounds**
   - Background atmosphere dynamically shifts according to live environmental telemetry:
     - **Sunlit Azure:** Radiant sun flare and warm sky gradients for clear days.
     - **Starlit Night:** Indigo celestial glow with twinkling stardust.
     - **Rainy Cascade:** Deep cobalt slate with falling rain droplet particles.
     - **Electric Thunderstorm:** Atmospheric purple/violet with lightning pulse.
     - **Smog Warning:** Amber-crimson atmospheric alert for high AQI (> 200).
     - **Overcast & Snow:** Diffuse moody slate and crystalline frost particles.
   - Floating **Atmosphere Switcher** pill for instant evaluation during hackathon presentations.

7. **📈 7-Day Environmental Trends (Recharts)**
   - Area charts with smooth curves, gradient fills, and custom tooltips.
   - Interactive tabs to switch between **Temperature (°C)**, **AQI**, and **PM2.5 (µg/m³)**.

8. **🕒 Local Alert History & Archive**
   - Archive advisories with one click.
   - Records timestamp, location, temperature, AQI, risk level, and personalized summary.
   - Individual deletion, search/filtering, and full clear options.

9. **🎯 Interactive Hackathon Demo Mode**
   - 4 pre-configured persona presets for instant comparison:
     1. **Healthy Adult (Alex):** Baseline tolerance, standard hydration.
     2. **Asthma Patient (Maya):** High bronchial sensitivity to PM2.5.
     3. **Outdoor Worker (Carlos):** High UV, heat exhaustion, and long exposure.
     4. **Elderly Person (Eleanor):** Cardiovascular and respiratory vulnerability.

---

## 🏗️ Architecture & Workflow

```
[ Browser / Client: React + Vite + Tailwind ]
       │
       ├─► Live Geolocation (GPS) / City Search
       ├─► Dynamic Atmospheric Background Engine
       ├─► Recharts 7-Day Visualizations
       └─► LocalStorage Persistence (Profile + History)
       │
       ▼ (HTTP / REST)
[ FastAPI Backend (Python) ]
       │
       ├──► Open-Meteo Weather API (Temp, Humidity, Wind, UV, Rain)
       ├──► Open-Meteo Air Quality API (AQI, PM2.5, PM10, CO, NO2, O3)
       ├──► Open-Meteo & OpenStreetMap Geocoding (Reverse & Search)
       ├──► OpenWeather API (Optional Custom Key support)
       │
       ├──► 0-100 Personal Risk Scoring Engine
       │
       └──► AI Advisory Synthesis
               ├──► Primary: Google Gemini / Groq Cloud LLM
               └──► Fallback: Clinical Heuristic Advisory Engine (100% Offline/Free)
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide React, Recharts, Canvas Confetti |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, HTTPX (Async HTTP), Pydantic v2, Python-dotenv |
| **Telemetry APIs** | Open-Meteo Forecast API, Open-Meteo Air Quality API, Geocoding API, OpenStreetMap |
| **AI Engines** | Google Gemini 1.5/2.0 Flash, Groq Cloud (LLaMA 3.3 70B), Rule-Based Fallback Engine |

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** (Tested on Python 3.13)
- **Node.js 18+** & **npm**

---

### Quick Start (Windows)

Simply double-click `start_all.bat` or run:
```bash
start_all.bat
```
This automatically launches the FastAPI backend on port 8000 and the Vite frontend on port 5173.

---

### Manual Setup

#### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# (Optional) Create a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Copy .env.example to .env and configure keys
copy .env.example .env

# Run FastAPI backend server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend runs at `http://localhost:8000` (Interactive Swagger Docs at `http://localhost:8000/docs`).*

#### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install node dependencies
npm install

# Start Vite development server
npm run dev
```
*Frontend runs at `http://localhost:5173`.*

---

## 🔑 Environment Variables

Create a `.env` file in the `backend/` directory (see `backend/.env.example`):

```ini
PORT=8000
HOST=0.0.0.0

# Optional: Google Gemini API Key (https://aistudio.google.com/)
GEMINI_API_KEY=

# Optional: Groq Cloud API Key (https://console.groq.com/)
GROQ_API_KEY=

# Optional: OpenWeather API Key (https://openweathermap.org/api)
OPENWEATHER_API_KEY=
```

> **Note:** AeroHealth AI works **completely out of the box with ZERO API keys** required. The system automatically utilizes real-time Open-Meteo telemetry and the clinical rule-based advisory engine if no keys are provided.

---

## 📸 Screenshots & Showcase

| View | Description |
|---|---|
| **Dashboard** | 3-Card layout (Weather, AQI Gauge, Personal Risk Score) + AI Health Advisory + 7-Day Charts |
| **Demo Mode** | Instant 1-click comparison between Healthy Adult, Asthma, Outdoor Worker, and Elderly Person |
| **Dynamic Themes** | Reactive backgrounds shifting between Sunlit Azure, Starlit Night, Rain, Thunderstorm, and Smog Alert |
| **Health Profile** | Dedicated physiological trait configurator with real-time risk factor impact |
| **Alert History** | Archive of past advisories saved locally with timestamps and telemetry |

---

## 🔮 Future Improvements

- [ ] Push notification alerts for sudden AQI or thermal spikes.
- [ ] Wearable integration (Apple HealthKit, Google Fit) for live heart-rate variability.
- [ ] Multi-lingual advisory voice readout for accessibility.
- [ ] Hyperlocal street-level micro-sensor mesh integration.

---

## ⚖️ Medical Disclaimer

*AeroHealth AI is designed for educational and informational purposes only. It does not provide medical diagnoses or replace professional healthcare consultations. Individuals with chronic medical conditions should always follow their physician's prescribed care plan.*

---

**Developed with ❤️ for the Hackathon.**
