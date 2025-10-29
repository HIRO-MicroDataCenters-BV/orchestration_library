"""Mock objects for testing Kubernetes cluster information retrieval""" ""
from datetime import datetime, timedelta, timezone
import time
from unittest.mock import MagicMock
from uuid import UUID, uuid4

from app.models.alerts import Alert
from app.schemas.alerts_request import AlertCreateRequest, AlertResponse, AlertType
from app.schemas.workload_action_schema import (
    WorkloadAction,
    WorkloadActionCreate,
    WorkloadActionUpdate,
)
from app.schemas.workload_decision_action_flow_schema import (
    WorkloadDecisionActionFlowItem,
)
from app.schemas.workload_request_decision_schema import WorkloadRequestDecisionCreate
from app.utils.constants import (
    PodParentTypeEnum,
    WorkloadActionStatusEnum,
    WorkloadActionTypeEnum,
    WorkloadRequestDecisionStatusEnum,
)


TEST_DATE = datetime.now(timezone.utc)
TEST_UUID = str(uuid4())


def to_jsonable(obj):
    """Recursively convert UUIDs and datetimes in dicts to strings for JSON serialization."""
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(i) for i in obj]
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def mock_to_dict(obj):
    """
    Recursively convert MagicMock or object with attributes to a dict.
    Works for nested mocks, dicts, and lists.
    """
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, list):
        return [mock_to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: mock_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, MagicMock) or hasattr(obj, "__dict__"):
        result = {}
        for attr in dir(obj):
            if attr.startswith("_"):
                continue  # skip private/internal attributes
            try:
                value = getattr(obj, attr)
            except AttributeError:
                continue
            if callable(value):
                continue
            result[attr] = mock_to_dict(value)
        return result
    return str(obj)  # fallback for unknown types


def mock_version_info():
    """
    Mock version information for the Kubernetes cluster.
    """
    version = MagicMock()
    version.git_version = "v1.25.0-test-10.0.0.1"
    version.git_commit = "abcdef123456"
    return version


# @pytest.fixture
def mock_component():
    """
    Mock a Kubernetes component status object.
    """
    comp = MagicMock()
    comp.metadata.name = "scheduler"
    cond = MagicMock(type="Healthy", status="True")
    comp.conditions = [cond]
    return comp


def mock_configmap():
    """
    Mock a Kubernetes ConfigMap object.
    """
    configmap = MagicMock()
    configmap.metadata.name = "kubeadm-config"
    configmap.metadata.namespace = "kube-system"
    configmap.data = {
        "ClusterConfiguration": """apiServer:
  certSANs:
  - 35.35.35.35
  extraArgs:
    authorization-mode: Node,RBAC
  timeoutForControlPlane: 4m0s
apiVersion: kubeadm.k8s.io/v1beta3
certificatesDir: /etc/kubernetes/pki
clusterName: test-cluster
controllerManager: {}
dns: {}
etcd:
  local:
    dataDir: /var/lib/etcd
imageRepository: registry.k8s.io
kind: ClusterConfiguration
kubernetesVersion: v1.29.4
networking:
  dnsDomain: cluster.local
  podSubnet: 10.42.0.0/16
  serviceSubnet: 10.43.0.0/16
scheduler: {}
"""
    }
    return configmap


# @pytest.fixture
def mock_pod():
    """
    Mock a Kubernetes pod object in the kube-system namespace.
    """
    pod = MagicMock()
    pod.metadata.name = "kube-proxy"
    pod.metadata.namespace = "kube-system"
    pod.status.phase = "Running"
    pod.spec.node_name = "node1"
    container_status = MagicMock()
    container_status.name = "kube-proxy"
    container_status.ready = True
    container_status.restart_count = 0
    container_status.image = "kube-proxy:v1.25.0"
    pod.status.container_statuses = [container_status]
    return pod


def mock_node():
    """
    Mock a Kubernetes node object with various attributes.
    """
    node = MagicMock()
    node.api_version = "v1"
    node.metadata.uid = "node-uid"
    node.metadata.name = "test-node"
    node.metadata.labels = {"role": "worker"}
    node.metadata.annotations = {"anno": "value"}
    # Node conditions
    condition = MagicMock()
    condition.type = "Ready"
    condition.message = "Node is ready"
    condition.reason = "KubeletReady"
    node.status.conditions = [condition]
    # Node info
    node_info = MagicMock()
    node_info.architecture = "amd64"
    node_info.container_runtime_version = "docker://20.10"
    node_info.kernel_version = "5.10"
    node_info.kubelet_version = "v1.21.0"
    node_info.os_image = "Ubuntu 20.04"
    node.status.node_info = node_info
    # Capacity and allocatable
    node.status.capacity = {"cpu": "4", "memory": "8Gi"}
    node.status.allocatable = {"cpu": "4", "memory": "8Gi"}
    # Addresses
    address = MagicMock()
    address.type = "InternalIP"
    address.address = "192.168.1.10"
    node.status.addresses = [address]
    # Pod CIDR
    node.spec.pod_cidr = "10.244.0.0/24"
    # Taints
    taint = MagicMock()
    taint.key = "node-role.kubernetes.io/master"
    taint.value = "true"
    taint.effect = "NoSchedule"
    node.spec.taints = [taint]
    node.spec.unschedulable = False
    return node


def mock_custom_api():
    """
    Mock a Kubernetes custom API object for metrics.
    """
    custom_api = MagicMock()
    custom_api.list_cluster_custom_object.return_value = {
        "items": [
            {
                "metadata": {"name": "test-node"},
                "usage": {"cpu": "100m", "memory": "512Mi"},
            }
        ]
    }
    return custom_api


def pod_mock_fixture():
    """
    Fixture to create a mock pod object with necessary attributes.
    """
    pod = MagicMock()
    pod.api_version = "v1"
    pod.metadata.uid = "123e4567-e89b-12d3-a456-426614174000"
    pod.metadata.namespace = "default"
    pod.metadata.name = "test-pod"
    pod.metadata.labels = {"app": "test"}
    pod.metadata.annotations = {"anno": "value"}
    pod.status.phase = "Running"
    pod.status.message = "All good"
    pod.status.reason = "Started"
    pod.status.host_ip = "1.2.3.4"
    pod.status.pod_ip = "5.6.7.8"
    pod.status.start_time = "2024-01-01T00:00:00Z"
    pod.spec.node_name = "node1"
    pod.spec.scheduler_name = "default-scheduler"
    container = MagicMock()
    container.name = "container1"
    container.image = "image:latest"
    container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
    container.resources.limits = {"cpu": "200m", "memory": "256Mi"}
    pod.spec.containers = [container]
    return pod


def mock_user_pod():
    """
    Mock pod object with necessary attributes.
    """
    pod = MagicMock()
    pod.metadata.owner_references = []
    pod.metadata.uid = "123e4567-e89b-12d3-a456-426614174000"
    pod.metadata.name = "test-pod"
    pod.metadata.namespace = "default"
    return pod


def make_owner(kind, name):
    """
    Create a mock owner reference with the specified kind and name.
    """
    owner = MagicMock()
    owner.kind = kind
    owner.name = name
    return owner


def mock_metrics_details(method, endpoint):
    """
    Mock metrics details dictionary for a workload action.
    """
    return {"start_time": time.time(), "method": method, "endpoint": endpoint}


def mock_workload_action_create_obj(
    action_id=None, action_type=None, action_status=None, count=1
):
    """
    Mock a workload action object with necessary attributes.
    """
    return WorkloadActionCreate(
        action_id=action_id or "123e4567-e89b-12d3-a456-426614174000",
        action_type=action_type or WorkloadActionTypeEnum.CREATE,
        action_status=action_status or WorkloadActionStatusEnum.PENDING,
        action_start_time=datetime.now(timezone.utc),
        action_end_time=None,
        action_reason=f"Test reason {count}",
        pod_parent_name=f"parent {count}",
        pod_parent_type=PodParentTypeEnum.DEPLOYMENT,
        pod_parent_uid=uuid4(),
        created_pod_name=f"pod {count}",
        created_pod_namespace="default",
        created_node_name=f"node {count}",
        deleted_pod_name=None,
        deleted_pod_namespace=None,
        deleted_node_name=None,
        bound_pod_name=None,
        bound_pod_namespace=None,
        bound_node_name=None,
    )


def mock_workload_action_update_obj(
    action_id=None, action_type=None, action_status=None, count=1
):
    """
    Mock a workload action update object with necessary attributes.
    """
    return WorkloadActionUpdate(
        action_id=action_id or "123e4567-e89b-12d3-a456-426614174000",
        action_type=action_type or WorkloadActionTypeEnum.SWAP_X,
        action_status=action_status or WorkloadActionStatusEnum.PENDING,
        action_reason=f"Updated reason {count}",
        pod_parent_name=f"parent {count}",
        pod_parent_type=PodParentTypeEnum.DEPLOYMENT,
        pod_parent_uid=uuid4(),
        created_pod_name=f"pod {count}",
        created_pod_namespace="default",
        created_node_name=f"node {count}",
        updated_at=datetime.now(timezone.utc),
    )


def mock_workload_action_obj(
    action_id=None, action_type=None, action_status=None, count=1
):
    """
    Mock a workload action object with necessary attributes.
    """
    return WorkloadAction(
        id=action_id or "123e4567-e89b-12d3-a456-426614174000",
        action_type=action_type or WorkloadActionTypeEnum.CREATE,
        action_status=action_status or WorkloadActionStatusEnum.PENDING,
        action_start_time=datetime.now(timezone.utc),
        action_end_time=None,
        action_reason=f"Test reason {count}",
        pod_parent_name=f"parent {count}",
        pod_parent_type=PodParentTypeEnum.DEPLOYMENT,
        pod_parent_uid=uuid4(),
        created_pod_name=f"pod {count}",
        created_pod_namespace="default",
        created_node_name=f"node {count}",
        deleted_pod_name=None,
        deleted_pod_namespace=None,
        deleted_node_name=None,
        bound_pod_name=None,
        bound_pod_namespace=None,
        bound_node_name=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def mock_alert_create_request_obj(
    alert_type=AlertType.ABNORMAL, pod_id=None, node_id=None
):
    """
    Mock an alert creation object with necessary attributes.
    """
    if alert_type is AlertType.NETWORK_ATTACK:
        return AlertCreateRequest(
            alert_type=alert_type,
            alert_level="Warning",
            alert_model="TestModel",
            alert_description="Test alert",
            source_ip="192.168.1.1",
            source_port=1234,
            destination_ip="192.168.1.2",
            destination_port=80,
            protocol="TCP",
            pod_id=pod_id or "11111111-1111-1111-1111-111111111111",
        )
    return AlertCreateRequest(
        alert_type=alert_type,
        alert_level="Warning",
        alert_model="TestModel",
        alert_description="Test alert",
        pod_id=pod_id or "11111111-1111-1111-1111-111111111111",
        pod_name="agent-644d8b675-jfxw8",
        node_id=node_id or "22222222-2222-2222-2222-222222222222",
        node_name="ip-172-31-33-42.us-west-2.compute.internal",
    )


def mock_alert_create_request_data(
    alert_type=AlertType.ABNORMAL, pod_id=None, node_id=None
):
    """
    Mock an alert creation request data dictionary with necessary attributes.
    """
    if alert_type is AlertType.NETWORK_ATTACK:
        return {
            "alert_type": alert_type,
            "alert_level": "Warning",
            "alert_model": "TestModel",
            "alert_description": "Test alert",
            "source_ip": "192.168.1.1",
            "source_port": 1234,
            "destination_ip": "192.168.1.2",
            "destination_port": 80,
            "protocol": "TCP",
            "pod_id": pod_id or "11111111-1111-1111-1111-111111111111",
            "pod_name": "agent-644d8b675-jfxw8",
            "node_id": node_id or "22222222-2222-2222-2222-222222222222",
            "node_name": "ip-172-31-33-42.us-west-2.compute.internal",
        }
    return {
        "alert_type": alert_type,
        "alert_level": "Warning",
        "alert_model": "TestModel",
        "alert_description": "Test alert",
        "pod_id": pod_id or "11111111-1111-1111-1111-111111111111",
        "node_id": node_id or "22222222-2222-2222-2222-222222222222",
        "pod_name": "agent-644d8b675-jfxw8",
        "node_name": "ip-172-31-33-42.us-west-2.compute.internal",
        "source_ip": "192.168.1.1",
        "source_port": 1234,
        "destination_ip": "192.168.1.2",
        "destination_port": 80,
        "protocol": "TCP",
    }


def mock_alert_response_obj(alert_type=AlertType.ABNORMAL):
    """
    Mock an alert response object with necessary attributes.
    """
    return AlertResponse(
        id=1,
        alert_type=alert_type,
        alert_level="Warning",
        alert_model="TestModel",
        alert_description="Test alert",
        pod_id="11111111-1111-1111-1111-111111111111",
        node_id="22222222-2222-2222-2222-222222222222",
        pod_name="agent-644d8b675-jfxw8",
        node_name="ip-172-31-33-42.us-west-2.compute.internal",
        source_ip="192.168.1.1",
        source_port=1234,
        destination_ip="192.168.1.2",
        destination_port=80,
        protocol="TCP",
        created_at=datetime.now(timezone.utc),
    )


def mock_alert_obj(alert_type=AlertType.ABNORMAL, pod_id=None, node_id=None):
    """
    Mock an alert object with necessary attributes.
    """
    return Alert(
        id=1,
        alert_type=alert_type,
        alert_model="TestModel",
        alert_level="Warning",
        alert_description="Test alert",
        pod_id=pod_id or "11111111-1111-1111-1111-111111111111",
        node_id=node_id or "22222222-2222-2222-2222-222222222222",
        pod_name="agent-644d8b675-jfxw8",
        node_name="ip-172-31-33-42.us-west-2.compute.internal",
        source_ip="192.168.1.1",
        source_port=1234,
        destination_ip="192.168.1.2",
        destination_port=80,
        protocol="TCP",
        created_at=datetime.now(timezone.utc),
    )


def mock_workload_request_decision_create() -> WorkloadRequestDecisionCreate:
    """ "mock data for WorkloadRequestDecisionCreate."""
    return WorkloadRequestDecisionCreate(
        pod_id=uuid4(),
        pod_name="test-pod",
        namespace="default",
        node_id=uuid4(),
        node_name="node-01",
        action_type=WorkloadActionTypeEnum.CREATE,
        is_elastic=True,
        queue_name="queue-x",
        demand_cpu=0.5,
        demand_memory=256,
        demand_slack_cpu=0.1,
        demand_slack_memory=64,
        decision_status=WorkloadRequestDecisionStatusEnum.SUCCEEDED,
        pod_parent_id=uuid4(),
        pod_parent_name="controller",
        pod_parent_kind=PodParentTypeEnum.DEPLOYMENT,
        decision_start_time="2024-07-01T12:00:00Z",
        decision_end_time="2024-07-01T12:00:00Z",
        created_at="2024-07-01T12:00:00Z",
        deleted_at=None,
    )


def mock_mock_workload_request_decision_api():
    """ "Test data for testing API."""
    return {
        "pod_id": str(uuid4()),
        "pod_name": "test-pod",
        "namespace": "default",
        "node_id": str(uuid4()),
        "node_name": "node-1",
        "action_type": WorkloadActionTypeEnum.CREATE,
        "is_elastic": True,
        "queue_name": "queue-A",
        "demand_cpu": 1.0,
        "demand_memory": 512.0,
        "demand_slack_cpu": 0.5,
        "demand_slack_memory": 128.0,
        "decision_status": WorkloadRequestDecisionStatusEnum.SUCCEEDED,
        "pod_parent_id": str(uuid4()),
        "pod_parent_name": "controller-1",
        "pod_parent_kind": PodParentTypeEnum.DEPLOYMENT,
        "decision_start_time": "2024-07-01T12:00:00Z",
        "decision_end_time": "2024-07-01T12:00:00Z",
        "created_at": TEST_DATE.isoformat(),
        "deleted_at": None,
    }


def mock_cluster_info_api():
    """Mock a cluster info object similar to what get_basic_cluster_info returns."""
    # Each node should have 'usage' and 'allocatable' keys with cpu/memory strings
    nodes = [
        {
            "usage": {"cpu": "1000m", "memory": "1024Mi"},
            "allocatable": {"cpu": "2000m", "memory": "2048Mi"},
        },
        {
            "usage": {"cpu": "500m", "memory": "512Mi"},
            "allocatable": {"cpu": "1000m", "memory": "1024Mi"},
        },
    ]
    return {
        "cluster_id": "test-cluster-id",
        "cluster_name": "test-cluster",
        "nodes": nodes,
        "pods": [
            {"name": "pod1", "namespace": "default"},
            {"name": "pod2", "namespace": "kube-system"},
            {"name": "pod3", "namespace": "kube-system"},
        ],
    }

def unpack_flow_filters(flow_filters: dict):
    """
    Return (decision_id, action_id, pod_name, namespace, node_name, action_type)
    from a flow_filters dict (values may be None).
    """
    return (
        flow_filters.get("decision_id"),
        flow_filters.get("action_id"),
        flow_filters.get("pod_name"),
        flow_filters.get("namespace"),
        flow_filters.get("node_name"),
        flow_filters.get("action_type"),
    )

def mock_workload_decision_action_flow_item(
    flow_filters: dict,
) -> WorkloadDecisionActionFlowItem:
    """Mock a workload decision action flow item."""
    create_types = {
        WorkloadActionTypeEnum.CREATE,
        WorkloadActionTypeEnum.MOVE,
        WorkloadActionTypeEnum.SWAP_X,
        WorkloadActionTypeEnum.SWAP_Y,
    }
    (
        decision_id,
        action_id,
        pod_name,
        namespace,
        node_name,
        action_type,
    ) = unpack_flow_filters(flow_filters)
    return WorkloadDecisionActionFlowItem(
        decision_id=decision_id if decision_id else uuid4(),
        action_id=action_id if action_id else uuid4(),
        action_type=action_type,
        decision_pod_name=pod_name,
        decision_namespace=namespace,
        decision_node_name=node_name,
        created_pod_name=pod_name if action_type in create_types else None,
        created_pod_namespace=namespace if action_type in create_types else None,
        created_node_name=node_name if action_type in create_types else None,
        deleted_pod_name=(
            pod_name if action_type == WorkloadActionTypeEnum.DELETE else None
        ),
        deleted_pod_namespace=(
            namespace if action_type == WorkloadActionTypeEnum.DELETE else None
        ),
        deleted_node_name=(
            node_name if action_type == WorkloadActionTypeEnum.DELETE else None
        ),
        bound_pod_name=pod_name if action_type == WorkloadActionTypeEnum.BIND else None,
        bound_pod_namespace=(
            namespace if action_type == WorkloadActionTypeEnum.BIND else None
        ),
        bound_node_name=(
            node_name if action_type == WorkloadActionTypeEnum.BIND else None
        ),
        decision_status=WorkloadRequestDecisionStatusEnum.SUCCEEDED,
        action_status=WorkloadActionStatusEnum.SUCCEEDED,
        decision_start_time=datetime.now(timezone.utc),
        decision_end_time=datetime.now(timezone.utc),
        action_start_time=datetime.now(timezone.utc),
        action_end_time=datetime.now(timezone.utc),
        decision_duration=timedelta(seconds=10),
        action_duration=timedelta(seconds=5),
        total_duration=timedelta(seconds=15),
        decision_created_at=datetime.now(timezone.utc),
        decision_deleted_at=None,
        action_created_at=datetime.now(timezone.utc),
        action_updated_at=datetime.now(timezone.utc),
        is_elastic=True,
        queue_name="queue-x",
        demand_cpu=0.5,
        demand_memory=256,
        demand_slack_cpu=0.1,
        demand_slack_memory=64,
        decision_pod_parent_id=uuid4(),
        decision_pod_parent_name="controller",
        decision_pod_parent_kind=PodParentTypeEnum.DEPLOYMENT,
        action_pod_parent_name="controller",
        action_pod_parent_type=PodParentTypeEnum.DEPLOYMENT,
        action_pod_parent_uid=uuid4(),
        action_reason="Test reason",
    )


def mock_workload_decision_action_flow_data(
    flow_filters: dict
):
    """Mock a workload decision action flow item as a dictionary."""
    item = mock_workload_decision_action_flow_item(
        flow_filters=flow_filters
    )
    return to_jsonable(
        item.model_dump()
    )  # Convert to dict with JSON-serializable values
