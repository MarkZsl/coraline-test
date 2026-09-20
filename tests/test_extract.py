from pathlib import Path

import pytest

from src.extract import extract_food_sales

SAMPLE_FILE = Path(__file__).resolve().parent.parent / "data" / "de_challenge_data.xlsx"


@pytest.mark.skipif(not SAMPLE_FILE.exists(), reason="sample workbook not present")
def test_extract_combines_all_blocks():
    df = extract_food_sales(SAMPLE_FILE, "FoodSales")
    assert len(df) == 244  # 2022 block (123 rows) + 2023 block (121 rows)


@pytest.mark.skipif(not SAMPLE_FILE.exists(), reason="sample workbook not present")
def test_extract_has_expected_columns():
    df = extract_food_sales(SAMPLE_FILE, "FoodSales")
    assert list(df.columns) == [
        "id", "sale_date", "region", "city", "category", "product",
        "qty", "unit_price", "total_price",
    ]


@pytest.mark.skipif(not SAMPLE_FILE.exists(), reason="sample workbook not present")
def test_extract_no_duplicate_ids():
    df = extract_food_sales(SAMPLE_FILE, "FoodSales")
    assert df["id"].is_unique


@pytest.mark.skipif(not SAMPLE_FILE.exists(), reason="sample workbook not present")
def test_extract_covers_both_years():
    df = extract_food_sales(SAMPLE_FILE, "FoodSales")
    years = {d.year for d in df["sale_date"]}
    assert years == {2022, 2023}


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        extract_food_sales("does/not/exist.xlsx")
