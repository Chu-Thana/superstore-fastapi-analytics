from __future__ import annotations

from app.models.streaming import (
    StreamingDedupCount,
    StreamingDepartmentSummaryItem,
    StreamingDepartmentSummaryResponse,
    StreamingEventItem,
    StreamingEventsResponse,
    StreamingSummaryResponse,
    StreamingSupplierSummaryItem,
    StreamingSupplierSummaryResponse,
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
    events = read_streaming_events()

    if fiscal_year is not None:
        events = [
            event
            for event in events
            if event["fiscal_year"] == fiscal_year
        ]

    if department:
        department_query = department.casefold()

        events = [
            event
            for event in events
            if department_query
            in str(event["department"]).casefold()
        ]

    if supplier_name:
        supplier_query = supplier_name.casefold()

        events = [
            event
            for event in events
            if supplier_query
            in str(event["supplier_name"]).casefold()
        ]

    if dedup_status:
        dedup_query = dedup_status.casefold()

        events = [
            event
            for event in events
            if str(event["dedup_status"]).casefold()
            == dedup_query
        ]

    total_count = len(events)
    paginated_events = events[offset : offset + limit]

    items = [
        StreamingEventItem(**event)
        for event in paginated_events
    ]

    return StreamingEventsResponse(
        total_count=total_count,
        count=len(items),
        limit=limit,
        offset=offset,
        data=items,
    )

def get_streaming_summary() -> StreamingSummaryResponse:
    events = read_streaming_events()

    if not events:
        raise ValueError(
            "Streaming events are empty."
        )

    total_events = len(events)

    total_payment_amount = sum(
        event["payment_amount"]
        for event in events
    )

    unique_departments = len(
        {
            event["department"]
            for event in events
        }
    )

    unique_suppliers = len(
        {
            event["supplier_name"]
            for event in events
        }
    )

    fiscal_years = [
        event["fiscal_year"]
        for event in events
    ]

    minimum_fiscal_year = min(fiscal_years)
    maximum_fiscal_year = max(fiscal_years)

    events_by_fiscal_year_map: dict[int, int] = {}

    for event in events:
        fiscal_year = int(event["fiscal_year"])

        events_by_fiscal_year_map[fiscal_year] = (
                events_by_fiscal_year_map.get(
                    fiscal_year,
                    0,
                )
                + 1
        )

    events_by_fiscal_year = [
        StreamingYearCount(
            fiscal_year=fiscal_year,
            event_count=event_count,
        )
        for fiscal_year, event_count
        in sorted(events_by_fiscal_year_map.items())
    ]

    events_by_dedup_status_map: dict[str, int] = {}

    for event in events:
        dedup_status = str(event["dedup_status"])

        events_by_dedup_status_map[dedup_status] = (
                events_by_dedup_status_map.get(
                    dedup_status,
                    0,
                )
                + 1
        )

    events_by_dedup_status = [
        StreamingDedupCount(
            dedup_status=dedup_status,
            event_count=event_count,
        )
        for dedup_status, event_count
        in sorted(events_by_dedup_status_map.items())
    ]

    return StreamingSummaryResponse(
        total_events=total_events,
        total_payment_amount=round(
            total_payment_amount,
            2,
        ),
        unique_departments=unique_departments,
        unique_suppliers=unique_suppliers,
        minimum_fiscal_year=minimum_fiscal_year,
        maximum_fiscal_year=maximum_fiscal_year,
        events_by_fiscal_year=events_by_fiscal_year,
        events_by_dedup_status=events_by_dedup_status,
    )


def get_streaming_department_summary(
    *,
    fiscal_year: int | None = None,
    department: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> StreamingDepartmentSummaryResponse:

    events = read_streaming_events()

    if fiscal_year is not None:
        events = [
            event
            for event in events
            if event["fiscal_year"] == fiscal_year
        ]

    if department:
        department_query = department.casefold()

        events = [
            event
            for event in events
            if department_query
            in str(event["department"]).casefold()
        ]

    grouped_events: dict[str, list[dict[str, object]]] = {}

    for event in events:
        department_name = str(event["department"])

        grouped_events.setdefault(
            department_name,
            [],
        ).append(event)

    items = []

    for department_name, department_events in grouped_events.items():
        fiscal_years = [
            int(event["fiscal_year"])
            for event in department_events
        ]

        items.append(
            StreamingDepartmentSummaryItem(
                department=department_name,
                event_count=len(department_events),
                total_payment_amount=round(
                    sum(
                        float(event["payment_amount"])
                        for event in department_events
                    ),
                    2,
                ),
                unique_suppliers=len(
                    {
                        str(event["supplier_name"])
                        for event in department_events
                    }
                ),
                minimum_fiscal_year=min(fiscal_years),
                maximum_fiscal_year=max(fiscal_years),
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
    events = read_streaming_events()

    if fiscal_year is not None:
        events = [
            event
            for event in events
            if event["fiscal_year"] == fiscal_year
        ]

    if supplier_name:
        supplier_query = supplier_name.casefold()

        events = [
            event
            for event in events
            if supplier_query
            in str(event["supplier_name"]).casefold()
        ]

    grouped_events: dict[str, list[dict[str, object]]] = {}

    for event in events:
        current_supplier_name = str(event["supplier_name"])

        grouped_events.setdefault(
            current_supplier_name,
            [],
        ).append(event)

    items = []

    for current_supplier_name, supplier_events in grouped_events.items():
        fiscal_years = [
            int(event["fiscal_year"])
            for event in supplier_events
        ]

        items.append(
            StreamingSupplierSummaryItem(
                supplier_name=current_supplier_name,
                event_count=len(supplier_events),
                total_payment_amount=round(
                    sum(
                        float(event["payment_amount"])
                        for event in supplier_events
                    ),
                    2,
                ),
                unique_departments=len(
                    {
                        str(event["department"])
                        for event in supplier_events
                    }
                ),
                minimum_fiscal_year=min(fiscal_years),
                maximum_fiscal_year=max(fiscal_years),
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