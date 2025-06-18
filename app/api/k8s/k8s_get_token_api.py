"""
API to retrieve a read-only token for a specific Kubernetes service account.
"""

from fastapi import APIRouter
from app.repositories.k8s import k8s_get_token


router = APIRouter(prefix="/k8s_get_token")


@router.get("/")
def get_ro_token(namespace: str = None, service_account_name: str = None):
    """
    Get a read-only token for a specific service account in a namespace.
    If no namespace or service account name is provided, it returns an error.

    Args:
        namespace (str): The namespace of the service account.
        service_account_name (str): The name of the service account.

    Returns:
        JSONResponse: A response containing the read-only token or an error message.
    """
    return k8s_get_token.get_read_only_token(
        namespace=namespace, service_account_name=service_account_name
    )
