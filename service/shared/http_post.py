"""HTTP POST utility functions."""
import json
import logging
import os
import httpx

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

def norm_url(url: str) -> str:
    """Normalize URL by ensuring it ends with a slash."""
    return url.rstrip("/") + "/"

async def post_json(client: httpx.AsyncClient, url: str, payload: dict) -> tuple[bool, int, str]:
    """POST JSON payload to the specified URL; return True on 2xx, else False."""
    try:
        url = norm_url(url)
        resp = await client.post(url, json=payload, timeout=10)
        logger.info("POST %s status=%s payload=%s", url, resp.status_code, payload)
        if 200 <= resp.status_code < 300:
            return (True, resp.status_code, resp.text)
        logger.error("Non-2xx %s %s", resp.status_code, resp.text)
        return (False, resp.status_code, resp.text)
    except Exception as e:
        logger.error("HTTP error posting: %s", e)
        return (False, 500, str(e))
