from __future__ import annotations

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.logger import get_logger

logger = get_logger(__name__)


def load_food_sales(df: pd.DataFrame, engine: Engine, table: str, strategy: str = "replace", chunk_size: int = 1000) -> int:
    if df.empty:
        logger.warning("Nothing to load: extracted DataFrame is empty")
        return 0

    if strategy == "replace":
        return _load_replace(df, engine, table, chunk_size)
    elif strategy == "append":
        return _load_upsert(df, engine, table, chunk_size)
    else:
        raise ValueError(f"Unknown load strategy '{strategy}'. Use 'replace' or 'append'.")


def _load_replace(df: pd.DataFrame, engine: Engine, table: str, chunk_size: int) -> int:
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table}"))
        df.to_sql(table, con=conn, if_exists="append", index=False, chunksize=chunk_size, method="multi")
    logger.info("Loaded %d rows into '%s' (strategy=replace)", len(df), table)
    return len(df)


def _load_upsert(df: pd.DataFrame, engine: Engine, table: str, chunk_size: int) -> int:
    cols = list(df.columns)
    update_cols = [c for c in cols if c != "id"]
    insert_cols_sql = ", ".join(cols)
    values_sql = ", ".join(f":{c}" for c in cols)
    update_sql = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    stmt = text(
        f"""
        INSERT INTO {table} ({insert_cols_sql})
        VALUES ({values_sql})
        ON CONFLICT (id) DO UPDATE SET {update_sql}
        """
    )

    records = df.to_dict(orient="records")
    total = 0
    with engine.begin() as conn:
        for i in range(0, len(records), chunk_size):
            chunk = records[i : i + chunk_size]
            conn.execute(stmt, chunk)
            total += len(chunk)

    logger.info("Upserted %d rows into '%s' (strategy=append)", total, table)
    return total
