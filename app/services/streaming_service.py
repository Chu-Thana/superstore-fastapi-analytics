from __future__ import annotations

from app.models.streaming import (
    StreamingDepartmentSummaryItem,
    StreamingDepartmentSummaryResponse,
    StreamingEventItem,
    StreamingEventsResponse,
    StreamingSummaryResponse,
    StreamingSupplierSummaryItem,
    StreamingSupplierSummaryResponse,
    StreamingDedupCount,
    StreamingYearCount,
)

from app.repositories.streaming_repository import (
    read_streaming_events,
)


def get_streaming_events(
    *,
    fiscal_year: int | None = None,
    department: str | None = None,
    supplier_name: str | None = None,
    dedup_status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> StreamingEventsResponse:
    department_query = (
        department.casefold()
        if department
        else None
    )

    supplier_query = (
        supplier_name.casefold()
        if supplier_name
        else None
    )

    dedup_query = (
        dedup_status.casefold()
        if dedup_status
        else None
    )

    total_count = 0
    selected_events: list[dict[str, object]] = []

    for event in read_streaming_events():
        if (
            fiscal_year is not None
            and event["fiscal_year"] != fiscal_year
        ):
            continue

        if (
            department_query
            and department_query
            not in str(event["department"]).casefold()
        ):
            continue

        if (
            supplier_query
            and supplier_query
            not in str(event["supplier_name"]).casefold()
        ):
            continue

        if (
            dedup_query
            and str(event["dedup_status"]).casefold()
            != dedup_query
        ):
            continue

        if (
            total_count >= offset
            and len(selected_events) < limit
        ):
            selected_events.append(event)

        total_count += 1

    items = [
        StreamingEventItem(**event)
        for event in selected_events
    ]

    return StreamingEventsResponse(
        total_count=total_count,
        count=len(items),
        limit=limit,
        offset=offset,
        data=items,
    )


def get_streaming_summary() -> StreamingSummaryResponse:
    total_events = 0
    total_payment_amount = 0.0

    departments: set[str] = set()
    suppliers: set[str] = set()

    fiscal_year_counts: dict[int, int] = {}
    dedup_status_counts: dict[str, int] = {}

    minimum_fiscal_year: int | None = None
    maximum_fiscal_year: int | None = None

    for event in read_streaming_events():
        total_events += 1

        fiscal_year = int(event["fiscal_year"])
        department = str(event["department"])
        supplier_name = str(event["supplier_name"])
        dedup_status = str(event["dedup_status"])

        total_payment_amount += float(
            event["payment_amount"]
        )

        departments.add(department)
        suppliers.add(supplier_name)

        fiscal_year_counts[fiscal_year] = (
            fiscal_year_counts.get(
                fiscal_year,
                0,
            )
            + 1
        )

        dedup_status_counts[dedup_status] = (
            dedup_status_counts.get(
                dedup_status,
                0,
            )
            + 1
        )

        if (
            minimum_fiscal_year is None
            or fiscal_year < minimum_fiscal_year
        ):
            minimum_fiscal_year = fiscal_year

        if (
            maximum_fiscal_year is None
            or fiscal_year > maximum_fiscal_year
        ):
            maximum_fiscal_year = fiscal_year

    if (
        total_events == 0
        or minimum_fiscal_year is None
        or maximum_fiscal_year is None
    ):
        raise ValueError(
            "Streaming events are empty."
        )

    return StreamingSummaryResponse(
        total_events=total_events,
        total_payment_amount=round(
            total_payment_amount,
            2,
        ),
        unique_departments=len(departments),
        unique_suppliers=len(suppliers),
        minimum_fiscal_year=minimum_fiscal_year,
        maximum_fiscal_year=maximum_fiscal_year,
        events_by_fiscal_year=[
            StreamingYearCount(
                fiscal_year=fiscal_year,
                event_count=event_count,
            )
            for fiscal_year, event_count
            in sorted(
                fiscal_year_counts.items()
            )
        ],
        events_by_dedup_status=[
            StreamingDedupCount(
                dedup_status=dedup_status,
                event_count=event_count,
            )
            for dedup_status, event_count
            in sorted(
                dedup_status_counts.items()
            )
        ],
    )


def get_streaming_department_summary(
    *,
    fiscal_year: int | None = None,
    department: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> StreamingDepartmentSummaryResponse:
    department_query = (
        department.casefold()
        if department
        else None
    )

    grouped: dict[str, dict[str, object]] = {}

    for event in read_streaming_events():
        if (
            fiscal_year is not None
            and event["fiscal_year"] != fiscal_year
        ):
            continue

        department_name = str(
            event["department"]
        )

        if (
            department_query
            and department_query
            not in department_name.casefold()
        ):
            continue

        event_fiscal_year = int(
            event["fiscal_year"]
        )

        stats = grouped.setdefault(
            department_name,
            {
                "event_count": 0,
                "total_payment_amount": 0.0,
                "suppliers": set(),
                "minimum_fiscal_year": event_fiscal_year,
                "maximum_fiscal_year": event_fiscal_year,
            },
        )

        stats["event_count"] = (
            int(stats["event_count"])
            + 1
        )

        stats["total_payment_amount"] = (
            float(stats["total_payment_amount"])
            + float(event["payment_amount"])
        )

        suppliers = stats["suppliers"]

        if isinstance(suppliers, set):
            suppliers.add(
                str(event["supplier_name"])
            )

        stats["minimum_fiscal_year"] = min(
            int(stats["minimum_fiscal_year"]),
            event_fiscal_year,
        )

        stats["maximum_fiscal_year"] = max(
            int(stats["maximum_fiscal_year"]),
            event_fiscal_year,
        )

    items = []

    for department_name, stats in grouped.items():
        suppliers = stats["suppliers"]

        items.append(
            StreamingDepartmentSummaryItem(
                department=department_name,
                event_count=int(
                    stats["event_count"]
                ),
                total_payment_amount=round(
                    float(
                        stats[
                            "total_payment_amount"
                        ]
                    ),
                    2,
                ),
                unique_suppliers=(
                    len(suppliers)
                    if isinstance(suppliers, set)
                    else 0
                ),
                minimum_fiscal_year=int(
                    stats["minimum_fiscal_year"]
                ),
                maximum_fiscal_year=int(
                    stats["maximum_fiscal_year"]
                ),
            )
        )

    items.sort(
        key=lambda item: item.event_count,
        reverse=True,
    )

    total_count = len(items)
    paginated_items = items[offset : offset + limit]

    return StreamingDepartmentSummaryResponse(
        total_count=total_count,
        count=len(paginated_items),
        limit=limit,
        offset=offset,
        data=paginated_items,
    )


def get_streaming_supplier_summary(
    *,
    fiscal_year: int | None = None,
    supplier_name: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> StreamingSupplierSummaryResponse:
    supplier_query = (
        supplier_name.casefold()
        if supplier_name
        else None
    )

    grouped: dict[str, dict[str, object]] = {}

    for event in read_streaming_events():
        if (
            fiscal_year is not None
            and event["fiscal_year"] != fiscal_year
        ):
            continue

        current_supplier_name = str(
            event["supplier_name"]
        )

        if (
            supplier_query
            and supplier_query
            not in current_supplier_name.casefold()
        ):
            continue

        event_fiscal_year = int(
            event["fiscal_year"]
        )

        stats = grouped.setdefault(
            current_supplier_name,
            {
                "event_count": 0,
                "total_payment_amount": 0.0,
                "departments": set(),
                "minimum_fiscal_year": event_fiscal_year,
                "maximum_fiscal_year": event_fiscal_year,
            },
        )

        stats["event_count"] = (
            int(stats["event_count"])
            + 1
        )

        stats["total_payment_amount"] = (
            float(stats["total_payment_amount"])
            + float(event["payment_amount"])
        )

        departments = stats["departments"]

        if isinstance(departments, set):
            departments.add(
                str(event["department"])
            )

        stats["minimum_fiscal_year"] = min(
            int(stats["minimum_fiscal_year"]),
            event_fiscal_year,
        )

        stats["maximum_fiscal_year"] = max(
            int(stats["maximum_fiscal_year"]),
            event_fiscal_year,
        )

    items = []

    for current_supplier_name, stats in grouped.items():
        departments = stats["departments"]

        items.append(
            StreamingSupplierSummaryItem(
                supplier_name=current_supplier_name,
                event_count=int(
                    stats["event_count"]
                ),
                total_payment_amount=round(
                    float(
                        stats[
                            "total_payment_amount"
                        ]
                    ),
                    2,
                ),
                unique_departments=(
                    len(departments)
                    if isinstance(departments, set)
                    else 0
                ),
                minimum_fiscal_year=int(
                    stats["minimum_fiscal_year"]
                ),
                maximum_fiscal_year=int(
                    stats["maximum_fiscal_year"]
                ),
            )
        )

    items.sort(
        key=lambda item: item.event_count,
        reverse=True,
    )

    total_count = len(items)
    paginated_items = items[offset : offset + limit]

    return StreamingSupplierSummaryResponse(
        total_count=total_count,
        count=len(paginated_items),
        limit=limit,
        offset=offset,
        data=paginated_items,
    )

