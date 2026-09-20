from __future__ import annotations

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.logger import get_logger

logger = get_logger(__name__)


def run_sql_file(engine: Engine, sql_path: str | Path) -> None:
    sql_path = Path(sql_path)
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    sql_text = sql_path.read_text(encoding="utf-8")
    logger.info("Executing SQL file '%s'", sql_path)
    with engine.begin() as conn:
        for statement in sql_text.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
    logger.info("Finished executing '%s'", sql_path)
