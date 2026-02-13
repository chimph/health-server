from fastapi import FastAPI, Request
import psycopg2
from psycopg2.extras import execute_values
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

    if not rows:
        return {"inserted": 0}

    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO metrics
            (time, source, metric, value, unit, metadata)
            VALUES %s
            ON CONFLICT (time, source, metric) DO NOTHING
        """, rows)

    conn.commit()

    return {"inserted": len(rows)}

@app.get("/health")
def health():
    return {"status": "ok"}
