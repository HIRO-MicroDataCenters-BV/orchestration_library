from fastapi import APIRouter
from app.kubernetes_info import list_pods


router = APIRouter(prefix="/kubernetes")
@router.get("/")
def list_all_pods():
    return list_pod_for_all_namespaces()