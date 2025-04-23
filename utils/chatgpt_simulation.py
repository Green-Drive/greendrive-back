from typing import List
from models import TripAnalysis

def analyze_trip_data(trip_data: List[dict]) -> TripAnalysis:
    # Simulation d'une analyse basée sur les données
    avg_speed = sum(d.get('speed', 0) for d in trip_data) / len(trip_data)
    max_rpm = max(d.get('rpm', 0) for d in trip_data)
    avg_temp = sum(d.get('engine_temp', 0) for d in trip_data) / len(trip_data)
    
    summary = f"Le véhicule a maintenu une vitesse moyenne de {avg_speed:.1f} km/h. "
    if max_rpm > 5000:
        summary += "Des pics de régime moteur élevés ont été détectés. "
    if avg_temp > 90:
        summary += "La température moteur a été élevée pendant le trajet. "
    
    suggestions = []
    if avg_speed < 30:
        suggestions.append("Considérer des trajets plus longs pour une meilleure efficacité")
    if max_rpm > 5000:
        suggestions.append("Éviter les accélérations brusques pour réduire la consommation")
    
    return TripAnalysis(
        trip_id=trip_data[0]['trip_id'],
        summary=summary,
        suggestions=suggestions
    ) 