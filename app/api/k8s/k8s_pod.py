"""
List pods in the cluster
"""
import logging
from fastapi import APIRouter
from kubernetes.client.exceptions import ApiException
from app.repositories.k8s import k8s_pod
from app.utils.exceptions import K8sAPIException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/k8s_pod")

# pylint: disable=invalid-name
@router.get("/")
def list_all_pods(
    namespace: str = None, name: str = None, pod_id: str = None, status: str = None
):
    """
    List all pods in the specified namespace.
    If no namespace is specified, list all pods in all namespaces.
    """
    try:
        return k8s_pod.list_k8s_pods(
            namespace=namespace, name=name, pod_id=pod_id, status=status
        )
    except ApiException as e:
        logger.error("Kubernetes API error: %s", str(e), exc_info=True)
        raise K8sAPIException(
            message="Failed to list Kubernetes pods due to API error.",
            status_code=e.status or 502,
            details={"error": e.reason}
        ) from e
    except Exception as e:
        logger.error("Unexpected error listing pods: %s", str(e), exc_info=True)
        raise K8sAPIException(
            message="Unexpected error occurred while retrieving pods.",
            details={"error": str(e)}
        ) from e
