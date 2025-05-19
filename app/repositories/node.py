"""
CRUD operations for managing nodes in the database.
This module provides functions to create, read, update, and delete nodes.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.node import Node
from app.schemas.node import NodeCreate


# pylint: disable=invalid-name
async def create_node(db: AsyncSession, data: NodeCreate):
    """
    Create a new node entry in the database.

    Args:
        db (AsyncSession): The database session.
        data (NodeCreate): The data for creating the node.

    Returns:
        Node: The created node object after committing to the database.
    """
    node = Node(**data.dict())
    db.add(node)
    await db.commit()
    await db.refresh(node)
    return node


async def get_nodes(db: AsyncSession, node_id: int = None):
    """
    Retrieve one or all nodes from the database.

    Args:
        db (AsyncSession): The database session.
        node_id (int, optional): If provided, fetches the node with this ID.
                                 If not, returns all nodes.

    Returns:
        list[Node]: A list of node objects, or a single-node list if node_id is given.
    """
    if node_id:
        query = select(Node).where(Node.id == node_id)
    else:
        query = select(Node)
    result = await db.execute(query)
    return result.scalars().all()


async def update_node(db: AsyncSession, node_id: int, updates: dict):
    """
    Update an existing node with new values.

    Args:
        db (AsyncSession): The database session.
        node_id (int): ID of the node to be updated.
        updates (dict): Dictionary of fields to update.

    Returns:
        Node | None: The updated node object, or None if not found.
    """
    await db.execute(update(Node).where(Node.id == node_id).values(**updates))
    await db.commit()
    query = select(Node).where(Node.id == node_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def delete_node(db: AsyncSession, node_id: int):
    """
    Delete a node from the database.

    Args:
        db (AsyncSession): The database session.
        node_id (int): ID of the node to be deleted.

    Returns:
        dict: A dictionary confirming the deletion by ID.
    """
    await db.execute(delete(Node).where(Node.id == node_id))
    await db.commit()
    return {"deleted_id": node_id}


async def get_node_by_id(db: AsyncSession, node_id: int):
    """
        Get a node from the database.

        Args:
            db (AsyncSession): The database session.
            node_id (int): ID of the node to be deleted.

        Returns:
            int: ...
        """
    result = await db.execute(select(Node).where(Node.id == node_id))
    return result.scalar_one_or_none()
