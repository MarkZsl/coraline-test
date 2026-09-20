from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config import Settings
from src.logger import get_logger

logger = get_logger(__name__)


def get_engine(settings: Settings) -> Engine:
    return create_engine(settings.postgres.dsn, future=True)


CREATE_FOOD_SALES_TABLE = """
CREATE TABLE IF NOT EXISTS {table} (
    id           TEXT PRIMARY KEY,
    sale_date    DATE NOT NULL,
    region       TEXT NOT NULL,
    city         TEXT NOT NULL,
    category     TEXT NOT NULL,
    product      TEXT NOT NULL,
    qty          INTEGER NOT NULL,
    unit_price   NUMERIC(10, 2) NOT NULL,
    total_price  NUMERIC(12, 2) NOT NULL,
    loaded_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_{table}_category ON {table} (category);
CREATE INDEX IF NOT EXISTS idx_{table}_region ON {table} (region);
CREATE INDEX IF NOT EXISTS idx_{table}_sale_date ON {table} (sale_date);
"""


def ensure_food_sales_table(engine: Engine, table: str) -> None:
    with engine.begin() as conn:
        conn.execute(text(CREATE_FOOD_SALES_TABLE.format(table=table)))
        for stmt in CREATE_INDEXES.format(table=table).strip().split(";"):
            if stmt.strip():
                conn.execute(text(stmt))
    logger.info("Ensured table '%s' exists", table)
