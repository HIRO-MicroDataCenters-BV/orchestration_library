"""
Tests for WorkloadAction CRUD operations.
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from unittest.mock import AsyncMock, MagicMock
from app.models.workload_action import WorkloadAction
from app.repositories.workload_action import (
    create_workload_action,
    get_workload_action_by_id,
    update_workload_action,
    delete_workload_action,
    list_workload_actions,
)
from app.schemas.workload_action_schema import (
    WorkloadActionCreate,
    WorkloadActionUpdate,
)
from app.tests.utils.mock_objects import mock_workload_action_create_obj, mock_workload_action_obj, mock_workload_action_update_obj

@pytest.mark.asyncio
async def test_create_and_get_workload_action():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    # Create
    data = mock_workload_action_create_obj(action_type='Create', action_status='pending') 
    created = await create_workload_action(db, data)
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(created, WorkloadAction)
    assert created.action_type == "Create"
    assert created.action_status == "pending"

@pytest.mark.asyncio
async def test_get_workload_action_by_id():
    db = AsyncMock()
    action_id = uuid4()
    mock_action = mock_workload_action_obj(
        action_id=action_id, action_type='Delete', action_status='completed'
    )
    
    # Create a mock result object with scalar_one_or_none method
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_action
    db.execute.return_value = mock_result

    result = await get_workload_action_by_id(db, action_id)
    db.execute.assert_called_once()
    assert result == mock_action

@pytest.mark.asyncio
async def test_update_workload_action():
    db = AsyncMock()
    action_id = uuid4()
    mock_action = mock_workload_action_obj(
        action_id=action_id, action_type='Update', action_status='completed'
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_action
    db.execute.return_value = mock_result

    update_data = mock_workload_action_update_obj(action_id=action_id, action_status='in_progress')
    updated_action = await update_workload_action(db, action_id, update_data)
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert updated_action.action_status == 'in_progress'
    assert updated_action.action_id == action_id

@pytest.mark.asyncio
async def test_delete_workload_action():
    db = AsyncMock()
    action_id = uuid4()

    mock_action = mock_workload_action_obj(action_id=action_id, action_type='Delete', action_status='completed')
    
    db.execute.return_value.scalars.return_value.one_or_none.return_value = mock_action

    await delete_workload_action(db, action_id)
    db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_list_workload_actions():
    db = AsyncMock()
    mock_action1 = mock_workload_action_obj(action_id=uuid4(), action_type='Bind', action_status='completed')
    mock_action2 = mock_workload_action_obj(action_id=uuid4(), action_type='Bind', action_status='pending')

    # Setup the scalars().all() chain
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_action1, mock_action2]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    actions = await list_workload_actions(db, action_type='Bind', action_status=None)
    db.execute.assert_called_once()
    assert len(actions) == 2
    assert actions[0].action_type == 'Bind'
    assert actions[1].action_type == 'Bind'
    assert actions[0].action_status == 'completed'
    assert actions[1].action_status == 'pending'

