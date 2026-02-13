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
