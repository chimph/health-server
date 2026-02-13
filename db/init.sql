CREATE TABLE metrics (
  time TIMESTAMPTZ NOT NULL,
  source TEXT,
  metric TEXT,
  value DOUBLE PRECISION,
  unit TEXT,
  metadata JSONB,
  UNIQUE (time, source, metric)
);

SELECT create_hypertable('metrics', 'time', if_not_exists => TRUE);

CREATE TABLE workouts (
  id TEXT NOT NULL,
  name TEXT NOT NULL,
  start TIMESTAMPTZ NOT NULL,
  "end" TIMESTAMPTZ,
  duration DOUBLE PRECISION,
  active_energy_burned DOUBLE PRECISION,
  distance DOUBLE PRECISION,
  detail JSONB,
  PRIMARY KEY (id, start)
);

SELECT create_hypertable('workouts', 'start', if_not_exists => TRUE);
