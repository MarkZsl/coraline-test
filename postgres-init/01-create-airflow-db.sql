-- Runs automatically on first container startup (postgres image convention:
-- anything in /docker-entrypoint-initdb.d executes once, only when the data
-- volume is empty).
--
-- The "challenge" database (created via POSTGRES_DB env var) holds the
-- actual pipeline data (food_sales, cat_reg). Airflow needs its own
-- database to store DAG runs, task history, connections, etc. — keeping it
-- separate avoids mixing Airflow's internal tables with the challenge data.
CREATE DATABASE airflow_meta;
