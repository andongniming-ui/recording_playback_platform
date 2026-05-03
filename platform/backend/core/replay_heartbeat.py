"""Replay job heartbeat helpers."""

import asyncio
import logging
import os
import socket
import uuid

from sqlalchemy import update

from config import settings
import database
from models.replay import ReplayJob
from utils.timezone import now_beijing

logger = logging.getLogger(__name__)

REPLAY_WORKER_ID = f"{socket.gethostname()}:{os.getpid()}:{uuid.uuid4().hex[:8]}"


async def touch_replay_job_heartbeat(job_id: int) -> None:
    async with database.async_session_factory() as db:
        await db.execute(
            update(ReplayJob)
            .where(ReplayJob.id == job_id, ReplayJob.status == "RUNNING")
            .values(heartbeat_at=now_beijing(), worker_id=REPLAY_WORKER_ID)
        )
        await db.commit()


async def replay_job_heartbeat_loop(job_id: int) -> None:
    interval = max(settings.replay_job_heartbeat_interval_s, 1)
    while True:
        await asyncio.sleep(interval)
        try:
            await touch_replay_job_heartbeat(job_id)
        except Exception:
            logger.exception("Failed to update replay job heartbeat: job_id=%s", job_id)


_REPLAY_WORKER_ID = REPLAY_WORKER_ID
_touch_replay_job_heartbeat = touch_replay_job_heartbeat
_replay_job_heartbeat_loop = replay_job_heartbeat_loop
