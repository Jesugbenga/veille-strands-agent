"""Seed a few messy records so the agent has real work to do in a demo.

Creates a double-booking, a booking missing its service, and an unresolved
urgent call — exactly the kinds of things the concierge should catch.

    python seed_demo.py
"""
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

import supabase_rest as db

load_dotenv()
BUSINESS_ID = os.environ["VEILLE_BUSINESS_ID"]


def tomorrow_at(hour: int, minute: int = 0) -> str:
    d = datetime.now(timezone.utc) + timedelta(days=1)
    return d.replace(hour=hour, minute=minute, second=0, microsecond=0).isoformat()


def booking(name: str, service, when: str, phone: str = "+16045550000") -> None:
    db.insert(
        "bookings",
        {
            "business_id": BUSINESS_ID,
            "customer_name": name,
            "customer_phone": phone,
            "requested_service": service,
            "confirmed_time": when,
            "integration_type": "veille_native",
            "status": "confirmed",
        },
    )


def urgent_call(number: str, summary: str) -> None:
    db.insert(
        "calls",
        {
            "business_id": BUSINESS_ID,
            "channel": "voice",
            "caller_number": number,
            "summary": summary,
            "urgency": "urgent",
            "status": "escalated",
        },
    )


def main() -> None:
    print(f"Seeding demo data for business {BUSINESS_ID} ...")
    booking("Jordan Blake", "Deep tissue massage", tomorrow_at(14, 0))
    booking("Alex Rivera", "Facial", tomorrow_at(14, 30))  # overlaps Jordan -> double-booking
    booking("Sam Okafor", None, tomorrow_at(16, 0))         # missing service -> ambiguous
    urgent_call(
        "+16045551234",
        "Caller reported a burst pipe flooding the salon and needs a callback tonight.",
    )
    print("Done: 3 bookings (incl. a double-booking + a missing-service) and 1 urgent call.")
    print("Now run:  python agent.py")


if __name__ == "__main__":
    main()
