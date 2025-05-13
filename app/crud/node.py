from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models import Node
from app.schemas import NodeCreate


async def create_node(db: AsyncSession, data: NodeCreate):
    node = Node(**data.dict())
    db.add(node)
    await db.commit()
    await db.refresh(node)
    return node


async def get_nodes(db: AsyncSession, node_id: int = None):
    if node_id:
        query = select(Node).where(Node.id == node_id)
    else:
        query = select(Node)
    result = await db.execute(query)
    return result.scalars().all()


async def update_node(db: AsyncSession, node_id: int, updates: dict):
    await db.execute(update(Node).where(Node.id == node_id).values(**updates))
    await db.commit()
    query = select(Node).where(Node.id == node_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def delete_node(db: AsyncSession, node_id: int):
    await db.execute(delete(Node).where(Node.id == node_id))
    await db.commit()
    return {"deleted_id": node_id}
