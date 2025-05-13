from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from app import crud, schemas

router = APIRouter(prefix="/node", tags=["Node"])

@router.post("/", response_model=schemas.NodeResponse)
async def create_node(data: schemas.NodeCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.create_node(db, data)

@router.get("/", response_model=list[schemas.NodeResponse])
async def get_nodes(db: AsyncSession = Depends(get_async_db)):
    return await crud.get_nodes(db)

@router.get("/{node_id}", response_model=schemas.NodeResponse)
async def get_node_by_id(node_id: int, db: AsyncSession = Depends(get_async_db)):
    nodes = await crud.get_nodes(db, node_id=node_id)
    if not nodes:
        return {"error": "Node not found"}
    return nodes[0]

@router.put("/{node_id}", response_model=schemas.NodeResponse)
async def update_node(node_id: int, data: schemas.NodeUpdate, db: AsyncSession = Depends(get_async_db)):
    return await crud.update_node(db, node_id, updates=data.dict(exclude_unset=True))

@router.delete("/{node_id}")
async def delete_node(node_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.delete_node(db, node_id)
