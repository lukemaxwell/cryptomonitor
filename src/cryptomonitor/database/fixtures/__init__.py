from cryptomonitor import schemas
from cryptomonitor.database import async_session
from cryptomonitor.database.crud import feed as feed_crud


async def add_fixtures():
    async with async_session() as db_session:
        feed_1 = schemas.FeedCreate(
            name="Blockworks",
            url="https://blockworks.co/feed/",
            rules=[
                schemas.RuleCreate(
                    name="hacks-vulns", pattern=".*((hack)|(exploit)|(vuln)).*"
                ),
                schemas.RuleCreate(
                    name="coinbase-binance-listings",
                    pattern=".*((Coinbase)|(Binance)).*list.*",
                ),
                schemas.RuleCreate(
                    name="eth-forks-upgrades",
                    pattern=".*((Ethereum)|(ETH)).*((fork)|(upgrad)).*",
                ),
            ],
        )
        await feed_crud.create_feed_with_rules(db_session=db_session, feed=feed_1)
        feed_2 = schemas.FeedCreate(
            name="Cryptopotato",
            url="https://cryptopotato.com/feed/",
            rules=[
                schemas.RuleCreate(
                    name="hacks-vulns", pattern=".*((hack)|(exploit)|(vuln)).*"
                ),
                schemas.RuleCreate(
                    name="coinbase-binance-listings",
                    pattern=".*((Coinbase)|(Binance)).*list.*",
                ),
                schemas.RuleCreate(
                    name="eth-forks-upgrades",
                    pattern=".*((Ethereum)|(ETH)).*((fork)|(upgrad)).*",
                ),
            ],
        )
        await feed_crud.create_feed_with_rules(db_session=db_session, feed=feed_2)
        feed_3 = schemas.FeedCreate(
            name="Cryptobriefing",
            url="https://cryptobriefing.com/feed/",
            rules=[
                schemas.RuleCreate(
                    name="hacks-vulns", pattern=".*((hack)|(exploit)|(vuln)).*"
                ),
                schemas.RuleCreate(
                    name="coinbase-binance-listings",
                    pattern=".*((Coinbase)|(Binance)).*list.*",
                ),
                schemas.RuleCreate(
                    name="eth-forks-upgrades",
                    pattern=".*((Ethereum)|(ETH)).*((fork)|(upgrad)).*",
                ),
            ],
        )
        await feed_crud.create_feed_with_rules(db_session=db_session, feed=feed_3)
        feed_4 = schemas.FeedCreate(
            name="Dailyhodl",
            url="https://dailyhodl.com/feed/",
            rules=[
                schemas.RuleCreate(
                    name="hacks-vulns", pattern=".*((hack)|(exploit)|(vuln)).*"
                ),
                schemas.RuleCreate(
                    name="coinbase-binance-listings",
                    pattern=".*((Coinbase)|(Binance)).*list.*",
                ),
                schemas.RuleCreate(
                    name="eth-forks-upgrades",
                    pattern=".*((Ethereum)|(ETH)).*((fork)|(upgrad)).*",
                ),
            ],
        )
        await feed_crud.create_feed_with_rules(db_session=db_session, feed=feed_4)
        feed_5 = schemas.FeedCreate(
            name="Cointelegraph",
            url="https://cointelegraph.com/rss",
            rules=[
                schemas.RuleCreate(
                    name="hacks-vulns", pattern=".*((hack)|(exploit)|(vuln)).*"
                ),
                schemas.RuleCreate(
                    name="coinbase-binance-listings",
                    pattern=".*((Coinbase)|(Binance)).*list.*",
                ),
                schemas.RuleCreate(
                    name="eth-forks-upgrades",
                    pattern=".*((Ethereum)|(ETH)).*((fork)|(upgrad)).*",
                ),
            ],
        )
        await feed_crud.create_feed_with_rules(db_session=db_session, feed=feed_5)
        feed_6 = schemas.FeedCreate(
            name="Decrypt",
            url="https://decrypt.co/feed",
            rules=[
                schemas.RuleCreate(
                    name="hacks-vulns", pattern=".*((hack)|(exploit)|(vuln)).*"
                ),
                schemas.RuleCreate(
                    name="coinbase-binance-listings",
                    pattern=".*((Coinbase)|(Binance)).*list.*",
                ),
                schemas.RuleCreate(
                    name="eth-forks-upgrades",
                    pattern=".*((Ethereum)|(ETH)).*((fork)|(upgrad)).*",
                ),
            ],
        )
        await feed_crud.create_feed_with_rules(db_session=db_session, feed=feed_6)
