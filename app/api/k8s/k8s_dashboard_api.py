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

router = APIRouter(prefix="/k8s-dashboard", tags=["Kubernetes Dashboard"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DASHBOARD_NAMESPACE = os.getenv(
    "KUBERNETES_DASHBOARD_NAMESPACE", "aces-kubernetes-dashboard"
)
SERVICE_ACCOUNT_NAME = os.getenv(
    "KUBERNETES_DASHBOARD_SERVICE_ACCOUNT_NAME", "readonly-user"
)
# REVERSE_PROXY_SERVICE_NAME = os.getenv(
#     "NGINX_REVERSE_PROXY_SERVICE_NAME", "aces-dashboard-reverse-proxy"
# )

# REVERSE_PROXY_SERVICE_PORT = os.getenv("NGINX_REVERSE_PROXY_SERVICE_PORT", "80")

# DASHBOARD_ACCESS_URL = (
#     f"http://{REVERSE_PROXY_SERVICE_NAME}."
#     f"{DASHBOARD_NAMESPACE}.svc.cluster.local:"
#     f"{REVERSE_PROXY_SERVICE_PORT}/"
# )

# DASHBOARD_ACCESS_URL = "http://localhost:8080/"

DASHBOARD_ACCESS_URL = os.getenv(
    "KUBERNETES_DASHBOARD_ACCESS_URL",
    "http://localhost:30016/",
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
<head>
    <title>K8s Dashboard Auto Login</title>
    <style>
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
        }}
        body {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            height: 100vh;
        }}
        #dashboardFrame {{
            flex: 1 1 auto;
            width: 100%;
            border: 1px solid #ccc;
            display: none;
        }}
        .button-container {{
            margin-bottom: 16px;
        }}
        button {{
            display: inline-block;
            padding: 10px 24px;
            font-size: 16px;
            border-radius: 4px;
            border: 1px solid #1976d2;
            background-color: #1976d2;
            color: #fff;
            cursor: pointer;
            margin-bottom: 16px;
            width: auto;
        }}
        button:hover {{
            background-color: #1565c0;
        }}
    </style>
</head>
<body>
    <h3>K8s Dashboard Auto Login</h3>
    <div class="button-container">
        <button onclick="loginToDashboard()">Open Dashboard</button>
    </div>
    <br>
    <iframe id="dashboardFrame" src=""></iframe>

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
