"""
Get a read-only token for a service account in a Kubernetes namespace.
"""

import logging
from fastapi.responses import JSONResponse
from kubernetes import client
from kubernetes.config import ConfigException
from kubernetes.client.rest import ApiException

from app.repositories.k8s.k8s_common import get_k8s_core_v1_client
from app.utils.k8s import handle_k8s_exceptions

logger = logging.getLogger(__name__)
DEFAULT_EXPIRATION_SECONDS = 3600  # Default token expiration time in seconds
DEFAULT_AUDIENCE = "https://kubernetes.default.svc.cluster.local"

# Suppress R1710: All exception handlers call a function that always raises, so no return needed.
# pylint: disable=R1710
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
    try:
        if not namespace or not service_account_name:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Namespace and service account name must be provided."
                },
            )

        token = create_token_for_sa(namespace, service_account_name)
        return JSONResponse(content={"token": token})
    except ApiException as e:
        handle_k8s_exceptions(
            e,
            context_msg=f"Kubernetes API error for {service_account_name} in {namespace}",
        )
    except ConfigException as e:
        handle_k8s_exceptions(
            e,
            context_msg=f"Kubernetes configuration error for {service_account_name} in {namespace}",
        )
    except ValueError as e:
        handle_k8s_exceptions(
            e, context_msg=f"Value error for {service_account_name} in {namespace}"
        )


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
    logger.info(
        f"Generated read-only token for service account {sa_name} in namespace {namespace}"
    )
    return token_response.status.token
