from typing import Awaitable, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from bot.db import SessionLocal
from bot.models import Schedule

JobFunc = Callable[[int], Awaitable[None]]


def _parse_time(time_str: str) -> tuple[int, int]:
    hour, minute = time_str.split(":")
    return int(hour), int(minute)


def setup_scheduler(job_func: JobFunc) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    session = SessionLocal()
    active_schedules = session.scalars(
        select(Schedule).where(Schedule.is_active == True)
    ).all()
    session.close()

    for schedule in active_schedules:
        hour, minute = _parse_time(schedule.time)
        scheduler.add_job(
            job_func,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=schedule.timezone),
            args=[schedule.user_id],
            id=f"schedule_{schedule.id}",
        )

    return scheduler