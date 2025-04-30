import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid
from app.models import WorkloadRequestDecision
from app.schemas import WorkloadRequestDecisionCreate
from app.crud.workload_request_decision import (
    create_workload_request_decision,
    update_workload_request_decision,
    get_workload_request_decision,
    delete_workload_request_decision,
)


@pytest.mark.asyncio
async def test_create_workload_request_decision():
    db = AsyncMock()
    decision_data = WorkloadRequestDecisionCreate(
        workload_request_id=1,
        node_name="node-1",
        queue_name="queue-1",
        status="pending",
    )
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await create_workload_request_decision(db, decision_data)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(result, WorkloadRequestDecision)


@pytest.mark.asyncio
async def test_update_workload_request_decision():
    db = AsyncMock()
    mock_decision = MagicMock(spec=WorkloadRequestDecision, status="pending")
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=mock_decision))  # Directly return the mock_decision
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    updates = {"status": "approved"}
    result = await update_workload_request_decision(db, workload_request_id=1, updates=updates)

    db.execute.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result is not None
    assert result.status == "approved"


@pytest.mark.asyncio
async def test_get_workload_request_decision():
    db = AsyncMock()
    # mock_decision = WorkloadRequestDecision()
    mock_decision = MagicMock(spec=WorkloadRequestDecision, workload_request_id=1, status="pending", node_name="node-1", queue_name="queue-1")
    # mock_decision_list = [mock_decision, mock_decision]
    # mock_decision.workload_request_id = 1
    # mock_decision.node_name = "node-1"
    # mock_decision.queue_name = "queue-1"
    # mock_decision.status = "pending"

    # Create a mock WorkloadRequestDecision object
    # mock_decision = WorkloadRequestDecision(
    #     workload_request_id=1,
    #     node_name="node-1",
    #     queue_name="queue-1",
    #     status="pending",
    # )
    # db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(all=MagicMock(return_value=[mock_decision]))))
    # db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(all=lambda: [mock_decision])))
    db.execute = AsyncMock(return_value=AsyncMock(scalars=MagicMock(all=AsyncMock(return_value=[mock_decision]))))


    # db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(all=lambda: [mock_decision, mock_decision])))
    # db.execute = AsyncMock(return_value=[decision_data])

    result = await get_workload_request_decision(db, workload_request_id=1, node_name="node-1", queue_name="queue-1", status="pending")
    print(result)
    print(list(result))
    print(type(result))
    print(isinstance(result, MagicMock))
    print(isinstance(result, list))
    print(result[0], isinstance(result[0], WorkloadRequestDecision))
    print(result[1], isinstance(result[1], WorkloadRequestDecision))

    db.execute.assert_called_once()
    assert result is not None
    # assert result.workload_request_id == 1
    # assert len(result) == 2
    # assert isinstance(result[0], WorkloadRequestDecision)


@pytest.mark.asyncio
async def test_delete_workload_request_decision():
    db = AsyncMock()
    mock_decision = WorkloadRequestDecision()
    db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(all=MagicMock(return_value=[mock_decision]))))
    db.delete = AsyncMock()
    db.commit = AsyncMock()

    result = await delete_workload_request_decision(db, workload_request_id=1)

    db.execute.assert_called_once()
    db.delete.assert_called()
    db.commit.assert_called_once()
    assert result["message"] == "Decision with ID 1 has been deleted"


###### Need to fix below test ######

# DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# # Set up the test database
# engine_test = create_async_engine(DATABASE_URL, echo=False)
# TestSessionLocal = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

# @pytest.mark.asyncio
# async def test_delete_workload_request_decision():
#     db = AsyncMock()
#     mock_decision = WorkloadRequestDecision()
#     db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(all=MagicMock(return_value=[mock_decision]))))
#     db.delete = AsyncMock()
#     db.commit = AsyncMock()

#     result = await delete_workload_request_decision(db, workload_request_id=1)

#     db.execute.assert_called_once()
#     db.delete.assert_called()
#     db.commit.assert_called_once()
#     assert result["message"] == "Decision with ID 1 has been deleted"



# @pytest.fixture(scope="function")
# async def db_session():
#     async with engine_test.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     async with TestSessionLocal() as session:
#         try:
#             yield session
#         finally:
#             async with engine_test.begin() as conn:
#                 await conn.run_sync(Base.metadata.drop_all)

# @pytest.mark.asyncio
# async def test_get_workload_request_decision(db_session):
#     # Insert sample data
#     test_data = WorkloadRequestDecision(
#         workload_request_id=1,
#         node_name="node-1",
#         queue_name="queue-1",
#         status="queued",
#     )
#     db_session.add(test_data)
#     await db_session.commit()

#     # Test with one filter
#     result = await get_workload_request_decision(db_session, node_name="node-1")
#     assert len(result) == 1
#     assert result[0].node_name == "node-1"

#     # Test with all filters
#     result = await get_workload_request_decision(
#         db_session,
#         workload_request_id=1,
#         node_name="node-1",
#         queue_name="queue-1",
#         status="queued"
#     )
#     assert len(result) == 1
#     assert result[0].queue_name == "queue-1"

#     # Test with no filters
#     result = await get_workload_request_decision(db_session)
#     assert len(result) == 1

#     # Test with non-matching filter
#     result = await get_workload_request_decision(db_session, node_name="not-found")
#     assert result == []
