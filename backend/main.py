from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import score, recommendation, hotspots, explanation, chatbot, competitor, compare, report

app = FastAPI(title="GeoVision AI Backend")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(score.router, tags=["Score"])
app.include_router(recommendation.router, tags=["Recommendation"])
app.include_router(hotspots.router, tags=["Hotspots"])
app.include_router(explanation.router, tags=["Explanation"])
app.include_router(chatbot.router, tags=["Chatbot"])
app.include_router(competitor.router, tags=["Competitor Impact"])
app.include_router(compare.router, tags=["Compare"])
app.include_router(report.router, tags=["Report"])

@app.get("/")
def read_root():
    return {"message": "GeoVision AI Backend is running."}
