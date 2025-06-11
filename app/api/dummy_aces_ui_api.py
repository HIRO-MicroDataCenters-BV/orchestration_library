import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.repositories.k8s.k8s_get_token import get_read_only_token

router = APIRouter(prefix="/dummy_aces_ui")

K8S_DASHBOARD_NAMESPACE = os.getenv(
    "KUBERNETES_DASHBOARD_NAMESPACE", "kubernetes-dashboard"
)
K8S_DASHBOARD_SERVICE_ACCOUNT_NAME = os.getenv(
    "KUBERNETES_DASHBOARD_SERVICE_ACCOUNT_NAME", "readonly-user"
)
K8S_DASHBOARD_PROXY_SERVICE_NAME = os.getenv(
    "KUBERNETES_DASHBOARD_PROXY_SERVICE_NAME", "kubernetes-dashboard-kong-proxy"
)
K8S_DASHBOARD_PROXY_SERVICE_PORT = os.getenv(
    "KUBERNETES_DASHBOARD_PROXY_SERVICE_PORT", "8443"
)
K8S_DASHBOARD_PROXY_URL = os.getenv(
    "K8S_DASHBOARD_PROXY_URL", "https://localhost:8443"
)  # Replace with real FQDN


# Dummy implementation of k8s_get_token
@router.get("/dummy_get_token")
async def k8s_get_token():
    return get_read_only_token(
        namespace=K8S_DASHBOARD_NAMESPACE,
        service_account_name=K8S_DASHBOARD_SERVICE_ACCOUNT_NAME,
    )


@router.get("/", response_class=HTMLResponse)
async def root():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <h3>K8s Dashboard Auto Login</h3>
        <button onclick="getTokenAndOpenUrl()">Open Dashboard</button>
        <script>
            async function getTokenAndOpenUrl() {{
            try {{
                const response = await fetch('/dummy_aces_ui/dummy_get_token');
                if (!response.ok) {{
                    alert("Failed to fetch token: " + response.statusText);
                    return;
                }}
                const data = await response.json();
                const token = data.token;
                if (!token) {{
                    alert("No token received.");
                    return;
                }}
                const dashboardUrl = '{K8S_DASHBOARD_PROXY_URL}/#/login?token=' + encodeURIComponent(token);
                window.open(dashboardUrl, '_blank');
            }} catch (err) {{
                console.error("Failed to fetch token or open dashboard:", err);
                alert("Error occurred: " + err.message);
            }}
        }}
        </script>
    </head>
    <body>
        <h1>Get K8s Token</h1>
        <button onclick="getTokenAndOpenUrl()">Get Token and Open URL</button>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
