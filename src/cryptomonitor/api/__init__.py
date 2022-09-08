import asyncio

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from cryptomonitor import schemas
from cryptomonitor.database import engine, fixtures, get_session, models
from cryptomonitor.database.crud import article as article_crud
from cryptomonitor.database.crud import feed as feed_crud
from cryptomonitor.database.crud import rule as rule_crud
from cryptomonitor.ingestion import articles, feeds, task_runner
from cryptomonitor.listener import global_listener

app = FastAPI()


@app.on_event("startup")
async def app_startup():
    # Create db tables
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)

    # Add fixtures
    await fixtures.add_fixtures()

    # Start event listener
    await global_listener.start_listening()

    # Uncomment to run ingestion run using fastapi background tasks,
    # DO NOT RUN 'feed' and 'article' docker containers when doing so
    # Not that it is ideal to have long running background tasks tied to your api thread
    #
    asyncio.create_task(task_runner.run(feeds.fetch_pending_feeds))
    asyncio.create_task(task_runner.run(articles.fetch_pending_articles))


@app.on_event("shutdown")
async def app_shutdown():
    await global_listener.stop_listening()


@app.post("/feeds/", response_model=schemas.Feed)
async def create_feed(
    feed: schemas.FeedCreate, db: AsyncSession = Depends(get_session)
):
    db_feed = await feed_crud.get_feed_by_url(db, url=feed.url)
    if db_feed:
        raise HTTPException(status_code=400, detail="Feed URL already registered")
    return await feed_crud.create_feed(db_session=db, feed=feed)


@app.get("/feeds/", response_model=list[schemas.Feed])
async def read_feeds(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)
):
    feeds = await feed_crud.get_feeds(db, skip=skip, limit=limit)
    return feeds


@app.get("/feeds/{feed_id}", response_model=schemas.Feed)
async def read_feed(feed_id: int, db: AsyncSession = Depends(get_session)):
    db_feed = await feed_crud.get_feed(db, feed_id=feed_id)
    if db_feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    return db_feed


@app.post("/rules/", response_model=schemas.Rule)
async def create_rule(
    rule: schemas.RuleCreate, db: AsyncSession = Depends(get_session)
):
    db_rule = await rule_crud.get_rule_by_pattern(db, pattern=rule.pattern)
    if db_rule:
        raise HTTPException(status_code=400, detail="Rule pattern already registered")
    return await rule_crud.create_rule(db=db, rule=rule)


@app.get("/rules/", response_model=list[schemas.Rule])
async def read_rules(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)
):
    rules = await rule_crud.get_rules(db, skip=skip, limit=limit)
    return rules


@app.get("/rules/{rule_id}", response_model=schemas.Rule)
async def read_rule(rule_id: int, db: AsyncSession = Depends(get_session)):
    db_rule = await rule_crud.get_rule(db, feed_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return db_rule


@app.get("/articles/{article_id}", response_model=schemas.Article)
async def read_article(article_id: int, db: AsyncSession = Depends(get_session)):
    db_article = await article_crud.get_article(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article


@app.get("/articles/", response_model=list[schemas.Article])
async def read_articles(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)
):
    articles = await article_crud.get_articles(db, skip=skip, limit=limit)
    return articles


@app.get("/article-jobs/", response_model=list[schemas.ArticleJob])
async def read_articles_jobs(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)
):
    article_jobs = await article_crud.get_article_jobs(db, skip=skip, limit=limit)
    return article_jobs


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, response_model=models.Article):
    await websocket.accept()
    q: asyncio.Queue = asyncio.Queue()
    await global_listener.subscribe(q=q)
    try:
        while True:
            data = await q.get()
            await websocket.send_text(jsonable_encoder(data))
    except WebSocketDisconnect:
        return
