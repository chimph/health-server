
A self-hosted health data ingestion platform designed to collect minute-level Apple Health data and make it available for AI analysis, dashboards, and long-term quantified-self tracking.

This system runs entirely in Docker and stores data in a time-series database optimized for analytics and AI.

---

## Architecture Overview

```
iPhone (Health Auto Export)
        ↓
Webhook API (FastAPI)
        ↓
TimescaleDB (Postgres time-series)
        ↓
AI Health Assistant
```

The API receives structured health data and normalizes it into a unified time-series schema.

---

## Stack

- FastAPI ingestion API
- TimescaleDB (PostgreSQL extension)
- Docker + Docker Compose
- Tailscale private networking
- WSL Linux host (Windows)

---

## Features

- Minute-level health metric ingestion
- Time-series optimized database
- Batch inserts for performance
- Duplicate-safe pipeline
- AI-ready schema
- Secure private network via Tailscale
- Portable Docker deployment

---

## Database Schema

Single unified hypertable:

```
metrics(
  time TIMESTAMPTZ,
  source TEXT,
  metric TEXT,
  value DOUBLE PRECISION,
  unit TEXT,
  metadata JSONB
)
```

Each row represents one measurement.

Example:

| time | metric | value |
|------|--------|-------|
| 07:01 | step_count | 23 |
| 07:02 | heart_rate | 78 |

This schema is flexible, scalable, and AI-friendly.

---

## API Endpoints

### Health check

GET /health

Returns:

```
{"status": "ok"}
```

### Metric ingestion

POST /metrics

Accepts Health Auto Export JSON payload and converts it into normalized rows.

Batch inserts for performance.

---

## Webhook Configuration

Webhook URL:

```
http://<tailscale-ip>:8000/metrics
```

Example:

```
http://100.112.205.123:8000/metrics
```

The iPhone must be connected to Tailscale.

---

## Running the Server

From project directory:

```
docker compose up -d
```

Check containers:

```
docker ps
```

Test API:

```
http://<ip>:8000/health
```

---

## Query Examples

### Total steps today

```sql
SELECT SUM(value)
FROM metrics
WHERE metric = 'step_count'
AND time >= CURRENT_DATE;
```

### Steps grouped by hour

```sql
SELECT date_trunc('hour', time), SUM(value)
FROM metrics
WHERE metric = 'step_count'
AND time >= CURRENT_DATE
GROUP BY 1
ORDER BY 1;
```

### List all metrics

```sql
SELECT DISTINCT metric FROM metrics;
```

---

## AI Integration Strategy

Raw metrics → Derived features → AI reasoning

Recommended approach:

- Create daily summary SQL views
- Feed summaries to AI watcher
- Run periodic analysis
- Generate coaching insights
- Detect anomalies

This keeps the AI fast, interpretable, and stable.

---

## Future Expansion

- Grafana dashboards
- AI anomaly detection
- Recovery scoring
- Sleep analysis
- Automated daily reports
- Encrypted backups
- Authentication layer
- Local LLM health assistant

---

## Philosophy

You own your health data.

This system is designed as a lifelong personal dataset that grows in value over time and enables deep self-understanding through analytics and AI.
