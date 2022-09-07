from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from cryptomonitor import schemas
from cryptomonitor.database import models


async def get_rule(db_session: AsyncSession, rule_id: int):
    result = await db_session.execute(
        select(models.Rule).where(models.Rule.id == rule_id).first()
    )
    return result.scalars().all()


async def get_rule_by_pattern(db_session: AsyncSession, pattern: str):
    result = await db_session.execute(
        select(models.Rule).where(models.Rule.pattern == pattern)
    )
    return result.scalars().one()


async def get_rules(db_session: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db_session.execute(select(models.Rule).offset(skip).limit(limit))
    return result.scalars().all()


async def create_rule(db_session: AsyncSession, rule: schemas.RuleCreate):
    db_rule = models.Rule(name=rule.name, pattern=rule.pattern)
    db_session.add(db_rule)
    await db_session.commit()
    await db_session.refresh(db_rule)
    return db_rule


async def get_or_create_rule(db_session: AsyncSession, rule: schemas.RuleCreate):
    try:
        db_rule = await get_rule_by_pattern(db_session=db_session, pattern=rule.pattern)
    except NoResultFound:
        db_rule = await create_rule(db_session=db_session, rule=rule)
    return db_rule
