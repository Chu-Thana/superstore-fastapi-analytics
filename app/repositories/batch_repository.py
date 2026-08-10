import csv
import io

import boto3
from botocore.exceptions import ClientError

from app.config import (
    AWS_REGION,
    FUND_CATEGORY_SUMMARY_S3_KEY,
    PENDING_BY_DEPARTMENT_S3_KEY,
    S3_BUCKET,
    SPENDING_BY_DEPARTMENT_S3_KEY,
    SPENDING_BY_FISCAL_YEAR_S3_KEY,
    TOP_SUPPLIERS_S3_KEY,
)


def read_csv_rows_from_s3(
    s3_key: str,
) -> list[dict[str, str]]:
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

    csv_content = (
        response["Body"]
        .read()
        .decode("utf-8-sig")
    )

    reader = csv.DictReader(
        io.StringIO(csv_content)
    )

    return list(reader)


def read_spending_by_fiscal_year() -> list[dict[str, int | float]]:
    rows = read_csv_rows_from_s3(
        SPENDING_BY_FISCAL_YEAR_S3_KEY
    )

    records: list[dict[str, int | float]] = []

    for row in rows:
        records.append(
            {
                "fiscal_year": int(row["fiscal_year"]),
                "total_vouchers_paid": float(
                    row["total_vouchers_paid"]
                ),
                "total_vouchers_pending": float(
                    row["total_vouchers_pending"]
                ),
                "total_encumbrance_balance": float(
                    row["total_encumbrance_balance"]
                ),
                "total_pending_retainage": float(
                    row["total_pending_retainage"]
                ),
                "record_count": int(row["record_count"]),
                "unique_suppliers": int(row["unique_suppliers"]),
                "negative_paid_records": int(
                    row["negative_paid_records"]
                ),
                "large_paid_1m_records": int(
                    row["large_paid_1m_records"]
                ),
                "missing_po_date_records": int(
                    row["missing_po_date_records"]
                ),
            }
        )

    return records


def read_spending_by_department(
) -> list[dict[str, str | int | float]]:
    rows = read_csv_rows_from_s3(
        SPENDING_BY_DEPARTMENT_S3_KEY
    )

    records: list[dict[str, str | int | float]] = []

    for row in rows:
        records.append(
            {
                "fiscal_year": int(row["fiscal_year"]),
                "organization_group": row["organization_group"],
                "department": row["department"],
                "total_vouchers_paid": float(
                    row["total_vouchers_paid"]
                ),
                "total_vouchers_pending": float(
                    row["total_vouchers_pending"]
                ),
                "total_encumbrance_balance": float(
                    row["total_encumbrance_balance"]
                ),
                "total_pending_retainage": float(
                    row["total_pending_retainage"]
                ),
                "record_count": int(row["record_count"]),
                "unique_suppliers": int(row["unique_suppliers"]),
                "negative_paid_records": int(
                    row["negative_paid_records"]
                ),
                "large_paid_1m_records": int(
                    row["large_paid_1m_records"]
                ),
                "missing_po_date_records": int(
                    row["missing_po_date_records"]
                ),
            }
        )

    return records


def read_top_suppliers(
) -> list[dict[str, str | int | float]]:
    rows = read_csv_rows_from_s3(
        TOP_SUPPLIERS_S3_KEY
    )

    records: list[dict[str, str | int | float]] = []

    for row in rows:
        records.append(
            {
                "supplier_name": row["supplier_name"],
                "total_vouchers_paid": float(
                    row["total_vouchers_paid"]
                ),
                "total_vouchers_pending": float(
                    row["total_vouchers_pending"]
                ),
                "total_encumbrance_balance": float(
                    row["total_encumbrance_balance"]
                ),
                "total_pending_retainage": float(
                    row["total_pending_retainage"]
                ),
                "record_count": int(row["record_count"]),
                "unique_suppliers": int(row["unique_suppliers"]),
                "negative_paid_records": int(
                    row["negative_paid_records"]
                ),
                "large_paid_1m_records": int(
                    row["large_paid_1m_records"]
                ),
                "missing_po_date_records": int(
                    row["missing_po_date_records"]
                ),
            }
        )

    return records


def read_pending_by_department(
) -> list[dict[str, str | int | float]]:
    rows = read_csv_rows_from_s3(
        PENDING_BY_DEPARTMENT_S3_KEY
    )

    records: list[dict[str, str | int | float]] = []

    for row in rows:
        records.append(
            {
                "fiscal_year": int(row["fiscal_year"]),
                "department": row["department"],
                "total_vouchers_paid": float(
                    row["total_vouchers_paid"]
                ),
                "total_vouchers_pending": float(
                    row["total_vouchers_pending"]
                ),
                "total_encumbrance_balance": float(
                    row["total_encumbrance_balance"]
                ),
                "total_pending_retainage": float(
                    row["total_pending_retainage"]
                ),
                "record_count": int(row["record_count"]),
                "unique_suppliers": int(row["unique_suppliers"]),
                "negative_paid_records": int(
                    row["negative_paid_records"]
                ),
                "large_paid_1m_records": int(
                    row["large_paid_1m_records"]
                ),
                "missing_po_date_records": int(
                    row["missing_po_date_records"]
                ),
            }
        )

    return records


def read_fund_category_summary(
) -> list[dict[str, str | int | float]]:
    rows = read_csv_rows_from_s3(
        FUND_CATEGORY_SUMMARY_S3_KEY
    )

    records: list[dict[str, str | int | float]] = []

    for row in rows:
        records.append(
            {
                "fiscal_year": int(row["fiscal_year"]),
                "fund_type": row["fund_type"],
                "fund_category": row["fund_category"],
                "total_vouchers_paid": float(
                    row["total_vouchers_paid"]
                ),
                "total_vouchers_pending": float(
                    row["total_vouchers_pending"]
                ),
                "total_encumbrance_balance": float(
                    row["total_encumbrance_balance"]
                ),
                "total_pending_retainage": float(
                    row["total_pending_retainage"]
                ),
                "record_count": int(row["record_count"]),
                "unique_suppliers": int(row["unique_suppliers"]),
                "negative_paid_records": int(
                    row["negative_paid_records"]
                ),
                "large_paid_1m_records": int(
                    row["large_paid_1m_records"]
                ),
                "missing_po_date_records": int(
                    row["missing_po_date_records"]
                ),
            }
        )

    return records