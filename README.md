# OBD Telemetry Analysis Backend

A FastAPI-based backend service for real-time telemetry data analysis from OBD-connected vehicles. This service processes vehicle data, stores it in a TimescaleDB database, and provides AI-powered analysis using ChatGPT.

## Features

- Real-time telemetry data ingestion
- TimescaleDB for efficient time-series data storage
- AI-powered trip analysis using ChatGPT
- Detailed vehicle performance metrics
- Timestamp-based issue detection and suggestions

## Tech Stack

- Python 3.8+
- FastAPI
- TimescaleDB (PostgreSQL extension)
- OpenAI GPT-3.5 Turbo
- Docker & Docker Compose

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Python 3.8 or higher

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Create a `.env` file with the following variables:
```env
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=telemetry_db
OPENAI_API_KEY=your_openai_api_key
```

3. Start the services using Docker Compose:
```bash
docker-compose up -d
```

4. Initialize the database:
```bash
python init_db.py
```

## API Endpoints

### POST /api/v1/ingest
Ingests telemetry data from the vehicle.

Request body example:
```json
[
  {
    "vehicle_id": "vehicle_1",
    "trip_id": "trip_123",
    "timestamp": "2024-03-20T14:30:00",
    "rpm": 2500,
    "speed": 60.5,
    "fuel_consumption": 7.2,
    "engine_temp": 85.5,
    "latitude": 48.8566,
    "longitude": 2.3522
  }
]
```

### GET /api/v1/analyze/{trip_id}
Retrieves AI-powered analysis for a specific trip.

Response example:
```json
{
  "trip_id": "trip_123",
  "summary": "Trip analysis summary...",
  "suggestions": [
    "At 14:23:45: Avoid sudden acceleration (+1500 RPM detected)",
    "At 14:24:10: Maintain more constant speed (consumption peak of +3.2 L/100km)"
  ]
}
```

## Data Analysis Features

The system analyzes:
- Speed variations
- RPM patterns
- Fuel consumption
- Engine temperature
- Driving patterns

Each analysis includes:
- Timestamp-based issue detection
- Specific improvement suggestions
- General driving optimization advice

## Testing

Run the test suite:
```bash
python test_api.py
```

The test suite will:
1. Generate realistic telemetry data
2. Test the ingestion API
3. Test the analysis API
4. Display the results

## Project Structure

```
backend/
├── docker-compose.yml
├── requirements.txt
├── init_db.py
├── test_api.py
├── models.py
├── db.py
└── routes/
    ├── ingest.py
    └── analyze.py
└── utils/
    └── chatgpt.py
```

## Acknowledgments

- FastAPI for the web framework
- TimescaleDB for time-series data storage
- OpenAI for the GPT-3.5 Turbo model 