import os
import sys

from fastapi import FastAPI, HTTPException


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.predict import get_dashboard_overview, recommend


app = FastAPI(title="Instacart Recommender System", version="1.0.0")


@app.get("/")
def home():
    return {"message": "Welcome to the Instacart Recommender System API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/recommend/{user_id}")
def get_recommendations(user_id: int, top_n: int = 10):
    result = recommend(user_id=user_id, top_n=top_n)
    if result is None:
        raise HTTPException(status_code=404, detail="User ID not found. Please try another one.")

    return result.to_dict(orient="records")


@app.get("/insights/overview")
def insights_overview():
    overview = get_dashboard_overview()
    return {
        "summary": overview["summary"],
        "popular_products": overview["popular_products"].to_dict(orient="records"),
        "reliable_products": overview["reliable_products"].to_dict(orient="records"),
    }

