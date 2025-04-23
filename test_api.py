import requests
import json
from datetime import datetime, timedelta
import random
import time
import math

BASE_URL = "http://localhost:8000/api/v1"

def generate_realistic_speed_profile(duration_minutes: int = 30) -> list:
    """Generate a realistic speed profile for a trip"""
    speeds = []
    current_speed = 0
    target_speed = 0
    time_points = duration_minutes * 60  # Convert to seconds
    
    for t in range(time_points):
        # Change target speed every 1-3 minutes to create more variations
        if t % (random.randint(60, 180)) == 0:
            # Realistic target speed based on road type
            if random.random() < 0.3:  # 30% chance of being in city
                target_speed = random.uniform(30, 50)
            elif random.random() < 0.6:  # 30% chance of being on road
                target_speed = random.uniform(70, 90)
            else:  # 40% chance of being on highway
                target_speed = random.uniform(100, 130)
        
        # More aggressive acceleration/deceleration
        if current_speed < target_speed:
            current_speed = min(current_speed + random.uniform(1.0, 2.5), target_speed)
        elif current_speed > target_speed:
            current_speed = max(current_speed - random.uniform(1.0, 2.5), target_speed)
        
        # Add more significant variations
        current_speed += random.uniform(-2, 2)
        current_speed = max(0, current_speed)  # Speed cannot be negative
        
        speeds.append(current_speed)
    
    return speeds

def calculate_rpm_from_speed(speed: float) -> int:
    """Calculate RPM based on speed"""
    # Base RPM for each speed
    base_rpm = int(speed * 30)  # About 30 RPM per km/h
    
    # Add more significant variations
    variation = random.randint(-500, 500)
    
    # Adjust based on driving type
    if speed < 30:  # City
        base_rpm += random.randint(0, 1000)  # Higher RPM in city
    elif speed > 100:  # Highway
        base_rpm -= random.randint(0, 500)  # Lower RPM on highway
    
    return max(800, min(6000, base_rpm + variation))

def calculate_fuel_consumption(speed: float, rpm: int) -> float:
    """Calculate fuel consumption based on speed and RPM"""
    # Base consumption
    base_consumption = 5.0  # L/100km
    
    # More significant adjustments based on speed
    if speed < 30:  # City
        base_consumption += random.uniform(3, 6)
    elif speed > 100:  # Highway
        base_consumption += random.uniform(2, 4)
    else:  # Road
        base_consumption += random.uniform(1, 3)
    
    # More significant adjustments based on RPM
    if rpm > 4000:
        base_consumption += (rpm - 4000) / 500  # More sensitive to high RPM
    
    return round(base_consumption + random.uniform(-1, 1), 1)

def calculate_engine_temp(speed: float, rpm: int, previous_temp: float) -> float:
    """Calculate engine temperature"""
    # Base temperature
    base_temp = 90.0
    
    # More significant speed influence
    speed_factor = speed / 50 if speed > 0 else 0
    
    # More significant RPM influence
    rpm_factor = rpm / 2000 if rpm > 0 else 0
    
    # Calculate new temperature with more variation
    new_temp = base_temp + (speed_factor * 10) + (rpm_factor * 5)
    
    # Smooth with previous temperature
    smoothed_temp = (previous_temp * 0.6) + (new_temp * 0.4)  # More responsive to changes
    
    # Add more significant variations
    smoothed_temp += random.uniform(-2, 2)
    
    return round(max(70, min(110, smoothed_temp)), 1)

def generate_telemetry_data(trip_id: str, vehicle_id: str, duration_minutes: int = 30) -> list:
    """Generate realistic telemetry data"""
    data = []
    current_time = datetime.now()
    speeds = generate_realistic_speed_profile(duration_minutes)
    engine_temp = 70.0  # Initial temperature
    
    for i, speed in enumerate(speeds):
        timestamp = current_time + timedelta(seconds=i)
        rpm = calculate_rpm_from_speed(speed)
        fuel_consumption = calculate_fuel_consumption(speed, rpm)
        engine_temp = calculate_engine_temp(speed, rpm, engine_temp)
        
        # Generate realistic GPS coordinates (simulating a trip)
        base_lat = 48.8566  # Paris
        base_lon = 2.3522
        lat = base_lat + (i * 0.00001 * random.uniform(-1, 1))
        lon = base_lon + (i * 0.00001 * random.uniform(-1, 1))
        
        data.append({
            "vehicle_id": vehicle_id,
            "trip_id": trip_id,
            "timestamp": timestamp.isoformat(),
            "rpm": rpm,
            "speed": round(speed, 1),
            "fuel_consumption": fuel_consumption,
            "engine_temp": engine_temp,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6)
        })
    
    return data

def test_ingest_api():
    """Test the ingestion API"""
    print("\n=== Testing Ingestion API ===")
    
    trip_id = f"test_trip_{int(time.time())}"
    vehicle_id = "test_vehicle_1"
    data = generate_telemetry_data(trip_id, vehicle_id, duration_minutes=15)  # 15-minute trip
    
    try:
        response = requests.post(
            f"{BASE_URL}/ingest",
            json=data
        )
        response.raise_for_status()
        print(f"✅ Ingestion test successful: {response.json()}")
        return trip_id
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during ingestion test: {e}")
        return None

def test_analyze_api(trip_id: str):
    """Test the analysis API"""
    print("\n=== Testing Analysis API ===")
    
    try:
        response = requests.get(f"{BASE_URL}/analyze/{trip_id}")
        response.raise_for_status()
        analysis = response.json()
        
        print("✅ Analysis test successful:")
        print(f"Trip ID: {analysis['trip_id']}")
        print(f"Summary: {analysis['summary']}")
        print("\nSuggestions:")
        if analysis['suggestions']:
            for suggestion in analysis['suggestions']:
                print(f"  - {suggestion}")
        else:
            print("  No suggestions generated. This might indicate:")
            print("  1. No significant variations in the data")
            print("  2. API connection issues")
            print("  3. Data format issues")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during analysis test: {e}")
        print("Please check if the API server is running and accessible.")

def main():
    print("=== Starting API Tests ===")
    
    # Wait for API to be ready
    print("Waiting for API to be ready...")
    time.sleep(5)
    
    # Test ingestion
    trip_id = test_ingest_api()
    
    if trip_id:
        # Test analysis
        test_analyze_api(trip_id)
    
    print("\n=== Tests Completed ===")

if __name__ == "__main__":
    main() 