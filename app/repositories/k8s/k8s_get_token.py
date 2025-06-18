"""
Get a read-only token for a service account in a Kubernetes namespace.
"""

import logging
from fastapi.responses import JSONResponse
from kubernetes import client

from app.repositories.k8s.k8s_common import get_k8s_core_v1_client

logger = logging.getLogger(__name__)
DEFAULT_EXPIRATION_SECONDS = 3600  # Default token expiration time in seconds
DEFAULT_AUDIENCE = "https://kubernetes.default.svc.cluster.local"


def get_read_only_token(
    namespace: str = None, service_account_name: str = None
) -> JSONResponse:
    """
    Get a read-only token for a specific service account in a namespace.
    If no namespace or service account name is provided, it returns an error.

    Args:
        namespace (str): The namespace of the service account.
        service_account_name (str): The name of the service account.

    Returns:
        JSONResponse: A response containing the read-only token or an error message.
    """
    if not namespace or not service_account_name:
        return JSONResponse(
            status_code=400,
            content={"error": "Namespace and service account name must be provided."},
        )

    try:
        token = create_token_for_sa(namespace, service_account_name)
        return JSONResponse(content={"token": token})
    except client.exceptions.ApiException as e:
        logger.error("Kubernetes API error for %s in %s: %s", service_account_name, namespace, e)
        return JSONResponse(status_code=500, content={"error": f"Kubernetes API error: {e}"})
    except ValueError as e:
        logger.error("Value error for %s in %s: %s", service_account_name, namespace, e)
        return JSONResponse(status_code=500, content={"error": f"Value error: {e}"})


def create_token_for_sa(
    namespace: str, sa_name: str, expiration_seconds=DEFAULT_EXPIRATION_SECONDS
) -> str:
    """
    Create a read-only token for a service account in a specific namespace.
    :param namespace: The namespace of the service account.
    :param sa_name: The name of the service account.
    :param expiration_seconds: Token expiration time in seconds.
    :return: The read-only token for the specified service account.
    """
    core_v1 = get_k8s_core_v1_client()
    token_spec = client.V1TokenRequestSpec(
        audiences=[DEFAULT_AUDIENCE], expiration_seconds=expiration_seconds
    )

    token_response = core_v1.create_namespaced_service_account_token(
        name=sa_name,
        namespace=namespace,
        body={
            "apiVersion": "authentication.k8s.io/v1",
            "kind": "TokenRequest",
            "spec": token_spec.to_dict(),
        },
    )
    return token_response.status.token
