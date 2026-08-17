import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(
    PROJECT_ROOT / ".env"
)

DATA_DIR = PROJECT_ROOT / "data"


S3_BUCKET = os.getenv(
    "S3_BUCKET",
    "your-s3-bucket-name",
)

S3_PREFIX = os.getenv(
    "S3_PREFIX",
    "data-platform/vendor-payments",
)

AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-southeast-1",
)

def build_batch_gold_s3_key(file_name: str) -> str:
    table_name = Path(file_name).stem

    return (
        f"{S3_PREFIX}/gold/full/"
        f"{table_name}/{file_name}"
    )


SPENDING_BY_FISCAL_YEAR_S3_KEY = build_batch_gold_s3_key(
    "mart_spending_by_fiscal_year.csv"
)

SPENDING_BY_DEPARTMENT_S3_KEY = build_batch_gold_s3_key(
    "mart_spending_by_department.csv"
)

TOP_SUPPLIERS_S3_KEY = build_batch_gold_s3_key(
    "mart_spending_by_supplier_top_n.csv"
)

PENDING_BY_DEPARTMENT_S3_KEY = build_batch_gold_s3_key(
    "mart_pending_by_department.csv"
)

FUND_CATEGORY_SUMMARY_S3_KEY = build_batch_gold_s3_key(
    "mart_fund_category_summary.csv"
)

STREAMING_CURATED_S3_KEY = (
    f"{S3_PREFIX}/streaming/curated/"
    "vendor_payments_streaming_events.csv"
)

STREAMING_SUMMARY_S3_KEY = (
    f"{S3_PREFIX}/streaming/analytics/"
    "vendor_payments_streaming_summary.json"
)

STREAMING_DEPARTMENT_SUMMARY_S3_KEY = (
    f"{S3_PREFIX}/streaming/analytics/"
    "vendor_payments_streaming_department_summary.json"
)

API_CACHE_TTL_SECONDS = float(
    os.getenv(
        "CACHE_TTL_SECONDS",
        "60",
    )
)