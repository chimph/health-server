from fastapi import FastAPI, Request
import psycopg2
from psycopg2.extras import execute_values, Json
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

conn = psycopg2.connect(DATABASE_URL)

def parse_date(d):
    return datetime.strptime(d, "%Y-%m-%d %H:%M:%S %z")

@app.post("/metrics")
async def ingest(request: Request):
    payload = await request.json()

    rows = []

    metrics = payload.get("data", {}).get("metrics", [])

    for metric in metrics:
        name = metric.get("name")
        unit = metric.get("units")

        for entry in metric.get("data", []):
            time = parse_date(entry["date"])
            value = entry.get("qty", 0)
            source = entry.get("source", "unknown")

            rows.append((time, source, name, value, unit, None))

    workout_rows = []
    for workout in payload.get("data", {}).get("workouts", []):
        energy = workout.get("activeEnergyBurned", {})
        dist = workout.get("distance", {})
        workout_rows.append((
            workout.get("id"),
            workout.get("name"),
            parse_date(workout["start"]),
            parse_date(workout["end"]) if workout.get("end") else None,
            workout.get("duration"),
            energy.get("qty") if isinstance(energy, dict) else energy,
            dist.get("qty") if isinstance(dist, dict) else dist,
            Json(workout),
        ))

    with conn.cursor() as cur:
        if rows:
            execute_values(cur, """
                INSERT INTO metrics
                (time, source, metric, value, unit, metadata)
                VALUES %s
                ON CONFLICT (time, source, metric) DO NOTHING
            """, rows)

        if workout_rows:
            execute_values(cur, """
                INSERT INTO workouts
                (id, name, start, "end", duration, active_energy_burned, distance, detail)
                VALUES %s
                ON CONFLICT (id, start) DO NOTHING
            """, workout_rows)

    conn.commit()

    return {"inserted_metrics": len(rows), "inserted_workouts": len(workout_rows)}

@app.get("/health")
def health():
    return {"status": "ok"}
