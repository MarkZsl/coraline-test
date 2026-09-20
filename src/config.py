from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"

load_dotenv(PROJECT_ROOT / ".env")  # no-op if the file doesn't exist


def _env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)


@dataclass(frozen=True)
class PostgresSettings:
    host: str
    port: int
    database: str
    user: str
    password: str
    db_schema: str = "public"

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


@dataclass(frozen=True)
class ExcelSettings:
    file_path: str
    sheet_name: str


@dataclass(frozen=True)
class EtlSettings:
    raw_table: str
    load_strategy: str
    chunk_size: int


@dataclass(frozen=True)
class CatRegSettings:
    sql_file: str
    table: str


@dataclass(frozen=True)
class Settings:
    excel: ExcelSettings
    postgres: PostgresSettings
    etl: EtlSettings
    cat_reg: CatRegSettings
    log_level: str


def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=1)
def get_settings(config_path: str | Path = DEFAULT_CONFIG_PATH) -> Settings:
    raw = _load_yaml(Path(config_path))

    excel = ExcelSettings(
        file_path=_env("EXCEL_FILE_PATH", raw["excel"]["file_path"]),
        sheet_name=_env("EXCEL_SHEET_NAME", raw["excel"]["sheet_name"]),
    )

    postgres = PostgresSettings(
        host=_env("POSTGRES_HOST", raw["postgres"]["host"]),
        port=int(_env("POSTGRES_PORT", str(raw["postgres"]["port"]))),
        database=_env("POSTGRES_DB", raw["postgres"]["database"]),
        user=_env("POSTGRES_USER", "root"),
        password=_env("POSTGRES_PASSWORD", ""),
        db_schema=_env("POSTGRES_SCHEMA", raw["postgres"]["schema"]),
    )

    etl = EtlSettings(
        raw_table=_env("ETL_RAW_TABLE", raw["etl"]["raw_table"]),
        load_strategy=_env("ETL_LOAD_STRATEGY", raw["etl"]["load_strategy"]),
        chunk_size=int(_env("ETL_CHUNK_SIZE", str(raw["etl"]["chunk_size"]))),
    )

    cat_reg = CatRegSettings(
        sql_file=_env("CAT_REG_SQL_FILE", raw["cat_reg"]["sql_file"]),
        table=_env("CAT_REG_TABLE", raw["cat_reg"]["table"]),
    )

    return Settings(
        excel=excel,
        postgres=postgres,
        etl=etl,
        cat_reg=cat_reg,
        log_level=_env("LOG_LEVEL", raw["logging"]["level"]),
    )
