"""
CRUD operations for managing nodes in the database.
This module provides functions to create, read, update, and delete nodes.
"""
import logging
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.node import Node
from app.schemas.node import NodeCreate
from app.utils.exceptions import DBEntryCreationException, DataBaseException, DBEntryUpdateException, \
    DBEntryDeletionException, DBEntryNotFoundException

# Configure logger
logger = logging.getLogger(__name__)


async def create_node(db: AsyncSession, data: NodeCreate):
    """
    Create a new node entry in the database.

    Args:
        db (AsyncSession): The database session.
        data (NodeCreate): The data for creating the node.

    Returns:
        Node: The created node object after committing to the database.

    Raises:
        DBEntryCreationException: If there is an error during node creation.
    """
    try:
        node = Node(**data.model_dump())
        db.add(node)
        await db.commit()
        await db.refresh(node)
        logger.info(f"Successfully created node: {data.name}")
        return node
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error while creating node {data.name}: {str(e)}")
        raise DBEntryCreationException(
            message=f"Failed to create node '{data.name}': Data constraint violation",
            details={
                "error_type": "database_integrity_error",
                "error": str(e)
            }
        )
    except OperationalError as e:
        await db.rollback()
        logger.error(f"Database operational error while creating node {data.name}: {str(e)}")
        raise DBEntryCreationException(
            message=f"Failed to create node '{data.name}': Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(e)
            }
        )
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while creating node {data.name}: {str(e)}")
        raise DBEntryCreationException(
            message=f"Failed to create node '{data.name}': Database error",
            details={
                "error_type": "database_error",
                "error": str(e)
            }
        )


async def get_nodes(db: AsyncSession, node_id: UUID = None):
    """
    Retrieve one or all nodes from the database.

    Args:
        db (AsyncSession): The database session.
        node_id (UUID, optional): If provided, fetches the node with this ID.
                                 If not, returns all nodes.

    Returns:
        list[Node]: A list of node objects, or a single-node list if node_id is given.

    Raises:
        DBEntryNotFoundException: If the specified node is not found.
        DataBaseException: If there is a database error during retrieval.
    """
    try:
        if node_id:
            query = select(Node).where(Node.id == node_id)
        else:
            query = select(Node)
        result = await db.execute(query)
        nodes = result.scalars().all()
        
        if node_id and not nodes:
            logger.warning(f"Node with ID {node_id} not found")
            raise DBEntryNotFoundException(
                message=f"Node with ID {node_id} not found",
                details={
                    "error_type": "not_found_error",
                    "node_id": str(node_id)
                }
            )
            
        logger.info(f"Successfully retrieved {'node' if node_id else 'all nodes'}")
        return nodes
    except OperationalError as e:
        logger.error(f"Database operational error while retrieving nodes: {str(e)}")
        raise DataBaseException(
            message="Failed to retrieve nodes: Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(e)
            }
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving nodes: {str(e)}")
        raise DataBaseException(
            message="Failed to retrieve nodes: Database error",
            details={
                "error_type": "database_error",
                "error": str(e)
            }
        )


async def update_node(db: AsyncSession, node_id: UUID, updates: dict):
    """
    Update an existing node with new values.

    Args:
        db (AsyncSession): The database session.
        node_id (UUID): ID of the node to be updated.
        updates (dict): Dictionary of fields to update.

    Returns:
        Node: The updated node object.

    Raises:
        DBEntryNotFoundException: If the node is not found.
        DBEntryUpdateException: If there is a database error during update.
    """
    try:
        # First check if node exists
        existing_node = await get_node_by_id(db, node_id)
        if not existing_node:
            logger.warning(f"Node with ID {node_id} not found for update")
            raise DBEntryNotFoundException(
                message=f"Node with ID {node_id} not found",
                details={
                    "error_type": "not_found_error",
                    "node_id": str(node_id)
                }
            )

        # Perform the update
        await db.execute(update(Node).where(Node.id == node_id).values(**updates))
        await db.commit()
        
        # Fetch and return the updated node
        query = select(Node).where(Node.id == node_id)
        result = await db.execute(query)
        updated_node = result.scalar_one_or_none()
        
        logger.info(f"Successfully updated node with ID {node_id}")
        return updated_node

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error while updating node {node_id}: {str(e)}")
        raise DBEntryUpdateException(
            message=f"Failed to update node {node_id}: Data constraint violation",
            details={
                "error_type": "database_integrity_error",
                "error": str(e),
                "node_id": str(node_id)
            }
        )
    except OperationalError as e:
        await db.rollback()
        logger.error(f"Database operational error while updating node {node_id}: {str(e)}")
        raise DBEntryUpdateException(
            message=f"Failed to update node {node_id}: Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(e),
                "node_id": str(node_id)
            }
        )
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while updating node {node_id}: {str(e)}")
        raise DBEntryUpdateException(
            message=f"Failed to update node {node_id}: Database error",
            details={
                "error_type": "database_error",
                "error": str(e),
                "node_id": str(node_id)
            }
        )


async def delete_node(db: AsyncSession, node_id: UUID):
    """
    Delete a node from the database.

    Args:
        db (AsyncSession): The database session.
        node_id (UUID): ID of the node to be deleted.

    Returns:
        dict: A dictionary confirming the deletion by ID.

    Raises:
        DBEntryNotFoundException: If the node is not found.
        DBEntryDeletionException: If there is a database error during deletion.
    """
    try:
        # First check if node exists
        existing_node = await get_node_by_id(db, node_id)
        if existing_node:
            # Perform the deletion
            await db.execute(delete(Node).where(Node.id == node_id))
            await db.commit()
            
            logger.info(f"Successfully deleted node with ID {node_id}")
            return {"deleted_id": node_id}

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error while deleting node {node_id}: {str(e)}")
        raise DBEntryDeletionException(
            message=f"Failed to delete node {node_id}: Data constraint violation",
            details={
                "error_type": "database_integrity_error",
                "error": str(e),
                "node_id": str(node_id)
            }
        )
    except OperationalError as e:
        await db.rollback()
        logger.error(f"Database operational error while deleting node {node_id}: {str(e)}")
        raise DBEntryDeletionException(
            message=f"Failed to delete node {node_id}: Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(e),
                "node_id": str(node_id)
            }
        )
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while deleting node {node_id}: {str(e)}")
        raise DBEntryDeletionException(
            message=f"Failed to delete node {node_id}: Database error",
            details={
                "error_type": "database_error",
                "error": str(e),
                "node_id": str(node_id)
            }
        )


async def get_node_by_id(db: AsyncSession, node_id: UUID):
    """
    Get a node from the database by its ID.

    Args:
        db (AsyncSession): The database session.
        node_id (UUID): ID of the node to retrieve.

    Returns:
        Node: The retrieved node object.

    Raises:
        DBEntryNotFoundException: If the node is not found.
        DataBaseException: If there is a database error during retrieval.
    """
    try:
        result = await db.execute(select(Node).where(Node.id == node_id))
        node = result.scalar_one_or_none()
        
        if not node:
            logger.warning(f"Node with ID {node_id} not found")
            raise DBEntryNotFoundException(
                message=f"Node with ID {node_id} not found",
                details={
                    "error_type": "not_found_error",
                    "node_id": str(node_id)
                }
            )
            
        logger.info(f"Successfully retrieved node with ID {node_id}")
        return node

    except OperationalError as e:
        logger.error(f"Database operational error while retrieving node {node_id}: {str(e)}")
        raise DataBaseException(
            message=f"Failed to retrieve node {node_id}: Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(e),
                "node_id": str(node_id)
            }
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving node {node_id}: {str(e)}")
        raise DataBaseException(
            message=f"Failed to retrieve node {node_id}: Database error",
            details={
                "error_type": "database_error",
                "error": str(e),
                "node_id": str(node_id)
            }
        )
