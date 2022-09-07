from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from cryptomonitor.database import Base


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)
    _updated = Column(DateTime, onupdate=func.now(), nullable=True)
    last_updated = Column(DateTime, nullable=True)
    last_article_date = Column(DateTime, nullable=True)
    rules = relationship(
        "Rule", secondary="feed_rules", back_populates="feeds", lazy="selectin"
    )


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    pattern = Column(String, index=True, unique=True)
    feeds = relationship("Feed", secondary="feed_rules", back_populates="rules")
    articles = relationship(
        "Article", secondary="article_rules", back_populates="rules"
    )


class FeedRule(Base):
    __tablename__ = "feed_rules"

    feed_id = Column(Integer, ForeignKey("feeds.id"), primary_key=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), primary_key=True)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    body = Column(String)
    url = Column(String)
    published = Column(DateTime)
    rules = relationship(
        "Rule", secondary="article_rules", back_populates="articles", lazy="selectin"
    )
    feed_id = Column(Integer, ForeignKey("feeds.id"), index=True)


class ArticleRule(Base):
    __tablename__ = "article_rules"

    article_id = Column(Integer, ForeignKey("articles.id"), primary_key=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), primary_key=True)


class ArticleJob(Base):
    __tablename__ = "article_jobs"
    id = Column(Integer, primary_key=True)
    _updated = Column(DateTime, onupdate=func.now(), nullable=True)
    title = Column(String)
    url = Column(String, unique=True)
    published = Column(DateTime)
    feed_id = Column(Integer, ForeignKey("feeds.id"), index=True)
    status = Column(String)
