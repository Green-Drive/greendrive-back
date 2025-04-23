from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import TelemetryData, TripAnalysis
from db import get_db
from utils.chatgpt import analyze_trip_with_chatgpt

router = APIRouter()

@router.get("/analyze/{trip_id}", response_model=TripAnalysis)
async def analyze_trip(
    trip_id: str,
    db: Session = Depends(get_db)
):
    # Récupérer toutes les données du trajet
    trip_data = db.query(TelemetryData).filter(
        TelemetryData.trip_id == trip_id
    ).order_by(TelemetryData.timestamp).all()
    
    if not trip_data:
        raise HTTPException(status_code=404, detail="Trajet non trouvé")
    
    # Convertir les données en format dict pour l'analyse
    trip_data_dict = [
        {
            "trip_id": item.trip_id,
            "speed": item.speed,
            "rpm": item.rpm,
            "engine_temp": item.engine_temp,
            "fuel_consumption": item.fuel_consumption,
            "timestamp": item.timestamp
        }
        for item in trip_data
    ]
    
    # Analyser les données avec ChatGPT
    return analyze_trip_with_chatgpt(trip_data_dict) 