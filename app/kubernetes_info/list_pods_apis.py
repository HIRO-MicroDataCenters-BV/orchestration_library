from fastapi import APIRouter
from list_pods import list_pods


router = APIRouter(prefix="/kpods")
@router.get("/list_all")
def list_all_pods():
    return list_pods.list_pod_for_all_namespaces()