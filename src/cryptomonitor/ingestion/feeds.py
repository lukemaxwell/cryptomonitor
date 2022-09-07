import asyncio
import logging
from datetime import datetime
from time import mktime
from typing import Awaitable, List

import aiohttp
import feedparser

from cryptomonitor import schemas
from cryptomonitor.config import HEADERS
from cryptomonitor.database import async_session, models
from cryptomonitor.database.crud import feed as feed_crud
from cryptomonitor.ingestion import parser

logger = logging.getLogger(__name__)


async def create_feed_update(
    parsed_feed: feedparser.FeedParserDict, last_article_date: datetime
) -> schemas.FeedUpdate:
    return schemas.FeedUpdate(
        last_updated=datetime.fromtimestamp(mktime(parsed_feed.feed.updated_parsed)),
        last_article_date=last_article_date or datetime(1970, 1, 1),
    )


async def fetch_feed(http_session: aiohttp.ClientSession, feed: models.Feed):
    async with async_session() as db_session:
        async with http_session.get(
            feed.url, raise_for_status=True, headers=HEADERS
        ) as response:
            logger.info(f"Got feed {feed.url}")
            parsed_feed = feedparser.parse(await response.text())
            if is_updated_feed(feed=feed, parsed_feed=parsed_feed):
                feed_update = await create_feed_update(
                    parsed_feed=parsed_feed, last_article_date=feed.last_article_date
                )
                await parser.parse_entries(
                    db_session=db_session, feed=feed, parsed_feed=parsed_feed
                )
                last_entry_date = parser.parse_last_entry_date(parsed_feed.entries)

                if last_entry_date > feed_update.last_article_date:
                    feed_update.last_article_date = last_entry_date

                await feed_crud.update_feed(feed_id=feed.id, feed_update=feed_update)


async def fetch_feeds(
    http_session: aiohttp.ClientSession,
    pending_feeds: List[models.Feed],
):
    tasks: List[Awaitable] = []
    for feed in pending_feeds:
        tasks.append(fetch_feed(http_session=http_session, feed=feed))
    return await asyncio.gather(*tasks)
    # return await asyncio.gather(*tasks, return_exceptions=True)


def is_updated_feed(feed: models.Feed, parsed_feed: feedparser.FeedParserDict):
    feed_updated = datetime.fromtimestamp(mktime(parsed_feed.feed.updated_parsed))
    return feed.last_updated is None or feed_updated > feed.last_updated


# async def fetch_articles(
#     feed: models.Feed,
#     parsed_feed: feedparser.FeedParserDict,
# ) -> List[schemas.ArticleCreate]:
#     """
#     Return feed entries published after `feed.last_article_date`.
#     """
#     async with async_session() as db_session:
#         if is_new_feed_version(feed=feed, parsed_feed=parsed_feed):
#             feed_update = schemas.FeedUpdate(
#                 last_updated=datetime.fromtimestamp(
#                     mktime(parsed_feed.feed.updated_parsed)
#                 ),
#                 last_article_date=feed.last_article_date or datetime(1970, 1, 1),
#             )
#             last_article_date = feed_update.last_article_date
#             for entry in parsed_feed["entries"]:
#                 article_published = datetime.fromtimestamp(
#                     mktime(entry.published_parsed)
#                 )
#                 if is_new_article(feed=feed, entry=entry):
#                     if article_published > last_article_date:
#                         last_article_date = article_published
#                     if "content" not in entry:
#                         article_job = article_job_from_entry(feed=feed, entry=entry)

#                         try:
#                             await article_crud.create_article_job(
#                                 db_session=db_session, article_job=article_job
#                             )
#                             logger.info(f"Queued article job for {entry['link']}")
#                         except IntegrityError:
#                             logger.info(
#                                 f"Article job already exists for {entry['link']}"
#                             )
#                             await db_session.rollback()
#                     else:
#                         article = article_from_entry(feed=feed, entry=entry)

#                         if len(article.rules) > 0:
#                             db_article = await article_crud.create_article(
#                                 db_session=db_session, article=article
#                             )
#                             print(db_article.body)

#             if last_article_date > feed_update.last_article_date:
#                 feed_update.last_article_date = last_article_date

#             await feed_crud.update_feed(feed_id=feed.id, feed_update=feed_update)


# async def fetch_pending_feeds(db_session: AsyncSession):
async def fetch_pending_feeds():
    """
    Fetch feed items for all pending feeds
    """
    pending_feeds = None
    async with async_session() as db_session:
        pending_feeds = await feed_crud.get_feeds(db_session=db_session)
        logger.info(f"Pending feeds: {len(pending_feeds)}")

    if pending_feeds:
        async with aiohttp.ClientSession() as http_session:
            await fetch_feeds(
                http_session=http_session,
                pending_feeds=pending_feeds,
            )
