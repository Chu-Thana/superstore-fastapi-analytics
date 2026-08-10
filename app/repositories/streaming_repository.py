import csv
import io
import json
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.config import (
    AWS_REGION,
    S3_BUCKET,
    STREAMING_CURATED_S3_KEY,
    STREAMING_SUMMARY_S3_KEY,
)


def read_text_from_s3(
    s3_key: str,
) -> str:
    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION,
    )

    try:
        response = s3_client.get_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
        )
    except ClientError as exc:
        raise FileNotFoundError(
            f"S3 object is unavailable: "
            f"s3://{S3_BUCKET}/{s3_key}"
        ) from exc

    return (
        response["Body"]
        .read()
        .decode("utf-8-sig")
    )


def read_csv_rows_from_s3(
    s3_key: str,
) -> list[dict[str, str]]:
    csv_content = read_text_from_s3(
        s3_key
    )

    reader = csv.DictReader(
        io.StringIO(csv_content)
    )

    return list(reader)


def read_json_object_from_s3(
    s3_key: str,
) -> dict[str, Any]:
    json_content = read_text_from_s3(
        s3_key
    )

    try:
        content = json.loads(
            json_content
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON object: "
            f"s3://{S3_BUCKET}/{s3_key}"
        ) from exc

    if not isinstance(content, dict):
        raise ValueError(
            f"JSON content must be an object: "
            f"s3://{S3_BUCKET}/{s3_key}"
        )

    return content


def read_streaming_events() -> list[dict[str, Any]]:
    rows = read_csv_rows_from_s3(
        STREAMING_CURATED_S3_KEY
    )

    events: list[dict[str, Any]] = []

    for row in rows:
        events.append(
            {
                "event_id": row["event_id"],
                "event_type": row["event_type"],
                "event_timestamp": row["event_timestamp"],
                "source_system": row["source_system"],
                "fiscal_year": int(row["fiscal_year"]),
                "supplier_name": row["supplier_name"],
                "department": row["department"],
                "vouchers_paid": float(row["vouchers_paid"]),
                "payment_amount": float(row["payment_amount"]),
                "dedup_status": row["dedup_status"],
                "ingested_at": row["ingested_at"],
            }
        )

    return events

def read_streaming_summary() -> dict[str, Any]:
    return read_json_object_from_s3(
        STREAMING_SUMMARY_S3_KEY
    )

