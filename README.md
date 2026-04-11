#  GeoVision AI
Smart Location Intelligence Platform using AI & Geospatial Analytics

---

##  Overview
GeoVision AI is an AI-powered geospatial platform that helps users identify the best locations for businesses. It combines maps, machine learning, and AI reasoning to provide data-driven insights.

---

##  Problem Statement
Choosing the right business location is difficult due to:
- Lack of data-driven insights
- Manual and time-consuming analysis
- High risk of poor investment decisions

---

##  Solution
GeoVision AI provides:
- Location-based analysis
- AI-powered scoring
- Business-specific recommendations
- Explainable insights

---

##  Features (Detailed)

###  Site Readiness Score
- Calculates score (0–100)
- Based on:
  - Population density
  - Competition density
  - Accessibility
- Uses weighted formula (Personalized Scoring Engine)

---

### Recommendation Engine
- Suggests top 3–5 best locations
- Based on score ranking and business type

---

###  Hotspot Detection
- Uses DBSCAN clustering
- Identifies high-potential zones

---

### AI Explanation Engine
- Explains why a location is good/bad
- Returns:
  - Explanation
  - Strengths
  - Weaknesses
  - Opportunities

---

### AI Business Advisor (Chatbot)
- Answers business-related questions
- Suggests locations and strategies

---

### Personalized Scoring Engine
- User sets priority:
  - Population
  - Competition
  - Accessibility
- Adjusts scoring dynamically

---

###  Competitor Impact Analyzer
- Shows how competitors affect score
- Simulates removal of competitors

---

### Location Comparison
- Compare multiple locations
- Shows score differences and factors

---

###  Report Generation
- Generates structured summary:
  - Score
  - Explanation
  - Recommendations

---

###  Business Type Selector
- Adapts scoring logic based on:
  - Restaurant
  - Warehouse
  - EV station

---

##  System Architecture

Frontend (React)  
↓  
Backend (FastAPI)  
↓  
AI Module + Database  
↓  
Response → Frontend  

---

## Workflow (End-to-End)

1. User selects:
   - Business type
   - Priority weights

2. User clicks location on map

3. Frontend sends request:
   POST /get-score

4. Backend:
   - Loads data (JSON)
   - Calls AI scoring
   - Calls explanation engine

5. Backend returns:
   - Score
   - Insights
   - Recommendations

6. Frontend updates UI dynamically

7. Additional features:
   - Chat → /chat
   - Compare → /compare
   - Report → /generate-report

---

##  API Endpoints

- POST /get-score
- POST /get-recommendations
- GET /get-hotspots
- POST /get-explanation
- POST /chat
- POST /competitor-impact
- POST /compare
- POST /generate-report

---

##  Tech Stack

### Frontend
- React.js
- Leaflet.js (Map)
- Tailwind CSS

### Backend
- Python
- FastAPI
- Uvicorn

### AI / ML
- scikit-learn (DBSCAN clustering)
- Claude / OpenAI API (LLM)

### Database
- JSON / GeoJSON (file-based)

---

## Data Sources
- OpenStreetMap (map tiles)
- Overpass API (POIs, competitors)
- Custom datasets (population)

---

## Project Structure

project/
├── frontend/
├── backend/
├── ai/
├── database/
├── guidelines/
└── README.md

---

##  Rules
- Do NOT change API names
- Do NOT change feature names
- Frontend must not access database
- Backend is main controller

---

##  Key Highlights
- AI-powered decision system
- Real-time geospatial analysis
- Explainable AI insights
- Lightweight architecture

---

##  Final Statement
GeoVision AI transforms geospatial data into intelligent business decisions using AI-driven insights and recommendations.
 transforms geospatial data into intelligent business decisions using AI-driven insights and recommendations.
