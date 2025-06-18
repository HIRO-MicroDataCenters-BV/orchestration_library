import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import logging

from app.repositories.k8s.k8s_get_token import get_read_only_token

router = APIRouter(prefix="/dummy_aces_ui")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DASHBOARD_ACCESS_URL = os.getenv(
    "DASHBOARD_ACCESS_URL",
    #"http://aces-dashboard-reverse-proxy.aces-kubernetes-dashboard.svc.cluster.local/k8s/dashboard",
    "http://localhost:8080/k8s/dashboard/", # Port forwarded to local port 8080 of the reverse proxy
)

DASHBOARD_NAMESPACE = os.getenv(
    "KUBERNETES_DASHBOARD_NAMESPACE", "aces-kubernetes-dashboard"
)
SERVICE_ACCOUNT_NAME = os.getenv(
    "KUBERNETES_DASHBOARD_SERVICE_ACCOUNT_NAME", "readonly-user"
)


async def get_dashboard_token():
    token_data = get_read_only_token(
        namespace=DASHBOARD_NAMESPACE,
        service_account_name=SERVICE_ACCOUNT_NAME,
    )
    if hasattr(token_data, "body"):
        import json

        return json.loads(token_data.body.decode()).get("token")
    return token_data.get("token")

@router.get("/", response_class=HTMLResponse)
async def root():
    token = await get_dashboard_token()
    if not token:
        return HTMLResponse("Failed to get token", status_code=500)
    html_content = f"""
<!DOCTYPE html>
<html>
<head><title>K8s Dashboard Auto Login</title></head>
<body>
    <h3>K8s Dashboard Auto Login</h3>
    <button onclick="loginToDashboard()">Open Dashboard</button>

    <script>
        function loginToDashboard() {{
            // Set token as cookie
            document.cookie = "auth_token={token}; path=/k8s/dashboard/";

            // Redirect
            window.open("{DASHBOARD_ACCESS_URL}", "_blank");
        }}
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
