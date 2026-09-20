from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.etl import task_build_cat_reg, task_extract_and_load_food_sales

default_args = {
    "owner": "data-engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="food_sales_etl",
    description="Load FoodSales workbook into Postgres and build the cat_reg pivot table",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["coraline", "challenge", "etl"],
) as dag:

    extract_and_load_food_sales = PythonOperator(
        task_id="extract_and_load_food_sales",
        python_callable=task_extract_and_load_food_sales,
    )

    build_cat_reg = PythonOperator(
        task_id="build_cat_reg",
        python_callable=task_build_cat_reg,
    )

    extract_and_load_food_sales >> build_cat_reg
