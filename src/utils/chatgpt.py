import os
import json
import statistics
from datetime import datetime
from typing import Any, Dict, List, Tuple

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionFunctionCallOptionParam,
)
from openai.types.chat.completion_create_params import Function

from schemas.models import TripAnalysis


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def _detect_peaks(
        data: List[Dict[str, Any]],
        key: str,
        threshold: float,
) -> List[Tuple[datetime, float]]:
    """
    One‐pass detection of (timestamp, delta) where |delta| > threshold.
    """
    peaks: List[Tuple[datetime, float]] = []
    prev = data[0].get(key)
    for pt in data[1:]:
        cur = pt.get(key)
        if prev is not None and cur is not None:
            delta = cur - prev
            if abs(delta) > threshold:
                peaks.append((pt["timestamp"], delta))
        prev = cur
    return peaks


def format_trip_data_for_analysis(trip_data: List[Dict[str, Any]]) -> str:
    """
    Return the same markdown summary your original code produced.
    """
    if not trip_data:
        return "No data available for this trip."

    mean = statistics.mean
    avg_speed = mean(p.get("speed", 0) for p in trip_data)
    max_rpm = max(p.get("rpm", 0) for p in trip_data)
    avg_temp = mean(p.get("engine_temp", 0) for p in trip_data)
    avg_cons = mean(p.get("fuel_consumption", 0) for p in trip_data)

    rpm_peaks = _detect_peaks(trip_data, "rpm", 1000.0)
    cons_peaks = _detect_peaks(trip_data, "fuel_consumption", 2.0)
    temp_peaks = _detect_peaks(trip_data, "engine_temp", 5.0)

    critical: List[str] = []
    for ts, d in rpm_peaks:
        label = "Acceleration" if d > 0 else "Deceleration"
        critical.append(f"- {label} peak at {ts}: {d:+.0f} RPM")
    for ts, d in cons_peaks:
        label = "Consumption peak" if d > 0 else "Consumption drop"
        critical.append(f"- {label} at {ts}: {d:+.1f} L/100 km")
    for ts, d in temp_peaks:
        label = "Rapid temperature rise" if d > 0 else "Rapid temperature drop"
        critical.append(f"- {label} at {ts}: {d:+.1f} °C")

    return f"""
Trip data {trip_data[0]['trip_id']}:
- Average speed: {avg_speed:.1f} km/h
- Maximum RPM: {max_rpm}
- Average engine temperature: {avg_temp:.1f} °C
- Average consumption: {avg_cons:.1f} L/100 km

Critical moments of the trip:
{chr(10).join(critical) if critical else "- No critical moments detected"}
"""


def analyze_trip_with_chatgpt(
        trip_data: List[Dict[str, Any]],
        *,
        model: str = "o4-mini-2025-04-16",
        debug: bool = False,
) -> TripAnalysis:
    """
    Send the formatted trip block to OpenAI, use function-calling
    to get back strict JSON, and return a TripAnalysis.
    """
    formatted = format_trip_data_for_analysis(trip_data)
    if debug:
        print("DEBUG – formatted block\n", formatted)

    # 1. Build typed messages
    messages: List[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(
            role="system",
            content="You are an expert in automotive telemetry data analysis. "
                    "Analyze the trip, provide a summary, suggestions, general advice, "
                    "and calculate an ecological score (eco_score) between 0 and 100, "
                    "where 100 is highly ecological and 0 is not ecological at all. "
                    "Also, estimate the fuel saved in liters (fuel_saved_liters) and CO2 emissions avoided in kilograms (co2_avoided_kg) "
                    "compared to a less ecological driving style for the same trip. If the driving was not ecological, these values can be 0 or negative.",
        ),
        ChatCompletionUserMessageParam(
            role="user",
            content=(
                    "Analyze the following telemetry summary and respond ONLY via the "
                    "function call.\n\n" + formatted
            ),
        ),
    ]

    # 2. Define strict JSON schema
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "suggestions": {
                "type": "array",
                "minItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "timestamp": {"type": "string"},
                        "advice": {"type": "string"},
                    },
                    "required": ["timestamp", "advice"],
                },
            },
            "general_advice": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string"},
            },
            "eco_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Ecological score of the trip, from 0 (not ecological) to 100 (highly ecological)."
            },
            "fuel_saved_liters": {
                "type": "number",
                "description": "Estimated fuel saved in liters compared to a less ecological driving style for this trip. Can be 0 or negative if driving was not ecological."
            },
            "co2_avoided_kg": {
                "type": "number",
                "description": "Estimated CO2 emissions avoided in kilograms compared to a less ecological driving style for this trip. Can be 0 or negative if driving was not ecological."
            }
        },
        "required": ["summary", "suggestions", "general_advice", "eco_score", "fuel_saved_liters", "co2_avoided_kg"],
        "strict": True,
    }

    # 3. Prepare function-calling params
    functions: List[Function] = [
        Function(
            name="report_trip_analysis",
            description="Return summary, suggestions, general advice, eco_score, fuel_saved_liters, and co2_avoided_kg",
            parameters=schema,
        )
    ]
    function_call_option: ChatCompletionFunctionCallOptionParam = {
        "name": "report_trip_analysis"
    }

    # 4. Call OpenAI
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        functions=functions,
        function_call=function_call_option,
    )

    msg = response.choices[0].message

    if not msg.function_call:
        error_content = msg.content if msg.content else "No content provided by API."
        raise RuntimeError(
            f"Expected a function call from OpenAI, but none was received. "
            f"Message role: '{msg.role}'. API content: '{error_content}'"
        )

    if msg.function_call.name != "report_trip_analysis":
        raise RuntimeError(
            f"Expected function call to 'report_trip_analysis', but received '{msg.function_call.name}'."
        )

    try:
        # Arguments are in msg.function_call.arguments as a JSON string
        function_arguments_json = msg.function_call.arguments
        result = json.loads(function_arguments_json)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Failed to parse function call arguments as JSON: {e}. "
            f"Raw arguments: '{msg.function_call.arguments}'"
        )

    if debug:
        print("DEBUG – GPT function call arguments (raw string):\n", msg.function_call.arguments)
        print("DEBUG – GPT output (parsed arguments JSON):\n", json.dumps(result, indent=2))

    # 5. Build TripAnalysis
    suggestions = [f"At {s['timestamp']}: {s['advice']}" for s in result["suggestions"]]
    return TripAnalysis(
        trip_id=trip_data[0]["trip_id"],
        summary=result["summary"],
        suggestions=suggestions,
        general_advice=result.get("general_advice"),
        eco_score=result["eco_score"],
        fuel_saved_liters=result.get("fuel_saved_liters"),
        co2_avoided_kg=result.get("co2_avoided_kg"),
        plain_text=json.dumps(result, ensure_ascii=False), # Storing the parsed result
    )
