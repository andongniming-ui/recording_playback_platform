"""Shared query helpers for API list endpoints."""
from sqlalchemy import asc, desc


def normalize_sort_order(value: str | None) -> str:
    return "asc" if (value or "").lower() == "asc" else "desc"


def apply_ordering(stmt, primary_column, id_column, sort_order: str):
    direction = asc if normalize_sort_order(sort_order) == "asc" else desc
    return stmt.order_by(direction(primary_column), direction(id_column))
