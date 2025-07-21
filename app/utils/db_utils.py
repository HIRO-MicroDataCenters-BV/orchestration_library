"""DB utility functions for handling database operations."""
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


async def delete_and_commit(db: AsyncSession, obj):
    """
    Delete an object from the database and commit the transaction.

    Args:
        db (AsyncSession): SQLAlchemy async session.
        obj: The SQLAlchemy model instance to delete.

    Returns:
        None
    """
    await db.delete(obj)
    await db.commit()
    return obj


async def handle_db_exception(
    exc, db_session, logger, exception_details=None, custom_exception_cls=None
):
    """
    Handle database exceptions by rolling back the session and logging the error.
    Args:
        exc (Exception): The exception that was raised.
        db_session (AsyncSession): The SQLAlchemy async session to rollback.
        logger (logging.Logger): Logger instance to log the error.
        error_type (str): Type of the error for logging and exception details.
        message (str): Custom message for the exception.
        details (dict, optional): Additional details to include in the exception.
        exception_cls (Exception, optional): Custom exception class to raise.
    """
    await db_session.rollback()
    message = (
        exception_details.get("message", "Database operation failed")
        if exception_details
        else "Database operation failed"
    )
    logger.error("%s: %s", message, str(exc))
    if custom_exception_cls:
        raise custom_exception_cls(
            message=message,
            details={**(exception_details or {})},
        ) from exc
    raise exc
