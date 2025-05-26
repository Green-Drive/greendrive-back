import statistics


def detect_peaks(data, key: str, threshold: float):
    peaks, prev = [], data[0].get(key)
    for pt in data[1:]:
        cur = pt.get(key)
        if prev is not None and cur is not None:
            delta = cur - prev
            if abs(delta) > threshold:
                peaks.append({"timestamp": pt["timestamp"].strftime("%H:%M:%S"),
                              "metric": key, "change": delta})
        prev = cur
    return peaks


def compute_trip_stats(trip_data):
    if not trip_data:
        return {}
    return {
        "trip_id": trip_data[0]["trip_id"],
        "avg_speed": round(statistics.mean(pt.get("speed", 0) for pt in trip_data), 1),
        "max_rpm": max(pt.get("rpm", 0) for pt in trip_data),
        "avg_temp": round(statistics.mean(pt.get("engine_temp", 0) for pt in trip_data), 1),
        "avg_consumption": round(statistics.mean(pt.get("fuel_consumption", 0) for pt in trip_data), 1),
        "critical_events": _gather_critical(trip_data)
    }


def _gather_critical(trip_data):
    metrics = [
        ("rpm", 1000, "RPM"),
        ("fuel_consumption", 2.0, "L/100km"),
        ("engine_temp", 5.0, "°C"),
    ]
    events = []
    for key, thr, unit in metrics:
        for evt in detect_peaks(trip_data, key, thr):
            evt.update({"unit": unit})
            events.append(evt)
    return events
