import json

SCHEMA = """
You are an expert in automotive telemetry analysis.

Return **only** JSON matching this schema:
{
  "summary": string,
  "suggestions": [
    {
      "timestamp": "HH:MM:SS",
      "metric": string,
      "change": number,
      "unit": string,
      "advice": string
    }
  ],
  "general_advice": [ string ]
}
"""

EXAMPLE = """
### Example Input
{
  "trip_id": "T1",
  "avg_speed": 72.3,
  "max_rpm": 4500,
  "avg_temp": 85.2,
  "avg_consumption": 6.8,
  "critical_events": [
    { "timestamp": "14:15:00", "metric": "rpm", "change": 1500, "unit": "RPM" }
  ]
}

### Example Output
{
  "summary": "...",
  "suggestions": [...],
  "general_advice": [...]
}
"""

def build_prompt(stats: dict) -> str:
    stats_json = json.dumps(stats, default=str, indent=2)
    return f"""{SCHEMA}
Here is the trip data:
```json
{stats_json}
{EXAMPLE}
"""