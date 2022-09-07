import asyncio
import logging
from typing import Awaitable

from cryptomonitor.ingestion import articles, feeds

logger = logging.getLogger(__name__)


class TaskRunner:
    def __init__(self):
        self.value = 0

    async def run(self, func: Awaitable):
        try:
            while True:
                await func()
                await asyncio.sleep(10)
                self.value += 1
        except Exception as e:
            logger.error(e)


task_runner = TaskRunner()


if __name__ == "__main__":
    # Used for testing, but this could be an entry point
    # for running as a seperate process, e.g. using supervisor
    import sys

    try:
        task = sys.argv[1]
    except IndexError:
        raise Exception("Provide task argument [feeds, articles]")
    if task == "feeds":
        asyncio.run(task_runner.run(feeds.fetch_pending_feeds))
    elif task == "articles":
        asyncio.run(task_runner.run(articles.fetch_pending_articles))
    else:
        raise Exception("Unrecognized task [feeds, articles]")
