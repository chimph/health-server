# Health Server

A self-hosted health data ingestion server that collects minute-level Apple Health metrics and stores them in a time-series database. Built for quantified-self tracking, dashboards, and AI analysis.

```
iPhone (Health Auto Export)
        |
   POST /metrics
        |
  FastAPI webhook
        |
    TimescaleDB
```

## Stack

- **API:** FastAPI (Python)
- **Database:** TimescaleDB (PostgreSQL time-series extension)
- **Containerization:** Docker & Docker Compose

## Requirements

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Health Auto Export](https://www.healthyapps.dev) iOS app (Premium or free trial for Automations)
- Network path from your iPhone to the server (e.g. same LAN or [Tailscale](https://tailscale.com))

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/chimph/health-server.git
cd health-server
cp .env.example .env
```

Edit `.env` and set a secure database password:

```
POSTGRES_USER=health
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=healthdata
```

### 2. Start the server

```bash
docker compose up -d
```

### 3. Verify it's running

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

### 4. Connect to the database

```bash
docker exec -it health-db psql -U health healthdata
```

## Setting Up Health Auto Export

[Health Auto Export](https://www.healthyapps.dev) is an iOS app that sends Apple Health data to a REST API on a schedule. A Premium subscription (or free trial) is required for the Automations feature.

### Step 1 — Install and grant permissions

Install **Health Auto Export** from the App Store. On first launch, grant it access to the Apple Health metrics you want to track (steps, heart rate, sleep, etc.).

### Step 2 — Create an automation

1. Open the app and go to **Automations**.
2. Tap **Add Automation**.
3. Select **REST API** as the automation type.

### Step 3 — Configure the endpoint

Enter your server URL as the API endpoint:

```
http://<your-server-ip>:8000/metrics
```

If you're using Tailscale or another private network, use that IP (e.g. `http://100.x.x.x:8000/metrics`). The server must be reachable from your iPhone.

### Step 4 — Choose metrics and schedule

- **Health Metrics:** Select the metrics you want to export (or choose all).
- **Export Format:** JSON
- **Time Interval:** Set how often data is pushed (as low as every 5 minutes).
- **Batching:** Enable this to prevent memory issues on your iPhone when exporting large amounts of data.

### Step 5 — Enable background automations

To allow exports while the app is in the background, add the **Automations widget** to your iPhone Home Screen:

1. Long-press your Home Screen and tap **+**.
2. Search for **"Auto Export"**.
3. Swipe to the **Automations** widget and add it.

This keeps the automation running reliably without needing the app open.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/metrics` | Ingest Health Auto Export JSON payload |
| `GET` | `/health` | Health check |

## Database Schema

All metrics are stored in a single TimescaleDB hypertable:

```sql
metrics(
  time        TIMESTAMPTZ,
  source      TEXT,
  metric      TEXT,
  value       DOUBLE PRECISION,
  unit        TEXT,
  metadata    JSONB
)
```

## Example Queries

Replace `'Pacific/Auckland'` with your [IANA timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) in the queries below. The database stores all timestamps in UTC, so `AT TIME ZONE` converts to your local day boundary.

```sql
-- Total steps today
SELECT SUM(value) FROM metrics
WHERE metric = 'step_count'
  AND time >= (CURRENT_DATE AT TIME ZONE 'Pacific/Auckland');

-- Steps by hour
SELECT date_trunc('hour', time AT TIME ZONE 'Pacific/Auckland') AS hour,
       SUM(value)
FROM metrics
WHERE metric = 'step_count'
  AND time >= (CURRENT_DATE AT TIME ZONE 'Pacific/Auckland')
GROUP BY 1 ORDER BY 1;

-- List all tracked metrics
SELECT DISTINCT metric FROM metrics;
```
