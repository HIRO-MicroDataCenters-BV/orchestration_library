"""
Tests for WorkloadAction CRUD operations.
"""

from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
import sqlalchemy
import pytest
from app.models.workload_action import WorkloadAction
from app.repositories.workload_action import (
    create_workload_action,
    get_workload_action_by_id,
    update_workload_action,
    delete_workload_action,
    list_workload_actions,
)
from app.tests.utils.mock_objects import (
    mock_metrics_details,
    mock_workload_action_create_obj,
    mock_workload_action_obj,
    mock_workload_action_update_obj,
)
from app.utils.constants import WorkloadActionStatusEnum, WorkloadActionTypeEnum
from app.utils.exceptions import (
    DBEntryCreationException,
    DBEntryUpdateException,
    DBEntryDeletionException,
    DatabaseConnectionException,
    DBEntryNotFoundException,
    OrchestrationBaseException,
)


@pytest.mark.asyncio
async def test_create_workload_action():
    """Test for creating a workload action."""
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    # Create
    data = mock_workload_action_create_obj(
        action_type=WorkloadActionTypeEnum.CREATE,
        action_status=WorkloadActionStatusEnum.PENDING,
    )
    metrics_details = mock_metrics_details("POST", "/workload_action")
    created = await create_workload_action(db, data, metrics_details=metrics_details)
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(created, WorkloadAction)
    assert created.action_type == WorkloadActionTypeEnum.CREATE
    assert created.action_status == WorkloadActionStatusEnum.PENDING


@pytest.mark.asyncio
async def test_get_workload_action_by_id():
    """Test for retrieving a workload action by ID."""
    db = AsyncMock()
    action_id = uuid4()
    mock_action = mock_workload_action_obj(
        action_id=action_id,
        action_type=WorkloadActionTypeEnum.DELETE,
        action_status=WorkloadActionStatusEnum.SUCCEEDED,
    )

    # Create a mock result object with scalar_one_or_none method
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_action
    db.execute.return_value = mock_result

    metrics_details = mock_metrics_details("GET", f"/workload_action/{action_id}")
    result = await get_workload_action_by_id(
        db, action_id, metrics_details=metrics_details
    )
    db.execute.assert_called_once()
    assert result == mock_action


@pytest.mark.asyncio
async def test_update_workload_action():
    """Test for updating a workload action."""
    db = AsyncMock()
    action_id = uuid4()
    mock_action = mock_workload_action_obj(
        action_id=action_id,
        action_type=WorkloadActionTypeEnum.BIND,
        action_status=WorkloadActionStatusEnum.SUCCEEDED,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_action
    db.execute.return_value = mock_result

    update_data = mock_workload_action_update_obj(
        action_id=action_id, action_status=WorkloadActionStatusEnum.PENDING
    )
    metrics_details = mock_metrics_details("PUT", f"/workload_action/{action_id}")
    updated_action = await update_workload_action(
        db, action_id, update_data, metrics_details=metrics_details
    )
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert updated_action.action_status == WorkloadActionStatusEnum.PENDING
    assert updated_action.id == action_id


@pytest.mark.asyncio
async def test_delete_workload_action():
    """Test for deleting a workload action."""
    db = AsyncMock()
    action_id = uuid4()

    mock_action = mock_workload_action_obj(
        action_id=action_id,
        action_type=WorkloadActionTypeEnum.DELETE,
        action_status=WorkloadActionStatusEnum.SUCCEEDED,
    )

    db.execute.return_value.scalars.return_value.one_or_none.return_value = mock_action

    metrics_details = mock_metrics_details("DELETE", f"/workload_action/{action_id}")
    await delete_workload_action(db, action_id, metrics_details=metrics_details)
    db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_list_workload_actions():
    """Test for listing workload actions with filters."""
    db = AsyncMock()
    mock_action1 = mock_workload_action_obj(
        action_id=uuid4(),
        action_type=WorkloadActionTypeEnum.BIND,
        action_status=WorkloadActionStatusEnum.SUCCEEDED,
    )
    mock_action2 = mock_workload_action_obj(
        action_id=uuid4(),
        action_type=WorkloadActionTypeEnum.BIND,
        action_status=WorkloadActionStatusEnum.PENDING,
    )

    # Setup the scalars().all() chain
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_action1, mock_action2]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    actions = await list_workload_actions(
        db,
        filters={"action_type": "bind", "action_status": None},
        metrics_details=None,
    )
    db.execute.assert_called_once()
    assert len(actions) == 2
    assert actions[0].action_type == WorkloadActionTypeEnum.BIND
    assert actions[1].action_type == WorkloadActionTypeEnum.BIND
    assert actions[0].action_status == WorkloadActionStatusEnum.SUCCEEDED
    assert actions[1].action_status == WorkloadActionStatusEnum.PENDING


@pytest.mark.asyncio
async def test_create_workload_action_integrity_error():
    """Test for creating a workload action with integrity error."""
    db = MagicMock()
    db.commit = AsyncMock(
        side_effect=sqlalchemy.exc.IntegrityError("stmt", "params", "orig")
    )
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.rollback = AsyncMock()
    data = mock_workload_action_create_obj(
        action_type=WorkloadActionTypeEnum.CREATE,
        action_status=WorkloadActionStatusEnum.PENDING,
    )
    with pytest.raises(DBEntryCreationException):
        metrics_details = mock_metrics_details("POST", "/workload_action")
        await create_workload_action(db, data, metrics_details=metrics_details)


@pytest.mark.asyncio
async def test_create_workload_action_operational_error():
    """Test for creating a workload action with operational error."""
    db = MagicMock()
    db.commit = AsyncMock(
        side_effect=sqlalchemy.exc.OperationalError("stmt", "params", "orig")
    )
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.rollback = AsyncMock()
    data = mock_workload_action_create_obj(
        action_type=WorkloadActionTypeEnum.CREATE,
        action_status=WorkloadActionStatusEnum.PENDING,
    )
    with pytest.raises(DBEntryCreationException):
        metrics_details = mock_metrics_details("POST", "/workload_action")
        await create_workload_action(db, data, metrics_details=metrics_details)


@pytest.mark.asyncio
async def test_create_workload_action_sqlalchemy_error():
    """Test for creating a workload action with SQLAlchemy error."""
    db = MagicMock()
    db.commit = AsyncMock(side_effect=sqlalchemy.exc.SQLAlchemyError("error"))
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.rollback = AsyncMock()
    data = mock_workload_action_create_obj(
        action_type=WorkloadActionTypeEnum.CREATE,
        action_status=WorkloadActionStatusEnum.PENDING,
    )
    with pytest.raises(DBEntryCreationException):
        metrics_details = mock_metrics_details("POST", "/workload_action")
        await create_workload_action(db, data, metrics_details=metrics_details)


@pytest.mark.asyncio
async def test_get_workload_action_by_id_not_found():
    """Test for retrieving a workload action by ID when not found."""
    db = AsyncMock()
    action_id = uuid4()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    with pytest.raises(DBEntryNotFoundException):
        metrics_details = mock_metrics_details("GET", f"/workload_action/{action_id}")
        await get_workload_action_by_id(db, action_id, metrics_details=metrics_details)


@pytest.mark.asyncio
async def test_get_workload_action_by_id_operational_error():
    """Test for retrieving a workload action by ID with operational error."""
    db = AsyncMock()
    db.execute.side_effect = sqlalchemy.exc.OperationalError("stmt", "params", "orig")
    with pytest.raises(OrchestrationBaseException):
        action_id = uuid4()
        metrics_details = mock_metrics_details("GET", f"/workload_action/{action_id}")
        await get_workload_action_by_id(db, action_id, metrics_details=metrics_details)


@pytest.mark.asyncio
async def test_get_workload_action_by_id_sqlalchemy_error():
    """Test for retrieving a workload action by ID with SQLAlchemy error."""
    db = AsyncMock()
    db.execute.side_effect = sqlalchemy.exc.SQLAlchemyError("error")
    with pytest.raises(OrchestrationBaseException):
        action_id = uuid4()
        metrics_details = mock_metrics_details("GET", f"/workload_action/{action_id}")
        await get_workload_action_by_id(db, action_id, metrics_details=metrics_details)


@pytest.mark.asyncio
async def test_update_workload_action_not_found():
    """Test for updating a workload action when not found."""
    db = AsyncMock()
    action_id = uuid4()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    update_data = mock_workload_action_update_obj(
        action_id=action_id, action_status="pending"
    )
    with pytest.raises(DBEntryNotFoundException):
        metrics_details = mock_metrics_details("PUT", f"/workload_action/{action_id}")
        await update_workload_action(
            db, action_id, update_data, metrics_details=metrics_details
        )


@pytest.mark.asyncio
async def test_update_workload_action_integrity_error():
    """Test for updating a workload action with integrity error."""
    db = AsyncMock()
    action_id = uuid4()
    mock_action = mock_workload_action_obj(
        action_id=action_id,
        action_type=WorkloadActionTypeEnum.BIND,
        action_status=WorkloadActionStatusEnum.SUCCEEDED,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_action
    db.execute.return_value = mock_result
    db.commit = AsyncMock(
        side_effect=sqlalchemy.exc.IntegrityError("stmt", "params", "orig")
    )
    db.refresh = AsyncMock()
    update_data = mock_workload_action_update_obj(
        action_id=action_id, action_status=WorkloadActionStatusEnum.PENDING
    )
    with pytest.raises(DBEntryUpdateException):
        metrics_details = mock_metrics_details("PUT", f"/workload_action/{action_id}")
        await update_workload_action(
            db, action_id, update_data, metrics_details=metrics_details
        )


@pytest.mark.asyncio
async def test_update_workload_action_operational_error():
    """Test for updating a workload action with operational error."""
    db = AsyncMock()
    action_id = uuid4()
    mock_action = mock_workload_action_obj(
        action_id=action_id,
        action_type=WorkloadActionTypeEnum.BIND,
        action_status=WorkloadActionStatusEnum.SUCCEEDED,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_action
    db.execute.return_value = mock_result
    db.commit = AsyncMock(
        side_effect=sqlalchemy.exc.OperationalError("stmt", "params", "orig")
    )
    db.refresh = AsyncMock()
    update_data = mock_workload_action_update_obj(
        action_id=action_id, action_status=WorkloadActionStatusEnum.PENDING
    )
    with pytest.raises(DBEntryUpdateException):
        metrics_details = mock_metrics_details("PUT", f"/workload_action/{action_id}")
        await update_workload_action(
            db, action_id, update_data, metrics_details=metrics_details
        )


@pytest.mark.asyncio
async def test_update_workload_action_sqlalchemy_error():
    """Test for updating a workload action with SQLAlchemy error."""
    db = AsyncMock()
    action_id = uuid4()
    mock_action = mock_workload_action_obj(
        action_id=action_id,
        action_type=WorkloadActionTypeEnum.BIND,
        action_status=WorkloadActionStatusEnum.SUCCEEDED,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_action
    db.execute.return_value = mock_result
    db.commit = AsyncMock(side_effect=sqlalchemy.exc.SQLAlchemyError("error"))
    db.refresh = AsyncMock()
    update_data = mock_workload_action_update_obj(
        action_id=action_id, action_status=WorkloadActionStatusEnum.PENDING
    )
    with pytest.raises(DBEntryUpdateException):
        metrics_details = mock_metrics_details("PUT", f"/workload_action/{action_id}")
        await update_workload_action(
            db, action_id, update_data, metrics_details=metrics_details
        )


@pytest.mark.asyncio
async def test_delete_workload_action_not_found():
    """Test for deleting a workload action when not found."""
    db = AsyncMock()
    action_id = uuid4()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    with pytest.raises(DBEntryNotFoundException):
        metrics_details = mock_metrics_details(
            "DELETE", f"/workload_action/{action_id}"
        )
        await delete_workload_action(db, action_id, metrics_details=metrics_details)


@pytest.mark.asyncio
async def test_delete_workload_action_integrity_error():
    """Test for deleting a workload action with integrity error."""
    db = AsyncMock()
    action_id = uuid4()
    mock_action = mock_workload_action_obj(
        action_id=action_id,
        action_type=WorkloadActionTypeEnum.DELETE,
        action_status=WorkloadActionStatusEnum.SUCCEEDED,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_action
    db.execute.return_value = mock_result
    db.delete = AsyncMock()
    db.commit = AsyncMock(
        side_effect=sqlalchemy.exc.IntegrityError("stmt", "params", "orig")
    )
    with pytest.raises(DBEntryDeletionException):
        metrics_details = mock_metrics_details(
            "DELETE", f"/workload_action/{action_id}"
        )
        await delete_workload_action(db, action_id, metrics_details=metrics_details)


@pytest.mark.asyncio
async def test_delete_workload_action_operational_error():
    """Test for deleting a workload action with operational error."""
    db = AsyncMock()
    action_id = uuid4()
    mock_action = mock_workload_action_obj(
        action_id=action_id,
        action_type=WorkloadActionTypeEnum.DELETE,
        action_status=WorkloadActionStatusEnum.SUCCEEDED,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_action
    db.execute.return_value = mock_result
    db.delete = AsyncMock()
    db.commit = AsyncMock(
        side_effect=sqlalchemy.exc.OperationalError("stmt", "params", "orig")
    )
    with pytest.raises(DBEntryDeletionException):
        metrics_details = mock_metrics_details(
            "DELETE", f"/workload_action/{action_id}"
        )
        await delete_workload_action(db, action_id, metrics_details=metrics_details)


@pytest.mark.asyncio
async def test_delete_workload_action_sqlalchemy_error():
    """Test for deleting a workload action with SQLAlchemy error."""
    db = AsyncMock()
    action_id = uuid4()
    mock_action = mock_workload_action_obj(
        action_id=action_id,
        action_type=WorkloadActionTypeEnum.DELETE,
        action_status=WorkloadActionStatusEnum.SUCCEEDED,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_action
    db.execute.return_value = mock_result
    db.delete = AsyncMock()
    db.commit = AsyncMock(side_effect=sqlalchemy.exc.SQLAlchemyError("error"))
    with pytest.raises(DBEntryDeletionException):
        metrics_details = mock_metrics_details(
            "DELETE", f"/workload_action/{action_id}"
        )
        await delete_workload_action(db, action_id, metrics_details=metrics_details)


@pytest.mark.asyncio
async def test_list_workload_actions_sqlalchemy_error():
    """Test for listing workload actions with SQLAlchemy error."""
    db = AsyncMock()
    db.execute.side_effect = sqlalchemy.exc.SQLAlchemyError("error")
    with pytest.raises(DatabaseConnectionException):
        metrics_details = mock_metrics_details("GET", "/workload_actions")
        await list_workload_actions(
            db,
            filters={"action_type": WorkloadActionTypeEnum.BIND},
            metrics_details=metrics_details,
        )
