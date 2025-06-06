"""Save an object to the database and refresh it. """
from sqlalchemy.ext.asyncio import AsyncSession


async def save_and_refresh(db: AsyncSession, obj):
    """
    Save an object to the database and refresh it.

    Args:
        db (AsyncSession): SQLAlchemy async session.
        obj: The SQLAlchemy model instance to persist.

    Returns:
        The refreshed object after commit.
    """
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj
