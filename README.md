# CryptoMonitor

TODO

## Improvements

## Usage
```
$ cd infrasctucture
$ docker-compose up -d
$ docker-compose logs -f api
```

* API: [http://localhost:8000](http://localhost:8000)
* Interactive swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
* Adminer: [http://localhost:8080](http://localhost:8080):
    * server: postgres 
    * username:postgres 
    * password:password 
    * database: cryptomonitor




# Notes

This would suit a serverless deployment.

Needs tests are incomplete.

I am not handling migrations (e.g. with Alembic)

Async parallelism could be maximised by using window query inget pending jobs


There is a known issue with aiohttp https://github.com/aio-libs/aiohttp/issues/4282