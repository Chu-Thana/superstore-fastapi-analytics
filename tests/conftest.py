import csv
import json
from pathlib import Path

import pytest

from app.config import (
    FUND_CATEGORY_SUMMARY_S3_KEY,
    PENDING_BY_DEPARTMENT_S3_KEY,
    SPENDING_BY_DEPARTMENT_S3_KEY,
    SPENDING_BY_FISCAL_YEAR_S3_KEY,
    TOP_SUPPLIERS_S3_KEY,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BATCH_DATA_DIR = PROJECT_ROOT / "data" / "batch"
STREAMING_DATA_DIR = PROJECT_ROOT / "data" / "streaming"


def load_batch_csv_rows(
    filename: str,
) -> list[dict[str, str]]:
    file_path = BATCH_DATA_DIR / filename

    with file_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


@pytest.fixture(autouse=True)
def mock_batch_s3_reader(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    s3_key_to_filename = {
        SPENDING_BY_FISCAL_YEAR_S3_KEY:
            "mart_spending_by_fiscal_year.csv",
        SPENDING_BY_DEPARTMENT_S3_KEY:
            "mart_spending_by_department.csv",
        TOP_SUPPLIERS_S3_KEY:
            "mart_spending_by_supplier_top_n.csv",
        PENDING_BY_DEPARTMENT_S3_KEY:
            "mart_pending_by_department.csv",
        FUND_CATEGORY_SUMMARY_S3_KEY:
            "mart_fund_category_summary.csv",
    }

    def mock_read_csv_rows_from_s3(
        s3_key: str,
    ) -> list[dict[str, str]]:
        filename = s3_key_to_filename[s3_key]

        return load_batch_csv_rows(
            filename
        )

    monkeypatch.setattr(
        "app.repositories.batch_repository."
        "read_csv_rows_from_s3",
        mock_read_csv_rows_from_s3,
    )


def load_streaming_events() -> list[dict[str, object]]:
    file_path = (
        STREAMING_DATA_DIR
        / "vendor_payments_streaming_sample.jsonl"
    )

    events: list[dict[str, object]] = []

    with file_path.open(
            "r",
            encoding="utf-8-sig",
    ) as file:
        for line in file:
            raw_event = json.loads(line)

            events.append(
                {
                    "event_id": raw_event["event_id"],
                    "event_type": raw_event["event_type"],
                    "event_timestamp": raw_event["event_timestamp"],
                    "source_system": raw_event["source_system"],
                    "fiscal_year": raw_event["fiscal_year"],
                    "supplier_name": raw_event["supplier_name"],
                    "department": raw_event["department"],
                    "vouchers_paid": raw_event["vouchers_paid"],
                    "payment_amount": raw_event["payment_amount"],
                    "dedup_status": raw_event["dedup_status"],
                    "ingested_at": raw_event["ingested_at"],
                }
            )

    return events


@pytest.fixture(autouse=True)
def mock_streaming_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = load_streaming_events()

    monkeypatch.setattr(
        "app.services.streaming_service.read_streaming_events",
        lambda: events,
    )
