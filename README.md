# CryptoMonitor


# Notes

This would suit a serverless deployment.

Using sqlite has severe limitations, most importantly
the table locking. This was used to make it easy to
demonstrate approach and avoid complex infrastructure so that the application can be easily run (although this could easily be achieved with docker-compose). In a real database should be used in production. Postgres would be a good choice if analysis is to be done however the config models would suit a nosql db like dynamodb.

The api is not async...because sqlalchemy, and sqlite

Tests are incomplete.


I am not handling migrations (e.g. with Alembic)


There is a known issue with aiohttp https://github.com/aio-libs/aiohttp/issues/4282