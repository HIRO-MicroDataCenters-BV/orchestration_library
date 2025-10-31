"""Unit tests for workload request decision repository functions."""

from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workload_request_decision import WorkloadRequestDecision
from datetime import datetime, timezone
from app.repositories.workload_request_decision import (
    create_workload_decision,
    get_workload_decision,
    get_all_workload_decisions,
    update_workload_decision,
    delete_workload_decision,
    update_workload_decision_status,
)
from app.schemas.workload_request_decision_schema import (
    WorkloadRequestDecisionStatusUpdate,
    WorkloadRequestDecisionUpdate,
)
from app.utils.exceptions import (
    DBEntryCreationException,
    DBEntryNotFoundException,
    DBEntryUpdateException,
    DBEntryDeletionException,
    OrchestrationBaseException,
)
from app.tests.utils.mock_objects import (
    mock_metrics_details,
    mock_workload_request_decision_create,
)


@pytest.mark.asyncio
async def test_create_workload_decision_success():
    """Test successful creation of a workload decision in DB."""
    mock_db = AsyncMock()
    mock_obj = MagicMock()
    mock_db.refresh = AsyncMock()

    # Attributes needed for KPI metrics creation in finally else block
    mock_obj.id = uuid4()
    mock_obj.node_name = "node-1"
    mock_obj.decision_start_time = datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
    mock_obj.decision_end_time = datetime(2024, 6, 1, 10, 0, 2, tzinfo=timezone.utc)

    with patch(
        "app.repositories.workload_request_decision.WorkloadRequestDecision",
        return_value=mock_obj,
    ), patch(
        "app.repositories.workload_request_decision.create_kpi_metrics"
    ) as mock_create_kpi:
        result = await create_workload_decision(
            mock_db,
            mock_workload_request_decision_create(),
            mock_metrics_details("POST", "/workload_request_decision"),
        )

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_obj)
    assert result == mock_obj

    # Assert KPI metrics creation (else branch)
    assert mock_create_kpi.called
    args, _ = mock_create_kpi.call_args
    # args: (db_session, kpi_data, metrics_details)
    kpi_data = args[1]
    assert kpi_data.request_decision_id == mock_obj.id
    assert kpi_data.node_name == mock_obj.node_name
    assert kpi_data.decision_time_in_seconds == 2.0


@pytest.mark.asyncio
async def test_get_workload_decision_success():
    """Test fetching a workload_decision by ID."""

    decision_id = uuid4()
    expected_decision = WorkloadRequestDecision(id=decision_id)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_decision

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_result

    # Act
    result = await get_workload_decision(
        mock_session,
        decision_id,
        mock_metrics_details("GET", f"/workload_request_decision/{decision_id}"),
    )

    # Assert
    assert result == expected_decision
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_workload_decision_not_found():
    """Test fetching a workload decision with non-existent ID."""
    decision_id = uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_result

    with pytest.raises(DBEntryNotFoundException) as exc_info:
        await get_workload_decision(
            mock_session,
            decision_id,
            mock_metrics_details("GET", f"/workload_request_decision/{decision_id}"),
        )

    assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_all_workload_decisions_success():
    """Test fetching all workload decisions."""
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
async def test_get_all_workload_decisions_with_filters_success():
    """Test fetching all workload decisions with filters."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()

    expected_data = [WorkloadRequestDecision(id=uuid4())]
    mock_scalars.all.return_value = expected_data

    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    filters = {"pod_name": "pod-a"}
    # Act
    result = await get_all_workload_decisions(mock_session, filters=filters)

    # Assert
    assert result == expected_data
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_workload_decision_success():
    """Test successful update of workload decision."""
    decision_id = uuid4()
    update_data = WorkloadRequestDecisionUpdate(pod_name="updated_pod")  # adjust fields

    existing_decision = WorkloadRequestDecision(id=decision_id, pod_name="old_value")

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_decision
    mock_session.execute.return_value = mock_result

    # Act
    result = await update_workload_decision(
        mock_session,
        decision_id,
        update_data,
        mock_metrics_details("PUT", f"/workload_request_decision/{decision_id}"),
    )

    # Assert
    assert result.pod_name == "updated_pod"
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_decision)


@pytest.mark.asyncio
async def test_update_workload_decision_not_found():
    """Test update with non-existent workload decision."""
    decision_id = uuid4()
    update_data = WorkloadRequestDecisionUpdate(pod_name="updated_value")

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(DBEntryNotFoundException):
        await update_workload_decision(
            mock_session,
            decision_id,
            update_data,
            mock_metrics_details("PUT", f"/workload_request_decision/{decision_id}"),
        )


# @pytest.mark.asyncio
# async def test_update_workload_decision_integrity_error():
#     """Test update with IntegrityError during commit."""
#     decision_id = uuid4()
#     update_data = WorkloadRequestDecisionUpdate(pod_name="updated_value")
#     existing_decision = WorkloadRequestDecision(id=decision_id, pod_name="old_value")

#     mock_session = AsyncMock()
#     mock_result = MagicMock()
#     mock_result.scalar_one_or_none.return_value = existing_decision
#     mock_session.execute.return_value = mock_result

#     # Simulate IntegrityError on commit
#     mock_session.commit.side_effect = IntegrityError("stmt", "params", "orig")

#     with pytest.raises(DBEntryUpdateException):
#         await update_workload_decision(mock_session, decision_id, update_data)

#     mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_workload_decision_status_success():
    """Test successful status update."""
    existing = WorkloadRequestDecision(
        pod_name="pod-a",
        namespace="ns1",
        node_name="node-x",
        action_type="bind",
        decision_status="pending",
    )
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing
    mock_session.execute.return_value = mock_result
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    payload = WorkloadRequestDecisionStatusUpdate(
        pod_name="pod-a",
        namespace="ns1",
        node_name="node-x",
        action_type="bind",
        decision_status="succeeded",
    )

    updated = await update_workload_decision_status(
        mock_session,
        payload,
        mock_metrics_details(
            "PATCH", f"/workload_request_decision/status/{payload.pod_name}"
        ),
    )

    assert updated.decision_status == "succeeded"
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing)


@pytest.mark.asyncio
async def test_update_workload_decision_status_not_found():
    """Test status update when record not found."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    payload = WorkloadRequestDecisionStatusUpdate(
        pod_name="pod-missing",
        namespace="nsX",
        node_name="node-missing",
        action_type="swap_x",
        decision_status="pending",
    )

    with pytest.raises(DBEntryNotFoundException):
        await update_workload_decision_status(
            mock_session,
            payload,
            mock_metrics_details(
                "PATCH", f"/workload_request_decision/status/{payload.pod_name}"
            ),
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc_cls",
    [IntegrityError, OperationalError, SQLAlchemyError],
)
async def test_update_workload_decision_status_db_errors(exc_cls):
    """Test status update DB exception branches."""
    existing = WorkloadRequestDecision(
        pod_name="pod-a",
        namespace="ns1",
        node_name="node-x",
        action_type="ScaleUp",
        decision_status="Pending",
    )
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing
    mock_session.execute.return_value = mock_result
    mock_session.commit.side_effect = (
        exc_cls("stmt", "params", "orig")
        if exc_cls is IntegrityError
        else exc_cls("err", None, None)
    )
    mock_session.rollback = AsyncMock()

    payload = WorkloadRequestDecisionStatusUpdate(
        pod_name="pod-a",
        namespace="ns1",
        node_name="node-x",
        action_type="bind",
        decision_status="pending",
    )

    with pytest.raises(DBEntryUpdateException):
        await update_workload_decision_status(
            mock_session,
            payload,
            mock_metrics_details(
                "PATCH", f"/workload_request_decision/status/{payload.pod_name}"
            ),
        )
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_workload_decision_success():
    """Test successful deletion of workload decision."""
    decision_id = uuid4()
    decision_obj = WorkloadRequestDecision(id=decision_id)

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = decision_obj
    mock_session.execute.return_value = mock_result

    result = await delete_workload_decision(
        mock_session,
        decision_id,
        mock_metrics_details("DELETE", f"/workload_request_decision/{decision_id}"),
    )

    assert result is True
    mock_session.delete.assert_awaited_once_with(decision_obj)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_workload_decision_not_found():
    """Test deletion of non-existent workload decision."""
    decision_id = uuid4()

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(DBEntryNotFoundException):
        await delete_workload_decision(
            mock_session,
            decision_id,
            mock_metrics_details("DELETE", f"/workload_request_decision/{decision_id}"),
        )


# @pytest.mark.asyncio
# async def test_delete_workload_decision_integrity_error():
#     """Test deletion with IntegrityError during commit."""
#     decision_id = uuid4()
#     decision_obj = WorkloadRequestDecision(id=decision_id)

#     mock_session = AsyncMock()
#     mock_result = MagicMock()
#     mock_result.scalar_one_or_none.return_value = decision_obj
#     mock_session.execute.return_value = mock_result
#     mock_session.commit.side_effect = IntegrityError("stmt", "params", "orig")

#     with pytest.raises(DBEntryDeletionException):
#         await delete_workload_decision(mock_session, decision_id)

#     mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc_cls,expected_exc",
    [
        (IntegrityError, DBEntryUpdateException),
        (OperationalError, DBEntryUpdateException),
        (SQLAlchemyError, DBEntryUpdateException),
    ],
)
async def test_update_workload_decision_db_errors(exc_cls, expected_exc):
    """Test update_workload_decision exception branches."""
    decision_id = uuid4()
    update_data = WorkloadRequestDecisionUpdate(pod_name="updated_value")
    existing_decision = WorkloadRequestDecision(id=decision_id, pod_name="old_value")

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_decision
    mock_session.execute.return_value = mock_result
    mock_session.commit.side_effect = (
        exc_cls("stmt", "params", "orig")
        if exc_cls is IntegrityError
        else exc_cls("err", None, None)
    )
    mock_session.rollback = AsyncMock()

    with pytest.raises(expected_exc):
        await update_workload_decision(
            mock_session,
            decision_id,
            update_data,
            mock_metrics_details("PUT", f"/workload_request_decision/{decision_id}"),
        )
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc_cls,expected_exc",
    [
        (IntegrityError, DBEntryDeletionException),
        (OperationalError, DBEntryDeletionException),
        (SQLAlchemyError, DBEntryDeletionException),
    ],
)
async def test_delete_workload_decision_db_errors(exc_cls, expected_exc):
    """Test delete_workload_decision exception branches."""
    decision_id = uuid4()
    decision_obj = WorkloadRequestDecision(id=decision_id)

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = decision_obj
    mock_session.execute.return_value = mock_result
    mock_session.commit.side_effect = (
        exc_cls("stmt", "params", "orig")
        if exc_cls is IntegrityError
        else exc_cls("err", None, None)
    )
    mock_session.rollback = AsyncMock()
    mock_session.delete = AsyncMock()

    with pytest.raises(expected_exc):
        await delete_workload_decision(
            mock_session,
            decision_id,
            mock_metrics_details("DELETE", f"/workload_request_decision/{decision_id}"),
        )
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc_cls,expected_exc",
    [
        (SQLAlchemyError, OrchestrationBaseException),
    ],
)
async def test_get_all_workload_decisions_db_error(exc_cls, expected_exc):
    """Test get_all_workload_decisions SQLAlchemy error branch."""
    mock_session = AsyncMock()
    mock_session.execute.side_effect = exc_cls("err", None, None)
    with pytest.raises(expected_exc):
        await get_all_workload_decisions(mock_session)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc_cls,expected_exc",
    [
        (IntegrityError, DBEntryCreationException),
        (OperationalError, DBEntryCreationException),
        (SQLAlchemyError, DBEntryCreationException),
    ],
)
async def test_create_workload_decision_db_errors(exc_cls, expected_exc):
    """Test create_workload_decision Integrity/Operational/SQLAlchemy
    error branches.
    """
    mock_db = AsyncMock()
    mock_db.commit.side_effect = exc_cls("err", None, None)
    mock_db.refresh = AsyncMock()
    mock_db.add = MagicMock()
    data = mock_workload_request_decision_create()
    metrics_details = mock_metrics_details("POST", "/workload_request_decision")
    with pytest.raises(expected_exc):
        await create_workload_decision(mock_db, data, metrics_details)
