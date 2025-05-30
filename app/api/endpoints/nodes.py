from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.node_repository import node_repository
from app.exceptions.db_entry_creation_exception import DBEntryCreationException
from app.exceptions.data_base_exception import DataBaseException
from app.exceptions.db_entry_update_exception import DBEntryUpdateException
from app.exceptions.db_entry_deletion_exception import DBEntryDeletionException
from app.exceptions.db_entry_not_found_exception import DBEntryNotFoundException

router = APIRouter()

@router.get("/", response_model=List[NodeResponse])
async def get_nodes(
    node_id: UUID = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve one or all nodes.

    Args:
        node_id (UUID, optional): If provided, fetches the node with this ID.
                                 If not, returns all nodes.
        db (AsyncSession): Database session dependency.

    Returns:
        List[NodeResponse]: A list of node responses.

    Raises:
        HTTPException: If there is an error retrieving nodes.
    """
    try:
        nodes = await node_repository.get_nodes(db, node_id)
        return nodes
    except DBEntryNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except DataBaseException as e:
        if e.details.get("error_type") == "database_connection_error":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error occurred"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while retrieving nodes"
            )

@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: UUID,
    updates: NodeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing node.

    Args:
        node_id (UUID): ID of the node to update.
        updates (NodeUpdate): The update data for the node.
        db (AsyncSession): Database session dependency.

    Returns:
        NodeResponse: The updated node.

    Raises:
        HTTPException: If there is an error updating the node.
    """
    try:
        updated_node = await node_repository.update_node(db, node_id, updates.model_dump(exclude_unset=True))
        return updated_node
    except DBEntryNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except DBEntryUpdateException as e:
        if e.details.get("error_type") == "database_connection_error":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error occurred"
            )
        elif e.details.get("error_type") == "database_integrity_error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid update data provided"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the node"
            )

@router.delete("/{node_id}")
async def delete_node(
    node_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a node.

    Args:
        node_id (UUID): ID of the node to delete.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A dictionary confirming the deletion by ID.

    Raises:
        HTTPException: If there is an error deleting the node.
    """
    try:
        result = await node_repository.delete_node(db, node_id)
        return result
    except DBEntryNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except DBEntryDeletionException as e:
        if e.details.get("error_type") == "database_connection_error":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error occurred"
            )
        elif e.details.get("error_type") == "database_integrity_error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete node due to existing references"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the node"
            )

@router.get("/{node_id}", response_model=NodeResponse)
async def get_node_by_id(
    node_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a node by its ID.

    Args:
        node_id (UUID): ID of the node to retrieve.
        db (AsyncSession): Database session dependency.

    Returns:
        NodeResponse: The retrieved node.

    Raises:
        HTTPException: If there is an error retrieving the node.
    """
    try:
        node = await node_repository.get_node_by_id(db, node_id)
        return node
    except DBEntryNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except DataBaseException as e:
        if e.details.get("error_type") == "database_connection_error":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error occurred"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while retrieving the node"
            ) 