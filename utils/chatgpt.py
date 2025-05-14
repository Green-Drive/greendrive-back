import openai
import os
from dotenv import load_dotenv
from typing import List, Dict, Tuple
from models import TripAnalysis
from datetime import datetime, timedelta

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def calculate_variations(data: List[Dict], key: str) -> List[Tuple[datetime, float]]:
    """Calculate variations of a metric over time"""
    variations = []
    for i in range(1, len(data)):
        if key in data[i] and key in data[i-1]:
            value = data[i][key] - data[i-1][key]
            timestamp = data[i]['timestamp']
            variations.append((timestamp, value))
    return variations

def find_peaks(variations: List[Tuple[datetime, float]], threshold: float) -> List[Tuple[datetime, float]]:
    """Find variation peaks above threshold"""
    return [(ts, val) for ts, val in variations if abs(val) > threshold]

def format_trip_data_for_analysis(trip_data: List[Dict]) -> str:
    """Format trip data for ChatGPT analysis"""
    if not trip_data:
        return "No data available for this trip."
    
    speeds = [d.get('speed', 0) for d in trip_data]
    rpms = [d.get('rpm', 0) for d in trip_data]
    temps = [d.get('engine_temp', 0) for d in trip_data]
    consumptions = [d.get('fuel_consumption', 0) for d in trip_data]
    
    avg_speed = sum(speeds) / len(speeds)
    max_rpm = max(rpms)
    avg_temp = sum(temps) / len(temps)
    avg_consumption = sum(consumptions) / len(consumptions)
    
    # Analyze variations
    rpm_variations = calculate_variations(trip_data, 'rpm')
    consumption_variations = calculate_variations(trip_data, 'fuel_consumption')
    temp_variations = calculate_variations(trip_data, 'engine_temp')
    
    # Find significant peaks
    rpm_peaks = find_peaks(rpm_variations, 1000)  # Threshold of 1000 RPM
    consumption_peaks = find_peaks(consumption_variations, 2)  # Threshold of 2 L/100km
    temp_peaks = find_peaks(temp_variations, 5)  # Threshold of 5°C
    
    # Format critical moments
    critical_moments = []
    
    for ts, val in rpm_peaks:
        if val > 0:
            critical_moments.append(f"- Acceleration peak at {ts}: +{val:.0f} RPM")
        else:
            critical_moments.append(f"- Deceleration peak at {ts}: {val:.0f} RPM")
    
    for ts, val in consumption_peaks:
        if val > 0:
            critical_moments.append(f"- Consumption peak at {ts}: +{val:.1f} L/100km")
        else:
            critical_moments.append(f"- Consumption drop at {ts}: {val:.1f} L/100km")
    
    for ts, val in temp_peaks:
        if val > 0:
            critical_moments.append(f"- Rapid temperature rise at {ts}: +{val:.1f}°C")
        else:
            critical_moments.append(f"- Rapid temperature drop at {ts}: {val:.1f}°C")
    
    return f"""
Trip data {trip_data[0]['trip_id']}:
- Average speed: {avg_speed:.1f} km/h
- Maximum RPM: {max_rpm}
- Average engine temperature: {avg_temp:.1f}°C
- Average consumption: {avg_consumption:.1f} L/100km

Critical moments of the trip:
{chr(10).join(critical_moments) if critical_moments else "- No critical moments detected"}
"""

def analyze_trip_with_chatgpt(trip_data: List[Dict]) -> TripAnalysis:
    """Analyze trip data with ChatGPT"""
    formatted_data = format_trip_data_for_analysis(trip_data)
    
    print("\n=== Debug: Formatted Data ===")
    print(formatted_data)
    
    prompt = f"""
You are an expert in automotive telemetry data analysis.
Analyze the following data and provide a concise summary in English,
along with improvement suggestions based on the data.

{formatted_data}

Expected response format:
1. A concise summary of key points, focusing on critical moments of the trip
2. Specific improvement suggestions for each critical moment identified, mentioning the exact timestamp of the issue
3. General advice for optimizing driving

For each suggestion, start with the timestamp of the problem, followed by the suggestion.
Example format:
"At 14:23:45: Avoid sudden acceleration (+1500 RPM detected)"
"At 14:24:10: Maintain more constant speed (consumption peak of +3.2 L/100km)"

IMPORTANT: Always provide at least 3 suggestions based on the data, even if they are general recommendations.
"""
    
    try:
        print("\n=== Debug: Sending request to ChatGPT ===")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in automotive telemetry data analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        # Extract response content
        content = response.choices[0].message.content
        print("\n=== Debug: ChatGPT Response ===")
        print(content)
        
        # Split content into lines and clean empty lines
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        
        # Parse ChatGPT response into sections
        summary = "No summary available"
        suggestions = []
        general_advice = []
        current_section = None
        
        for line in lines:
            if line.lower().startswith("1. summary"):
                current_section = "summary"
                continue
            elif line.lower().startswith("2. improvement suggestions"):
                current_section = "suggestions"
                continue
            elif line.lower().startswith("3. general advice"):
                current_section = "general_advice"
                continue
            elif line.strip().startswith("Overall"):
                # Sometimes ChatGPT adds a final overall comment
                current_section = None
                continue
            if not line.strip():
                continue
            if current_section == "summary":
                if summary == "No summary available":
                    summary = line
                else:
                    summary += " " + line
            elif current_section == "suggestions":
                if line.strip().startswith("-") or line.strip().startswith("At") or ":" in line:
                    suggestions.append(line.lstrip("- "))
            elif current_section == "general_advice":
                if line.strip().startswith("-"):
                    general_advice.append(line.lstrip("- "))

        # If no suggestions found, add some default ones
        if not suggestions:
            suggestions = [
                "General: Consider maintaining more consistent speeds to improve fuel efficiency",
                "General: Monitor engine temperature during high-speed driving",
                "General: Try to avoid sudden acceleration and deceleration"
            ]

        # Optionally, add general advice to suggestions if you want to always show at least 3
        while len(suggestions) < 3 and general_advice:
            suggestions.append(general_advice.pop(0))

        print("\n=== Debug: Extracted Analysis ===")
        print(f"Summary: {summary}")
        print("Suggestions:")
        for suggestion in suggestions:
            print(f"- {suggestion}")

        return TripAnalysis(
            trip_id=trip_data[0]['trip_id'],
            summary=summary,
            suggestions=suggestions
        )
        
    except Exception as e:
        print(f"\n=== Debug: Error during ChatGPT API call ===")
        print(f"Error: {e}")
        # Return default analysis in case of error
        return TripAnalysis(
            trip_id=trip_data[0]['trip_id'],
            summary="Error during analysis. Please try again later.",
            suggestions=[
                "Check ChatGPT API connection",
                "Verify your API key is valid",
                "Ensure the server has internet access"
            ]
        )