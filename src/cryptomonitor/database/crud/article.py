from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from cryptomonitor.listener import global_listener
from cryptomonitor import schemas
from cryptomonitor.database import async_session, models


async def get_article(db_session: AsyncSession, article_id: int):
    """
    Get article identified by `article_id`
    """
    result = await db_session.execute(
        select(models.Article).where(models.Article.id == article_id)
    )
    return result.scalars().first()


async def get_articles(db_session: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Get articles
    """
    result = await db_session.execute(select(models.Article).offset(skip).limit(limit))
    return result.scalars().all()


async def create_article(db_session: AsyncSession, article: schemas.ArticleCreate):
    db_article = models.Article(
        title=article.title,
        published=article.published,
        url=article.url,
        feed_id=article.feed_id,
        body=article.body,
    )
    db_session.add(db_article)
    await db_session.commit()
    await db_session.refresh(db_article)
    await create_article_rules(
        db_session=db_session, rules=article.rules, article_id=db_article.id
    )
    await global_listener.receive_and_publish_message(db_article.to_dict())
    return db_article


async def create_article_rule(db_session: AsyncSession, article_id: int, rule_id: int):
    db_article_rule = models.ArticleRule(article_id=article_id, rule_id=rule_id)
    db_session.add(db_article_rule)
    await db_session.commit()
    await db_session.refresh(db_article_rule)
    return db_article_rule


async def create_article_rules(
    db_session: AsyncSession, article_id: int, rules: List[schemas.Rule]
):
    db_article_rules: List[models.ArticleRule] = []
    for rule in rules:
        db_article_rule = await create_article_rule(
            db_session=db_session, article_id=article_id, rule_id=rule.id
        )
        db_article_rules.append(db_article_rule)
    return db_article_rules


async def create_article_job(
    db_session: AsyncSession, article_job: schemas.ArticleJobCreate
):
    db_article_job = models.ArticleJob(
        title=article_job.title,
        published=article_job.published,
        url=article_job.url,
        feed_id=article_job.feed_id,
        status=article_job.status,
    )
    db_session.add(db_article_job)
    await db_session.commit()
    await db_session.refresh(db_article_job)
    return db_article_job


async def get_article_job(db_session: AsyncSession, article_job_id: int):
    """
    Get feed identified by `article_job_id`
    """
    result = await db_session.execute(
        select(models.ArticleJob).where(models.ArticleJob.id == article_job_id)
    )
    return result.scalars().first()


async def get_article_jobs(db_session: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Get article jobs
    """
    result = await db_session.execute(
        select(models.ArticleJob).order_by(models.ArticleJob._updated).limit(limit)
    )
    return result.scalars().all()


async def get_pending_article_jobs(db_session: AsyncSession, limit: int = 10):
    """
    Get pending article jobs

    TODO: use window query to get n rows per feed id
    This would be superior to the rate limiter as it would minimise
    rate limiting and maximise the number of async requests that could be
    made in parallel
    """
    return await get_article_jobs_by_status(
        db_session=db_session, status=schemas.ArticleJobStatus.pending
    )


async def get_article_jobs_by_status(
    db_session: AsyncSession, status=schemas.ArticleJobStatus, limit: int = 10
):
    """
    Get article jobs by status
    """
    result = await db_session.execute(
        select(models.ArticleJob)
        .where(models.ArticleJob.status == status)
        .order_by(models.ArticleJob._updated)
        .limit(limit)
    )
    return result.scalars().all()


async def update_article_job(
    article_job_id: models.Feed,
    article_job_update: schemas.FeedUpdate,
) -> models.ArticleJob:
    """
    Update an article job
    """
    async with async_session() as db_session:
        db_article_job: models.ArticleJob = await get_article_job(
            db_session=db_session, article_job_id=article_job_id
        )
        db_article_job.status = article_job_update.status
        await db_session.commit()
        await db_session.refresh(db_article_job)
        return db_article_job
