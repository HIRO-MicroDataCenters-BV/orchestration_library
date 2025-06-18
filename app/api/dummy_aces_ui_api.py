import mimetypes
import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import httpx
import logging

from app.repositories.k8s.k8s_get_token import get_read_only_token

router = APIRouter(prefix="/dummy_aces_ui")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
# DASHBOARD_HOST = os.getenv(
#     "DASHBOARD_HOST",
#     "kubernetes-dashboard-kong-proxy.kubernetes-dashboard.svc.cluster.local",
# )
# DASHBOARD_PORT = os.getenv("DASHBOARD_PORT", "80")  # Default port for HTTP dashboard
# DASHBOARD_SCHEME = os.getenv("DASHBOARD_SCHEME", "http")  # Could be https
# # DASHBOARD_PORT = os.getenv("DASHBOARD_PORT", "443")  # Default port for HTTPS dashboard
# # DASHBOARD_SCHEME = os.getenv("DASHBOARD_SCHEME", "https")  # Could be http
# DASHBOARD_BASE_URL = f"{DASHBOARD_SCHEME}://{DASHBOARD_HOST}:{DASHBOARD_PORT}"

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


# def rewrite_location(loc: str) -> str:
#     """
#     Turn upstream Location: /#/foo?bar=… or absolute URLs
#     into a path under /dummy_aces_ui/proxy/… so the browser
#     follows back through our proxy.
#     """
#     if loc.startswith("http://") or loc.startswith("https://"):
#         # absolute – just re-proxy the entire URL
#         return f"/dummy_aces_ui/proxy/{loc}"

#     # strip leading slash, encode any '#' → '%23'
#     stripped = loc.lstrip("/")
#     encoded = stripped.replace("#", "%23")
#     return f"/dummy_aces_ui/proxy/{encoded}"


# @router.api_route(
#     "/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
# )
# async def reverse_proxy(request: Request, path: str = ""):
#     try:
#         token = await get_dashboard_token()
#         if not token:
#             return HTMLResponse("Failed to get token", status_code=500)

#         # Build full URL
#         target_url = f"{DASHBOARD_BASE_URL}/{path}"
#         if request.query_params:
#             target_url += f"?{request.query_params}"

#         logger.info(f"Proxying request to: {target_url}")

#         # Build request headers
#         headers = {"Authorization": f"Bearer {token}", "Connection": "close"}
#         for key, value in request.headers.items():
#             if key.lower() not in ["host", "content-length", "transfer-encoding"]:
#                 headers[key] = value

#         body = await request.body()

#         # These will be bound once streaming starts
#         response_headers = {}
#         status_code = 200
#         media_type = None

#         async def proxy_stream():
#             nonlocal status_code, response_headers, media_type
#             # Use httpx.AsyncClient to stream the response
#             async with httpx.AsyncClient(
#                 verify=False, follow_redirects=False
#             ) as client:
#                 # response = await client.request(
#                 #     method=request.method,
#                 #     url=target_url,
#                 #     headers=headers,
#                 #     content=body,
#                 #     timeout=None,
#                 # )
#                 # return StreamingResponse(
#                 #     response.aiter_raw(),
#                 #     status_code=response.status_code,
#                 #     headers={
#                 #         k: v
#                 #         for k, v in response.headers.items()
#                 #         if k.lower() not in ("content-length", "transfer-encoding")
#                 #     },
#                 #     media_type=response.headers.get("content-type"),
#                 # )

#                 async with client.stream(
#                     method=request.method,
#                     url=target_url,
#                     headers=headers,
#                     content=body,
#                     timeout=None,
#                 ) as response:
#                     status_code = response.status_code
#                     response_headers = {
#                         k: v
#                         for k, v in response.headers.items()
#                         if k.lower() not in ("content-length", "transfer-encoding")
#                     }
#                     media_type = response.headers.get("content-type")
#                     if not media_type:
#                         guessed_type, _ = mimetypes.guess_type(target_url)
#                         media_type = guessed_type or "application/octet-stream"
#                     # response.aiter_raw(),  # Ensures proper streaming
#                     # 2) if it’s a redirect, rewrite Location
#                     if 300 <= status_code < 400 and "location" in response_headers:
#                         response_headers["location"] = rewrite_location(
#                             response_headers["location"]
#                         )
#                     # forward raw bytes as they arrive
#                     async for chunk in response.aiter_bytes():
#                         yield chunk

#         # Now returning the streaming response **while** the context manager is still open
#         return StreamingResponse(
#             proxy_stream(),
#             status_code=status_code,
#             headers=response_headers,
#             media_type=media_type,
#         )
#     except Exception as e:
#         logger.error(f"Proxy error: {str(e)}", exc_info=True)
#         return HTMLResponse(f"Proxy error: {str(e)}", status_code=500)


# @router.get("/", response_class=HTMLResponse)
# async def dashboard_ui():
#     """Simple UI with button to access dashboard"""
#     launch_url = "/dummy_aces_ui/proxy/#!/overview?namespace=default"
#     dashboard_entry_url = "/dummy_aces_ui/proxy/"
#     token = await get_dashboard_token()
#     login_js = f"""
#     async function loginToDashboard() {{
#     try {{
#         const response = await fetch("{dashboard_entry_url}", {{
#             method: "GET",
#                 headers: {{
#                     "Authorization": "Bearer {token}"
#                 }}
#             }});
#             if (!response.ok) {{
#                 throw new Error("Failed to validate token");
#             }}
#         }} catch (e) {{
#             document.body.innerHTML = "<h3>Login Failed</h3><p>" + e.message + "</p>";
#             return;
#         }}
#         window.location.href = "{launch_url}";
#     }}
#     """
#     html_content = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>K8s Dashboard Auto-Login</title>
#         <style>
#             body {{ font-family: Arial, sans-serif; margin: 40px; }}
#             .container {{ max-width: 600px; margin: 0 auto; }}
#             button {{
#                 padding: 12px 24px;
#                 font-size: 16px;
#                 background-color: #326ce5;
#                 color: white;
#                 border: none;
#                 border-radius: 4px;
#                 cursor: pointer;
#                 transition: background-color 0.3s;
#             }}
#             button:hover {{ background-color: #2a5bc7; }}
#         </style>
#     </head>
#     <body>
#         <script>
#         {login_js}
#         </script>
#         <div class="container">
#             <h2>Kubernetes Dashboard Auto-Login</h2>
#             <p>Click below to automatically authenticate with the dashboard:</p>
#             button onclick="window.open('{launch_url}', '_blank')">
#                 Open Authenticated Dashboard
#             </button>
#         </div>
#     </body>
#     </html>
#     """
#     return HTMLResponse(content=html_content)

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
        <a href="http://aces-dashboard-reverse-proxy.aces-kubernetes-dashboard.svc.cluster.local/k8s/dashboard?token={token}" target="_blank">
            <button>Open Dashboard</button>
        </a>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
