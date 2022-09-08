# Cryptomonitor
Cryptomonitor is a demo application designed to monitor crypto news feeds in real time and store articles that match configurable rules.

The application is built using FastAPI and SQLAlchemy (async). 
It checks for new feed content every 10 seconds using a FastAPI background task.

If articles must be fetched from the source website they are queued in the database as ArticleJobs.

Article jobs are checked every 10 seconds using a seperate background task and articles are fetched in rate limited fashion (no more than 1 request per host every 5 seconds).

Feeds and rules can be configured using the API, and article body is printed to stdout and the json format can be retrieved using the articles API endpoint, or via the websocket.

The article job queue can also be viewed via the API.


## Improvements

### Architecture
This is small self-contained application used for the purposes of demonstration, and to see what can be done with FastAPI background tasks. However, doing this volume of background work on the same thread as the server is unwise. 

There are various options for improvement which were out of scope for this example.

1. Run the feed and article tasks in separate containers. There is an example of this in the docker-compose file. It is a very small improvement and would break the websocket (as the websocket listener is run by the API). An easy fix for this would be to have the article task use the API endpoint to create articles. Slightly more robust, would work with ECS/EKS.

2. Use proper background workers for the task collection, e.g. celery. Much more rebust and better for ongoing collection and debug. At this point the benefit of asynchrounous web request would begin to diminish (or simply add unwanted debug complexity). 

3. Use a hybrid serverless solution where feed and article tasks are offloaded to lambdas for parallel procesing. Similar benefits to above with opportunity for greater parallelism. 

4. Use a fully serverless approach using http gateway, api gateway, SNS/SQS queues and triggers. Scales to large volume of data collection and allows full range of aws services, however would require significant changes to the code. 

## Usage
```
$ cd infrastructure
$ docker-compose up -d
$ docker-compose logs -f api
```

* API: [http://localhost:8000](http://localhost:8000)
* Interactive swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
* Adminer: [http://localhost:8080](http://localhost:8080)
    * server: postgres 
    * username:postgres 
    * password:password 
    * database: cryptomonitor
* Websocket: ws://localhost:8000/ws

# Notes

Needs a lot more error handling. 

Needs tests.

There is no housekeeping of the article job queue. If there are issues or the db is
closed while tasks are running, the article jobs may be stuck in processing state and the task will no longer collect. A cleanup task could be created to take care of stale article jobs.

There are no db migrations (e.g. with Alembic).

The collection of articles is inefficient. Async parallelism could be maximised by using window query to get pending jobs. See [here](src/cryptomonitor/database/crud/article.py#103).

There is a runtime warning from aiohttp visible in the logs. This appears to be a known issue with aiohttp https://github.com/aio-libs/aiohttp/issues/4282

Probabably a lot of undiscovered bugs (this was written in a short space of time).
