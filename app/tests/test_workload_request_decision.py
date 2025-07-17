import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workload_request_decision import WorkloadRequestDecision
from app.repositories.workload_request_decision import (
    create_workload_decision,
    get_workload_decision,
    get_all_workload_decisions,
    update_workload_decision,
    delete_workload_decision,
)
from app.schemas.workload_request_decision_schema import (
    WorkloadRequestDecisionCreate,
    WorkloadRequestDecisionUpdate,
)
from app.utils.exceptions import (
    DBEntryNotFoundException,
    DBEntryUpdateException,
    DBEntryDeletionException,
)


@pytest.fixture
def sample_create_data():
    return WorkloadRequestDecisionCreate(
        pod_id=uuid4(),
        pod_name="test-pod",
        namespace="default",
        node_id=uuid4(),
        node_name="node-01",
        is_elastic=True,
        queue_name="queue-x",
        demand_cpu=0.5,
        demand_memory=256,
        demand_slack_cpu=0.1,
        demand_slack_memory=64,
        is_decision_status=True,
        pod_parent_id=uuid4(),
        pod_parent_name="controller",
        pod_parent_kind="Deployment",
        created_at="2024-07-01T12:00:00Z",
        deleted_at=None,
    )


@pytest.mark.asyncio
async def test_create_workload_decision_success(sample_create_data):
    mock_db = AsyncMock()
    mock_obj = MagicMock()
    mock_db.refresh = AsyncMock()

    with patch(
        "app.repositories.workload_request_decision.WorkloadRequestDecision",
        return_value=mock_obj,
    ):
        result = await create_workload_decision(mock_db, sample_create_data)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_obj)
    assert result == mock_obj


@pytest.mark.asyncio
async def test_get_workload_decision_success():
    # Arrange
    decision_id = uuid4()
    expected_decision = WorkloadRequestDecision(id=decision_id)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_decision

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_result

    # Act
    result = await get_workload_decision(mock_session, decision_id)

    # Assert
    assert result == expected_decision
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_workload_decision_not_found():
    decision_id = uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_result

    with pytest.raises(DBEntryNotFoundException) as exc_info:
        await get_workload_decision(mock_session, decision_id)

    assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_all_workload_decisions_success():
    # Arrange
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()

    expected_data = [WorkloadRequestDecision(id=uuid4())]
    mock_scalars.all.return_value = expected_data

    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act
    result = await get_all_workload_decisions(mock_session)

    # Assert
    assert result == expected_data
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_workload_decision_success():
    decision_id = uuid4()
    update_data = WorkloadRequestDecisionUpdate(pod_name="updated_pod")  # adjust fields

    existing_decision = WorkloadRequestDecision(id=decision_id, pod_name="old_value")

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_decision
    mock_session.execute.return_value = mock_result

    # Act
    result = await update_workload_decision(mock_session, decision_id, update_data)

    # Assert
    assert result.pod_name == "updated_pod"
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_decision)


@pytest.mark.asyncio
async def test_update_workload_decision_not_found():
    decision_id = uuid4()
    update_data = WorkloadRequestDecisionUpdate(field1="updated_value")

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(DBEntryNotFoundException):
        await update_workload_decision(mock_session, decision_id, update_data)


@pytest.mark.asyncio
async def test_update_workload_decision_integrity_error():
    decision_id = uuid4()
    update_data = WorkloadRequestDecisionUpdate(pod_name="updated_value")
    existing_decision = WorkloadRequestDecision(id=decision_id, pod_name="old_value")

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_decision
    mock_session.execute.return_value = mock_result

    # Simulate IntegrityError on commit
    mock_session.commit.side_effect = IntegrityError("stmt", "params", "orig")

    with pytest.raises(DBEntryUpdateException):
        await update_workload_decision(mock_session, decision_id, update_data)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_workload_decision_success():
    decision_id = uuid4()
    decision_obj = WorkloadRequestDecision(id=decision_id)

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = decision_obj
    mock_session.execute.return_value = mock_result

    result = await delete_workload_decision(mock_session, decision_id)

    assert result is True
    mock_session.delete.assert_awaited_once_with(decision_obj)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_workload_decision_not_found():
    decision_id = uuid4()

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(DBEntryNotFoundException):
        await delete_workload_decision(mock_session, decision_id)


@pytest.mark.asyncio
async def test_delete_workload_decision_integrity_error():
    decision_id = uuid4()
    decision_obj = WorkloadRequestDecision(id=decision_id)

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = decision_obj
    mock_session.execute.return_value = mock_result
    mock_session.commit.side_effect = IntegrityError("stmt", "params", "orig")

    with pytest.raises(DBEntryDeletionException):
        await delete_workload_decision(mock_session, decision_id)

    mock_session.rollback.assert_awaited_once()
