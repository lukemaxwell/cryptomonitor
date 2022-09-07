from datetime import datetime, timedelta
from typing import List

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from cryptomonitor import schemas
from cryptomonitor.database import async_session, models
from cryptomonitor.database.crud.rule import get_or_create_rule


async def get_feed(db_session: AsyncSession, feed_id: int):
    """
    Get feed identified by `feed_id`
    """
    result = await db_session.execute(
        select(models.Feed).where(models.Feed.id == feed_id)
    )
    return result.scalars().first()


async def get_feed_by_url(db_session: AsyncSession, url: str):
    """
    Get feed identified by `url`
    """
    result = await db_session.execute(
        select(models.Feed).where(models.Feed.url == url).first()
    )
    return result.scalars().all()


async def get_feeds(db_session: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Get all feeds
    """
    result = await db_session.execute(select(models.Feed).offset(skip).limit(limit))
    return result.scalars().all()


async def get_pending_feeds(db_session: AsyncSession, limit: int = 10):
    """
    Get feeds that should be updated
    """
    result = await db_session.execute(
        select(models.Feed).where(
            or_(
                (models.Feed.last_updated < datetime.now() - timedelta(seconds=30)),
                (models.Feed.last_updated is None),
            )
        )
    )
    return result.scalars().all()


async def create_feed(db_session: AsyncSession, feed: schemas.FeedCreate):
    """
    Create a feed
    """
    db_feed = models.Feed(name=feed.name, url=feed.url)
    db_session.add(db_feed)
    await db_session.commit()
    await db_session.refresh(db_feed)
    return db_feed


async def create_feed_with_rules(db_session: AsyncSession, feed: schemas.FeedCreate):
    """
    Create a feed and associated feed rules
    """
    db_feed: models.Feed = await create_feed(db_session=db_session, feed=feed)
    await create_feed_rules(db_session=db_session, feed_id=db_feed.id, rules=feed.rules)


async def create_feed_rule(db_session: AsyncSession, feed_id: int, rule_id: int):
    """
    Create a feed rule
    """
    db_feed_rule = models.FeedRule(feed_id=feed_id, rule_id=rule_id)
    db_session.add(db_feed_rule)
    await db_session.commit()
    await db_session.refresh(db_feed_rule)
    return db_feed_rule


async def create_feed_rules(
    db_session: AsyncSession, feed_id: int, rules: List[schemas.RuleCreate]
):
    """
    Create feed rules
    """
    db_feed_rules: List[models.FeedRule] = []
    for rule in rules:
        db_rule = await get_or_create_rule(db_session=db_session, rule=rule)
        db_feed_rule = await create_feed_rule(
            db_session=db_session, feed_id=feed_id, rule_id=db_rule.id
        )
        db_feed_rules.append(db_feed_rule)
    return db_feed_rules


async def update_feed(
    feed_id: models.Feed,
    feed_update: schemas.FeedUpdate,
):
    """
    Update a feed
    """
    async with async_session() as db_session:
        db_feed: models.Feed = await get_feed(db_session=db_session, feed_id=feed_id)
        update: bool = False
        if db_feed._updated is None or db_feed._updated < feed_update.last_updated:
            if (
                db_feed.last_updated is None
                or feed_update.last_updated > db_feed.last_updated
            ):
                db_feed.last_updated = feed_update.last_updated
                update = True
            if (
                db_feed.last_article_date is None
                or feed_update.last_article_date > db_feed.last_article_date
            ):
                db_feed.last_article_date = feed_update.last_article_date
                update = True

        if update:
            await db_session.commit()
