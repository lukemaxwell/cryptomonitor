import logging
from datetime import datetime
from email import feedparser
from time import mktime
from typing import List

import feedparser
from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cryptomonitor import schemas
from cryptomonitor.database import models
from cryptomonitor.database.crud import article as article_crud
from cryptomonitor.ingestion import rules

logger = logging.getLogger(__name__)


def parse_entry_datetime(entry: feedparser.FeedParserDict) -> datetime:
    """
    Return entry published date as datetime
    """
    return datetime.fromtimestamp(mktime(entry.published_parsed))


async def parse_entry(
    db_session: AsyncSession, feed: models.Feed, entry: feedparser.FeedParserDict
):
    """
    Parse feed entry
    """
    article = parse_article_from_entry(feed=feed, entry=entry)

    if len(article.rules) > 0:
        db_article = await article_crud.create_article(
            db_session=db_session, article=article
        )
        print(db_article.body)


def is_new_entry(entry_date: datetime, last_article_date):
    return last_article_date is None or entry_date > last_article_date


def parse_article_job_from_entry(
    feed: models.Feed, entry: feedparser.FeedParserDict
) -> schemas.ArticleJobCreate:
    return schemas.ArticleJobCreate(
        title=entry.title,
        url=entry.link,
        published=datetime.fromtimestamp(mktime(entry.published_parsed)),
        feed_id=feed.id,
        status=schemas.ArticleJobStatus.pending,
    )


async def create_article_job(
    db_session: AsyncSession, feed: models.Feed, entry: feedparser.FeedParserDict
):
    article_job = parse_article_job_from_entry(feed=feed, entry=entry)
    try:
        await article_crud.create_article_job(
            db_session=db_session, article_job=article_job
        )
        logger.info(f"Queued article job for {entry['link']}")
    except IntegrityError:
        logger.info(f"Article job already exists for {entry['link']}")
        await db_session.rollback()


def parse_html(html: str):
    """
    Extract text content from html
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.find_all(text=True)
    # Remove unwanted tag elements:
    cleaned_text = ""
    blacklist = [
        "[document]",
        "noscript",
        "header",
        "html",
        "meta",
        "head",
        "input",
        "script",
        "style",
    ]
    for item in text:
        if item.parent.name not in blacklist:
            cleaned_text += "{} ".format(item)

    cleaned_text = cleaned_text.replace("\t", "")
    return cleaned_text.strip()


async def parse_article(
    db_session: AsyncSession,
    article_job: schemas.ArticleJob,
    match_rules: List[models.Rule],
    html: str,
):
    body = parse_html(html)
    article = schemas.ArticleCreate(
        title=article_job.title,
        url=article_job.url,
        body=body,
        feed_id=article_job.feed_id,
        published=article_job.published,
        rules=rules.match_rules(match_rules=match_rules, body=body),
    )
    if len(article.rules) > 0:
        db_article = await article_crud.create_article(
            db_session=db_session, article=article
        )
        print(db_article.body)


def parse_last_entry_date(entries: List[feedparser.FeedParserDict]) -> datetime:
    """
    Return last entry date from list of feedparser entries
    """
    last_entry_date = datetime(1970, 1, 1)
    for entry in entries:
        entry_date = parse_entry_datetime(entry)
        if entry_date > last_entry_date:
            last_entry_date = entry_date
    return last_entry_date


async def parse_entries(
    db_session: AsyncSession,
    feed: models.Feed,
    parsed_feed: feedparser.FeedParserDict,
):
    last_article_date = feed.last_article_date
    for entry in parsed_feed["entries"]:
        entry_date = parse_entry_datetime(entry)
        if is_new_entry(entry_date=entry_date, last_article_date=last_article_date):
            last_article_date = entry_date
            if "content" not in entry:
                await create_article_job(db_session=db_session, feed=feed, entry=entry)
            else:
                await parse_entry(db_session=db_session, feed=feed, entry=entry)


def parse_article_from_entry(
    feed: models.Feed, entry: feedparser.FeedParserDict
) -> schemas.ArticleCreate:
    body = parse_html(entry.content[0].value)
    return schemas.ArticleCreate(
        title=entry.title,
        url=entry.link,
        rules=rules.match_rules(match_rules=feed.rules, body=body),
        body=body,
        published=datetime.fromtimestamp(mktime(entry.published_parsed)),
        feed_id=feed.id,
    )
