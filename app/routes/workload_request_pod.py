from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from app import schemas, crud

router = APIRouter(prefix="/workload_request_pod")


@router.post("/")
async def create_workload_request_pod(
    data: schemas.WorkloadRequestPodCreate, db: AsyncSession = Depends(get_async_db)
):
    """
        Create a new WorkloadRequestPod entry.

        Args:
            data (WorkloadRequestPodCreate): The data required to create the WorkloadRequestPod.
            db (AsyncSession): The database session dependency.

        Returns:
            The newly created WorkloadRequestPod object.
        """
    return await crud.create_workload_request_pod(db, data)


@router.get("/")
async def read_workload_request_pods(
    workload_request_pod_id: int = None,
    workload_request_id: int = None,
    pod_id: int = None,
    db: AsyncSession = Depends(get_async_db),
):
    """
        Retrieve a list of WorkloadRequestPod entries filtered by optional parameters.

        Args:
            workload_request_pod_id (int, optional): Filter by the WorkloadRequestPod ID.
            workload_request_id (int, optional): Filter by the associated WorkloadRequest ID.
            pod_id (int, optional): Filter by the associated Pod ID.
            db (AsyncSession): The database session dependency.

        Returns:
            A list of matching WorkloadRequestPod entries or an error message if none found.
    """
    pods = await crud.get_workload_request_pods(
        db,
        workload_request_pod_id=workload_request_pod_id,
        workload_request_id=workload_request_id,
        pod_id=pod_id,
    )
    if not pods:
        return {"error": "No workload request pods found"}
    return pods


@router.put("/{workload_request_pod_id}")
async def update_workload_request_pod(
    workload_request_pod_id: int,
    data: schemas.WorkloadRequestPodUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """
        Update an existing WorkloadRequestPod entry.

        Args:
            workload_request_pod_id (int): The ID of the WorkloadRequestPod to update.
            data (WorkloadRequestPodUpdate): The updated field values.
            db (AsyncSession): The database session dependency.

        Returns:
            The updated WorkloadRequestPod object.
    """
    return await crud.update_workload_request_pod(
        db, workload_request_pod_id, updates=data.model_dump(exclude_unset=True)
    )


@router.delete("/{workload_request_pod_id}")
async def delete_workload_request_pod(
    workload_request_pod_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """
        Delete a WorkloadRequestPod entry by its ID.

        Args:
            workload_request_pod_id (int): The ID of the WorkloadRequestPod to delete.
            db (AsyncSession): The database session dependency.

        Returns:
            A message indicating successful deletion or error if not found.
    """
    return await crud.delete_workload_request_pod(db, workload_request_pod_id)


@router.get("/{workload_request_pod_id}")
async def read_workload_request_pod_by_id(
    workload_request_pod_id: int, db: AsyncSession = Depends(get_async_db)
):
    """
        Retrieve a single WorkloadRequestPod entry by its ID.

        Args:
            workload_request_pod_id (int): The ID of the WorkloadRequestPod.
            db (AsyncSession): The database session dependency.

        Returns:
            The matched WorkloadRequestPod object or an error if not found.
    """
    pod_entry = await crud.get_workload_request_pods(
        db, workload_request_pod_id=workload_request_pod_id
    )
    if not pod_entry:
        return {"error": "ID not found"}
    return pod_entry
