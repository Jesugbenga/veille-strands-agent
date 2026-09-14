"""Strands tools — thin wrappers over Veille's Supabase data.

Each function is exposed to the agent via the @tool decorator; the docstring is
what the model reads to decide when to call it.
"""
import os
from datetime import datetime, timedelta, timezone

from strands import tool

import supabase_rest as db

BUSINESS_ID = os.environ["VEILLE_BUSINESS_ID"]
APPOINTMENT_MINUTES = 60


def _since(hours: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


@tool
def list_recent_bookings(hours: int = 24) -> list:
    """List bookings created in the last `hours` hours: id, customer name/phone,
    requested service, confirmed time, status. Use this to review overnight
    bookings that may need a confirmation or a human decision."""
    return db.select(
        "bookings",
        {
            "select": "id,customer_name,customer_phone,requested_service,confirmed_time,status,call_id,created_at",
            "business_id": f"eq.{BUSINESS_ID}",
            "created_at": f"gte.{_since(hours)}",
            "order": "confirmed_time.asc",
        },
    )


@tool
def list_recent_calls(hours: int = 24) -> list:
    """List calls from the last `hours` hours: summary, urgency, status, caller
    name/number. No transcript. Use this to spot unresolved or urgent calls."""
    return db.select(
        "calls",
        {
            "select": "id,caller_name,caller_number,summary,urgency,status,created_at",
            "business_id": f"eq.{BUSINESS_ID}",
            "created_at": f"gte.{_since(hours)}",
            "order": "created_at.desc",
        },
    )


@tool
def find_double_bookings() -> list:
    """Return pairs of confirmed upcoming bookings whose 1-hour slots overlap.
    Use this to catch scheduling conflicts a human should resolve."""
    rows = db.select(
        "bookings",
        {
            "select": "id,customer_name,requested_service,confirmed_time",
            "business_id": f"eq.{BUSINESS_ID}",
            "status": "eq.confirmed",
            "confirmed_time": f"gte.{datetime.now(timezone.utc).isoformat()}",
            "order": "confirmed_time.asc",
        },
    )
    slot = timedelta(minutes=APPOINTMENT_MINUTES)
    conflicts = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            if not a.get("confirmed_time") or not b.get("confirmed_time"):
                continue
            sa = datetime.fromisoformat(a["confirmed_time"].replace("Z", "+00:00"))
            sb = datetime.fromisoformat(b["confirmed_time"].replace("Z", "+00:00"))
            if sa < sb + slot and sb < sa + slot:
                conflicts.append({"a": a, "b": b})
    return conflicts


@tool
def draft_confirmation_text(booking_id: str) -> str:
    """Draft (do NOT send) a short, friendly confirmation SMS for a booking.
    Returns the drafted message text for a human to approve."""
    rows = db.select(
        "bookings",
        {"select": "customer_name,requested_service,confirmed_time", "id": f"eq.{booking_id}"},
    )
    if not rows:
        return "Booking not found."
    b = rows[0]
    when = b.get("confirmed_time", "")
    return (
        f"Hi {b.get('customer_name') or 'there'}, this confirms your "
        f"{b.get('requested_service') or 'appointment'} on {when}. "
        f"Reply here if you need to change it."
    )


@tool
def create_staff_task(title: str, detail: str, severity: str = "review") -> dict:
    """Create a task for staff to review. severity is 'info', 'review', or
    'urgent'. Only call this for something a human must actually decide."""
    sev = severity if severity in ("info", "review", "urgent") else "review"
    rows = db.insert(
        "agent_tasks",
        {"business_id": BUSINESS_ID, "title": title, "detail": detail, "severity": sev, "status": "open"},
    )
    return rows[0] if rows else {}
