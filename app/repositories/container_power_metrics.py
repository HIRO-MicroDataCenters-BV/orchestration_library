"""
Container power metrics repository.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.container_power_metrics import ContainerPowerMetrics
from app.schemas.container_power_metrics import ContainerPowerMetricsCreate, ContainerPowerMetricsUpdate
import logging

class ContainerPowerMetricsRepository:
    """Repository for container power metrics operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, metrics: ContainerPowerMetricsCreate) -> ContainerPowerMetrics:
        db_metrics = ContainerPowerMetrics(**metrics.model_dump())
        self.db.add(db_metrics)
        await self.db.commit()
        await self.db.refresh(db_metrics)
        logging.debug(f"DB CREATE: {db_metrics}")
        return db_metrics

    async def get_by_pk(self, timestamp: datetime, container_name: str, pod_name: str) -> Optional[ContainerPowerMetrics]:
        query = select(ContainerPowerMetrics).where(
            and_(
                ContainerPowerMetrics.timestamp == timestamp,
                ContainerPowerMetrics.container_name == container_name,
                ContainerPowerMetrics.pod_name == pod_name
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        container_name: Optional[str] = None,
        pod_name: Optional[str] = None,
        namespace: Optional[str] = None,
        node_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ContainerPowerMetrics]:
        query = select(ContainerPowerMetrics)
        if container_name:
            query = query.where(ContainerPowerMetrics.container_name == container_name)
        if pod_name:
            query = query.where(ContainerPowerMetrics.pod_name == pod_name)
        if namespace:
            query = query.where(ContainerPowerMetrics.namespace == namespace)
        if node_name:
            query = query.where(ContainerPowerMetrics.node_name == node_name)
        if start_time:
            query = query.where(ContainerPowerMetrics.timestamp >= start_time)
        if end_time:
            query = query.where(ContainerPowerMetrics.timestamp <= end_time)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, timestamp: datetime, container_name: str, pod_name: str, metrics_update: ContainerPowerMetricsUpdate) -> Optional[ContainerPowerMetrics]:
        update_data = metrics_update.model_dump(exclude_unset=True)
        if not update_data:
            logging.debug(f"DB UPDATE: No update data for {timestamp}, {container_name}, {pod_name}")
            return None
        query = (
            update(ContainerPowerMetrics)
            .where(
                and_(
                    ContainerPowerMetrics.timestamp == timestamp,
                    ContainerPowerMetrics.container_name == container_name,
                    ContainerPowerMetrics.pod_name == pod_name
                )
            )
            .values(**update_data)
            .returning(ContainerPowerMetrics)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        updated = result.scalar_one_or_none()
        if updated:
            logging.debug(f"DB UPDATE: Updated {timestamp}, {container_name}, {pod_name}")
        else:
            logging.debug(f"DB UPDATE: No row found for {timestamp}, {container_name}, {pod_name}")
        return updated

    async def delete(self, timestamp: datetime, container_name: str, pod_name: str) -> bool:
        query = delete(ContainerPowerMetrics).where(
            and_(
                ContainerPowerMetrics.timestamp == timestamp,
                ContainerPowerMetrics.container_name == container_name,
                ContainerPowerMetrics.pod_name == pod_name
            )
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0

    async def get_by_container_name(self, container_name: str, skip: int = 0, limit: int = 100) -> List[ContainerPowerMetrics]:
        query = (
            select(ContainerPowerMetrics)
            .where(ContainerPowerMetrics.container_name == container_name)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_pod(self, pod_name: str, namespace: str, skip: int = 0, limit: int = 100) -> List[ContainerPowerMetrics]:
        query = (
            select(ContainerPowerMetrics)
            .where(
                ContainerPowerMetrics.pod_name == pod_name,
                ContainerPowerMetrics.namespace == namespace
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all() 