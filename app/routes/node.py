from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from app import schemas
from app.crud import node
from fastapi import HTTPException

router = APIRouter(prefix="/node")


@router.post("/", response_model=schemas.NodeResponse)
async def create_node(
    data: schemas.NodeCreate, db: AsyncSession = Depends(get_async_db)
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


@router.get("/", response_model=list[schemas.NodeResponse])
async def get_nodes(db: AsyncSession = Depends(get_async_db)):
    return await node.get_nodes(db)


@router.get("/{node_id}", response_model=schemas.NodeResponse)
async def get_node_by_id(node_id: int):
    nodes = await get_nodes()  # Or however you fetch nodes
    for node_ in nodes:
        if node_["id"] == node_id:
            return node_
    # Return an actual error, not a dict
    raise HTTPException(status_code=404, detail="Node not found")


@router.put("/{node_id}", response_model=schemas.NodeResponse)
async def update_node(
    node_id: int, data: schemas.NodeUpdate, db: AsyncSession = Depends(get_async_db)
):
    return await node.update_node(db, node_id, updates=data.dict(exclude_unset=True))


@router.delete("/{node_id}")
async def delete_node(node_id: int, db: AsyncSession = Depends(get_async_db)):
    await node.delete_node(db, node_id)
    return {"detail": "Node deleted successfully"}
