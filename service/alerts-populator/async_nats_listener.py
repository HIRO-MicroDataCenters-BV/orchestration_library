"""Asynchronous NATS JetStream listener for alerts populator service."""
import asyncio
import logging
import os
import httpx
from shared.js_forwarder import JetStreamForwarder
from shared.http_post import post_json, norm_url
from transformations import get_transformation_func

MAX_REDELIVERIES = int(os.getenv("MAX_REDELIVERIES", "5"))
INIT_RECONNECT_DELAY = int(os.getenv("INIT_RECONNECT_DELAY", "2"))
MAX_RECONNECT_DELAY = int(os.getenv("MAX_RECONNECT_DELAY", "30"))
NATS_SERVER = os.getenv("NATS_SERVER", "nats://nats:4222")
NATS_JS_STREAM = os.getenv("NATS_JS_STREAM", "PREDICTIONS")
NATS_JS_SUBJECTS = [
    s.strip() for s in os.getenv("NATS_JS_SUBJECTS", "anomalies").split(",")
]
NATS_JS_DURABLE = os.getenv("NATS_JS_DURABLE", "alerts-populator")
ALERTS_API_URL = os.getenv(
    "ALERTS_API_URL", "http://api-service.default.svc.cluster.local:8080/alerts"
)

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


async def handler(subject: str, data_bytes: bytes, attempt: int) -> bool:
    """Handle incoming NATS message."""
    logger.info("Handling message for subject: %s", subject)
    data = data_bytes.decode()
    transform = get_transformation_func(subject)
    payloads = transform(data)
    if not isinstance(payloads, list):
        logger.error("Transformer returned non-list: %s", type(payloads))
        return False
    async with httpx.AsyncClient(follow_redirects=True) as client:
        all_ok = True
        for p in payloads:
            if "alert_type" not in p:
                p["alert_type"] = "Other"
            ok = await post_json(client, ALERTS_API_URL, p)
            all_ok = all_ok and ok
        return all_ok


async def main():
    """Main entry point."""
    logger.info("ENV Variables:")
    logger.info(f"NATS_SERVER: {NATS_SERVER}")
    logger.info(f"NATS_JS_STREAM: {NATS_JS_STREAM}")
    logger.info(f"NATS_JS_SUBJECT: {NATS_JS_SUBJECTS}")
    logger.info(f"NATS_JS_DURABLE: {NATS_JS_DURABLE}")
    logger.info(f"ALERTS_API_URL: {ALERTS_API_URL}")
    logger.info(f"MAX_REDELIVERIES: {MAX_REDELIVERIES}")
    logger.info(f"INIT_RECONNECT_DELAY: {INIT_RECONNECT_DELAY}")
    logger.info(f"MAX_RECONNECT_DELAY: {MAX_RECONNECT_DELAY}")

    forwarder = JetStreamForwarder(
        nats_server=NATS_SERVER,
        stream=NATS_JS_STREAM,
        subjects=NATS_JS_SUBJECTS,
        durable_prefix=NATS_JS_DURABLE,
        max_redeliveries=MAX_REDELIVERIES,
        init_reconnect_delay=INIT_RECONNECT_DELAY,
        max_reconnect_delay=MAX_RECONNECT_DELAY,
        handler=handler,
    )
    await forwarder.run()


if __name__ == "__main__":
    asyncio.run(main())
