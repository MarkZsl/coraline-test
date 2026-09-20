from __future__ import annotations

from src.config import Settings, get_settings
from src.db import ensure_food_sales_table, get_engine
from src.extract import extract_food_sales
from src.load import load_food_sales
from src.logger import get_logger
from src.sql_runner import run_sql_file

logger = get_logger(__name__)


def task_extract_and_load_food_sales(settings: Settings | None = None) -> int:
    settings = settings or get_settings()
    engine = get_engine(settings)

    ensure_food_sales_table(engine, settings.etl.raw_table)
    df = extract_food_sales(settings.excel.file_path, settings.excel.sheet_name)
    rows_loaded = load_food_sales(
        df,
        engine,
        table=settings.etl.raw_table,
        strategy=settings.etl.load_strategy,
        chunk_size=settings.etl.chunk_size,
    )
    logger.info("task_extract_and_load_food_sales complete: %d rows", rows_loaded)
    return rows_loaded


def task_build_cat_reg(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    engine = get_engine(settings)
    run_sql_file(engine, settings.cat_reg.sql_file)
    logger.info("task_build_cat_reg complete")


def run_pipeline() -> None:
    settings = get_settings()
    task_extract_and_load_food_sales(settings)
    task_build_cat_reg(settings)
