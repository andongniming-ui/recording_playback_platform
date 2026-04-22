"""Helpers for deriving replay execution context from test cases."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.test_case import TestCase


async def infer_application_id_for_case_ids(
    db: AsyncSession,
    case_ids: list[int],
) -> int | None:
    """
    Infer a single application_id from a set of test cases.

    Returns the unique non-null application_id when all cases belong to the same
    application, None when all cases are unassigned, and raises ValueError when
    the selected cases span multiple applications or mix assigned/unassigned
    application state.
    """
    if not case_ids:
        return None

    result = await db.execute(
        select(TestCase.application_id).where(TestCase.id.in_(case_ids))
    )
    application_ids = list(result.scalars().all())

    non_null_ids = {app_id for app_id in application_ids if app_id is not None}
    has_null_ids = any(app_id is None for app_id in application_ids)

    if len(non_null_ids) > 1:
        raise ValueError("All replayed test cases must belong to the same application")

    if has_null_ids and non_null_ids:
        raise ValueError(
            "Replayed test cases must either all have an application or all be unassigned"
        )

    if not non_null_ids:
        return None

    return next(iter(non_null_ids))
