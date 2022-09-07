from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, validator


class RuleBase(BaseModel):
    name: str
    pattern: str

    @validator("name")
    def name_non_empty(cls, v):
        assert len(v) > 0
        return v

    @validator("pattern")
    def pattern_non_empty(cls, v):
        assert len(v) > 0
        return v


class RuleCreate(RuleBase):
    pass


class Rule(RuleBase):
    id: int

    class Config:
        orm_mode = True


class FeedBase(BaseModel):
    name: str
    url: str
    rules: List[Rule] = []

    @validator("url")
    def url_non_empty(cls, v):
        assert len(v) > 0
        return v

    @validator("name")
    def name_non_empty(cls, v):
        assert len(v) > 0
        return v


class FeedCreate(FeedBase):
    rules: List[RuleCreate] = []


class Feed(FeedBase):
    id: int

    class Config:
        orm_mode = True


class FeedUpdate(BaseModel):
    last_updated: datetime
    last_article_date: datetime


class ArticleBase(BaseModel):
    title: str
    body: str
    url: str
    feed_id: int
    published: datetime
    rules: List[Rule] = []


class ArticleCreate(ArticleBase):
    pass


class Article(ArticleBase):
    id: int

    class Config:
        orm_mode = True


class ArticleJobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    complete = "complete"
    error = "error"


class ArticleJobBase(BaseModel):
    title: str
    url: str
    feed_id: int
    published: datetime
    status: ArticleJobStatus

    class Config:
        use_enum_values = True


class ArticleJobCreate(ArticleJobBase):
    pass


class ArticleJob(ArticleJobBase):
    id: int

    class Config:
        orm_mode = True


class ArticleJobUpdate(BaseModel):
    status: ArticleJobStatus
