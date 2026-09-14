"""Thin Supabase REST wrapper (service-role key, bypasses RLS)."""
import os
import requests

_BASE = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"
_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
_HEADERS = {
    "apikey": _KEY,
    "Authorization": f"Bearer {_KEY}",
    "Content-Type": "application/json",
}


def select(table: str, params: dict) -> list:
    r = requests.get(f"{_BASE}/{table}", headers=_HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def insert(table: str, row: dict) -> list:
    r = requests.post(
        f"{_BASE}/{table}",
        headers={**_HEADERS, "Prefer": "return=representation"},
        json=row,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def update(table: str, match: dict, patch: dict) -> list:
    params = {k: f"eq.{v}" for k, v in match.items()}
    r = requests.patch(
        f"{_BASE}/{table}",
        headers={**_HEADERS, "Prefer": "return=representation"},
        params=params,
        json=patch,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()
