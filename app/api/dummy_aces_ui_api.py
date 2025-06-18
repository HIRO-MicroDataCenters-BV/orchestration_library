"""
Dummy API for ACES UI to auto-login to Kubernetes Dashboard
This API provides a simple HTML page with a button to open the Kubernetes Dashboard.

Its goinng to be deleted in the future, but is useful for testing purposes.
"""

import os
import json
import logging
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.repositories.k8s.k8s_get_token import get_read_only_token

router = APIRouter(prefix="/dummy_aces_ui")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DASHBOARD_ACCESS_URL = os.getenv(
    "DASHBOARD_ACCESS_URL",
    # "http://aces-dashboard-reverse-proxy.aces-kubernetes-dashboard.svc.cluster.local/",
    "http://localhost:8080/",  # Port forwarded to local port 8080 of the reverse proxy
)

DASHBOARD_NAMESPACE = os.getenv(
    "KUBERNETES_DASHBOARD_NAMESPACE", "aces-kubernetes-dashboard"
)
SERVICE_ACCOUNT_NAME = os.getenv(
    "KUBERNETES_DASHBOARD_SERVICE_ACCOUNT_NAME", "readonly-user"
)


async def get_dashboard_token():
    """
    Get a read-only token for the Kubernetes Dashboard service account.
    This function retrieves the token for the service account specified 
    in the environment variables.
    Returns:
        str: The read-only token for the Kubernetes Dashboard service account.
    """
    token_data = get_read_only_token(
        namespace=DASHBOARD_NAMESPACE,
        service_account_name=SERVICE_ACCOUNT_NAME,
    )
    if hasattr(token_data, "body"):
        return json.loads(token_data.body.decode()).get("token")
    if isinstance(token_data, dict):
        return token_data.get("token")
    logger.error("Unexpected token_data type: %s", type(token_data))
    return None


@router.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint that serves an HTML page with a button to 
    open the Kubernetes Dashboard.
    This endpoint generates an HTML page with a button that, when clicked, 
    sets a cookie with the read-only token
    and opens the Kubernetes Dashboard in an iframe.
    """
    token = await get_dashboard_token()
    if not token:
        return HTMLResponse("Failed to get token", status_code=500)
    html_content = f"""
<!DOCTYPE html>
<html>
<head><title>K8s Dashboard Auto Login</title></head>
<body>
    <h3>K8s Dashboard Auto Login</h3>
    <p style="color: #b00;">
        <b>Note:</b> Please port-forward the <code>aces-dashboard-reverse-proxy</code> service to <code>localhost:8080</code> for this button to work.<br>
        Example:<br>
        <code>kubectl port-forward svc/aces-dashboard-reverse-proxy -n aces-kubernetes-dashboard 8080:80</code>
    </p>
    <button onclick="loginToDashboard()">Open Dashboard</button>
    <br><br>
    <iframe id="dashboardFrame" src="" width="100%" height="800" style="display:none; border:1px solid #ccc;"></iframe>

    <script>
        function loginToDashboard() {{
            // Set token as cookie
            document.cookie = "auth_token={token}; path=/";

            // Show the iframe and set its src to the dashboard URL
            var frame = document.getElementById('dashboardFrame');
            frame.style.display = 'block';
            frame.src = "{DASHBOARD_ACCESS_URL}";
        }}
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
