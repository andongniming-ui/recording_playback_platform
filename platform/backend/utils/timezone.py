from __future__ import annotations

from datetime import datetime, timedelta, timezone


BEIJING_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")


def now_beijing() -> datetime:
    return datetime.now(BEIJING_TZ)


def ensure_beijing_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=BEIJING_TZ)
    return value.astimezone(BEIJING_TZ)


def from_epoch_ms_beijing(epoch_ms: int | str | float) -> datetime:
    return datetime.fromtimestamp(int(epoch_ms) / 1000, tz=BEIJING_TZ)


def current_time_for_update() -> datetime:
    return now_beijing()
