import asyncio
import logging
from typing import Awaitable, List

import aiohttp

from cryptomonitor import schemas
from cryptomonitor.config import HEADERS
from cryptomonitor.database import async_session, models
from cryptomonitor.database.crud import article as article_crud
from cryptomonitor.database.crud import feed as feed_crud
from cryptomonitor.ingestion import parser
from cryptomonitor.ingestion.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


async def fetch_article(article_job: models.ArticleJob, match_rules: List[models.Rule]):
    """
    Fetch article from website
    """
    async with async_session() as db_session:
        async with aiohttp.ClientSession() as http_session:
            try:
                async with http_session.get(
                    article_job.url, raise_for_status=True, headers=HEADERS
                ) as response:
                    logger.info(f"Got article {article_job.url}")
                    html = await response.content.read()
                    await parser.parse_article(
                        db_session=db_session,
                        article_job=article_job,
                        html=html,
                        match_rules=match_rules,
                    )
                    article_job_update = schemas.ArticleJobUpdate(
                        status=schemas.ArticleJobStatus.complete
                    )
            except Exception as e:
                logger.error(e)
                article_job_update = schemas.ArticleJobUpdate(
                    status=schemas.ArticleJobStatus.error
                )

            await article_crud.update_article_job(
                article_job_id=article_job.id,
                article_job_update=article_job_update,
            )


async def fetch_articles(
    pending_article_jobs: List[models.ArticleJob],
):
    tasks: List[Awaitable] = []
    async with async_session() as db_session:
        for article_job in pending_article_jobs:
            article_job = await article_crud.update_article_job(
                article_job_id=article_job.id,
                article_job_update=schemas.ArticleJobUpdate(
                    status=schemas.ArticleJobStatus.processing
                ),
            )
            db_feed = await feed_crud.get_feed(
                db_session=db_session, feed_id=article_job.feed_id
            )
            async with RateLimiter(article_job.url):
                tasks.append(
                    fetch_article(
                        article_job=article_job,
                        match_rules=db_feed.rules,
                    )
                )
    return await asyncio.gather(*tasks)


async def fetch_pending_articles():
    """
    Fetch pending article jobs

    The method first checks to determine that there are no currently
    processing article jobs.
    """
    pending_article_jobs = None
    async with async_session() as db_session:
        if not await article_crud.get_article_jobs_by_status(
            db_session=db_session, status=schemas.ArticleJobStatus.processing
        ):
            pending_article_jobs = await article_crud.get_pending_article_jobs(
                db_session=db_session
            )

        if pending_article_jobs:
            logger.info(f"fetching {len(pending_article_jobs)} articles")
            await fetch_articles(
                pending_article_jobs=pending_article_jobs,
            )
        else:
            logger.info("No pending articles")
