from arq.cron import cron
from arq.connections import RedisSettings
from sqlalchemy import select

from src.bot.notifications import notify_bad_status, shutdown_bot, startup_bot
from src.config import settings
from src.database import Session
from src.live_checker.models import Link, LinkCheck
from src.live_checker.utils import check_link


BAD_STATUS_CODE_MIN = 400


async def perform_checks(ctx: dict) -> None:
    async with Session() as session:
        result = await session.execute(select(Link))
        links = result.scalars().all()

        for link in links:
            check_result = await check_link(link.url)
            status_code = check_result["status_code"]
            response_time = check_result["response_time"]

            new_check = LinkCheck(
                link_id=link.id,
                status_code=status_code,
                response_time=response_time,
            )
            session.add(new_check)

            if status_code >= BAD_STATUS_CODE_MIN:
                await ctx["redis"].enqueue_job(
                    "notify_bad_status",
                    link.telegram_id,
                    link.url,
                    status_code,
                    response_time,
                )

        await session.commit()


class WorkerSettings:
    functions = [perform_checks, notify_bad_status]
    cron_jobs = [cron(perform_checks, minute={0, 10, 20, 30, 40, 50})]
    on_startup = startup_bot
    on_shutdown = shutdown_bot
    redis_settings = RedisSettings(
        host=settings.redis_settings.redis_host,
        port=settings.redis_settings.redis_port,
        password=settings.redis_settings.redis_password,
    )
