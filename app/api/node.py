"""
DB node routes.
This module defines the API endpoints for managing nodes in the database.
It includes routes for creating, retrieving, updating, and deleting nodes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.schemas.node import NodeCreate, NodeUpdate, NodeResponse
from app.repositories import node


router = APIRouter(prefix="/node")


# pylint: disable=invalid-name
@router.post("/", response_model=NodeResponse)
async def create_node(
    data: NodeCreate, db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new node.

    Args:
        data (schemas.NodeCreate): Payload containing node creation details.
        db (AsyncSession): Database session dependency.

    Returns:
        schemas.NodeResponse: The created node data.
    """
    return await node.create_node(db, data)


@router.get("/", response_model=list[NodeResponse])
async def get_nodes(db: AsyncSession = Depends(get_async_db)):
    """
    Retrieve all nodes.

    Args:
        db (AsyncSession): Database session dependency.

    Returns:
        list[schemas.NodeResponse]: A list of all available nodes.
    """
    return await node.get_nodes(db)


@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: int, data: NodeUpdate, db: AsyncSession = Depends(get_async_db)
):
    """
    Update an existing node by ID.

    Args:
        node_id (int): The ID of the node to update.
        data (schemas.NodeUpdate): Fields to update.
        db (AsyncSession): Database session dependency.

    Returns:
        schemas.NodeResponse: The updated node data.
    """
    return await node.update_node(db, node_id, updates=data.dict(exclude_unset=True))


@router.delete("/{node_id}")
async def delete_node(node_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Delete a node by ID.

    Args:
        node_id (int): The ID of the node to delete.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A message indicating successful deletion.
    """
    await node.delete_node(db, node_id)
    return {"detail": "Node deleted successfully"}


@router.get("/{node_id}", response_model=NodeResponse)
async def get_node_by_id(node_id: int, db: AsyncSession = Depends(get_async_db)):
    """
        Retrieve a node by its ID.

        Args:
            node_id (int): The ID of the node to fetch.
            db: ...

        Returns:
            schemas.NodeResponse: The node with the given ID.

        Raises:
            HTTPException: If the node with the given ID does not exist.
    """

    node_ = await node.get_node_by_id(db, node_id)
    if not node_:
        raise HTTPException(status_code=404, detail="Node not found")
    return node_
