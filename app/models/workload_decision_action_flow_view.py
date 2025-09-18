"""
NOTE: For database views, the actual creation and management should be handled directly in Alembic migration files.
This ORM class is provided solely for reference and query purposes within the application code.

We intentionally configure Alembic to skip these view classes during autogeneration by using the `include_object`
function in alembic/env.py, so that they are not recognized as tables to be created, altered, or dropped.

If you want to modify this class, you should do so in the Alembic migration file
(alembic/versions/009_87e4d5720302_Add_workload_decision_action_flow_view_.py).).

Model for the workload_decision_action_flow database view.
Read-only ORM mapping.
"""
from sqlalchemy import Column, String, Boolean, Float, TIMESTAMP, UUID, Enum as SAEnum
from sqlalchemy.dialects.postgresql import INTERVAL
from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin
from app.utils.constants import (
    WORKLOAD_ACTION_TYPE_ENUM,
    WORKLOAD_ACTION_STATUS_ENUM,
    WORKLOAD_REQUEST_DECISION_STATUS_ENUM,
    POD_PARENT_TYPE_ENUM,
)


class WorkloadDecisionActionFlowView(Base, BaseDictMixin):
    """
    ORM mapping to the VIEW: workload_decision_action_flow.
    (created in Alembic migration 
    alembic/versions/009_87e4d5720302_Add_workload_decision_action_flow_view_.py).
    Do not flush INSERT/UPDATE/DELETE against this model.

    Below tablename should be same as the view name in 
    alembic/versions/009_87e4d5720302_Add_workload_decision_action_flow_view_.py
    """
    __tablename__ = "workload_decision_action_flow"
    __table_args__ = {"info": {"is_view": True}}

    # Composite primary key to keep SQLAlchemy happy
    decision_id = Column(UUID(as_uuid=True), primary_key=True)
    action_id = Column(UUID(as_uuid=True), primary_key=True)

    action_type = Column(SAEnum(*WORKLOAD_ACTION_TYPE_ENUM, 
                                name="workload_action_type_enum", native_enum=False))

    # Decision (d.*)
    decision_pod_name = Column(String)
    decision_namespace = Column(String)
    decision_node_name = Column(String)

    # Action created*
    created_pod_name = Column(String)
    created_pod_namespace = Column(String)
    created_node_name = Column(String)

    # Action deleted*
    deleted_pod_name = Column(String)
    deleted_pod_namespace = Column(String)
    deleted_node_name = Column(String)

    # Action bound*
    bound_pod_name = Column(String)
    bound_pod_namespace = Column(String)
    bound_node_name = Column(String)

    decision_status = Column(SAEnum(*WORKLOAD_REQUEST_DECISION_STATUS_ENUM, 
                                    name="workload_request_decision_status_enum", 
                                    native_enum=False))
    action_status = Column(SAEnum(*WORKLOAD_ACTION_STATUS_ENUM, 
                                   name="workload_action_status_enum", 
                                   native_enum=False))

    decision_start_time = Column(TIMESTAMP(timezone=True))
    decision_end_time = Column(TIMESTAMP(timezone=True))
    action_start_time = Column(TIMESTAMP(timezone=True))
    action_end_time = Column(TIMESTAMP(timezone=True))

    # Durations (PostgreSQL interval)
    decision_duration = Column(INTERVAL)
    action_duration = Column(INTERVAL)
    total_duration = Column(INTERVAL)

    decision_created_at = Column(TIMESTAMP(timezone=True))
    decision_deleted_at = Column(TIMESTAMP(timezone=True))
    action_created_at = Column(TIMESTAMP(timezone=True))
    action_updated_at = Column(TIMESTAMP(timezone=True))

    is_elastic = Column(Boolean)
    queue_name = Column(String)

    demand_cpu = Column(Float)
    demand_memory = Column(Float)
    demand_slack_cpu = Column(Float)
    demand_slack_memory = Column(Float)

    decision_pod_parent_id = Column(UUID(as_uuid=True))
    decision_pod_parent_name = Column(String)
    decision_pod_parent_kind = Column(SAEnum(*POD_PARENT_TYPE_ENUM, 
                                             name="pod_parent_type_enum", 
                                             native_enum=False))

    action_pod_parent_name = Column(String)
    action_pod_parent_type = Column(SAEnum(*POD_PARENT_TYPE_ENUM, 
                                           name="pod_parent_type_enum", 
                                           native_enum=False))
    action_pod_parent_uid = Column(String)

    action_reason = Column(String)
