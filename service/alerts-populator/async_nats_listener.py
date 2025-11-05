import asyncio
import logging
import os
import httpx
from nats.aio.client import Client as NATS
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
from transformations import get_transformation_func


RECONNECT_DELAY = 2  # seconds
MAX_RECONNECT_DELAY = 30  # seconds
MAX_REDELIVERIES = 5  # max redeliveries for JetStream messages

nats_server = os.getenv("NATS_SERVER", "nats://nats:4222")
nats_js_stream = os.getenv("NATS_JS_STREAM", "PREDICTIONS")
nats_js_subjects = os.getenv("NATS_JS_SUBJECTS", "anomalies")
nats_js_durable = os.getenv("NATS_JS_DURABLE", "alerts-populator")
# topics_list = os.getenv("NATS_TOPICS", "alerts.network-attack, alerts.abnormal")
alerts_api_url = os.getenv(
    "ALERTS_API_URL", "http://api-service.default.svc.cluster.local:8080/alerts"
)

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def _norm_alerts_url(url: str) -> str:
    return url.rstrip("/") + "/"


async def post_alert(client: httpx.AsyncClient, url: str, payload: dict) -> bool:
    try:
        if payload is None or (
            payload.get("pod_id") is None
            and payload.get("pod_name") is None
            and payload.get("node_id") is None
            and payload.get("node_name") is None
            and payload.get("source_ip") is None
            and payload.get("destination_ip") is None
            and payload.get("source_port") is None
            and payload.get("destination_port") is None
        ):
            logger.error("Ignoring alert with insufficient data: %s", payload)
            return True
        resp = await client.post(url, json=payload, timeout=10)
        logger.info("POST %s status=%s payload=%s", url, resp.status_code, payload)
        if 200 <= resp.status_code < 300:
            return True
        logger.error("Non-2xx from API: %s %s", resp.status_code, resp.text)
        return False
    except Exception as e:
        logger.error("HTTP error posting alert: %s", e)
        return False


async def handle_js_message(
    msg, alerts_api_url: str, http_client: httpx.AsyncClient
) -> bool:
    """Transform and forward a JetStream message; return True to ack, False to redeliver."""
    subject = msg.subject
    data = msg.data.decode()

    transform = get_transformation_func(subject)
    transformed_alerts = transform(data)

    # Expect a list of dicts; if single dict, normalize to list
    # if isinstance(transformed_alerts, dict):
    #     transformed_alerts = [transformed_alerts]
    if not isinstance(transformed_alerts, list):
        logger.error(
            "Transformer returned unexpected type: %s", type(transformed_alerts)
        )
        return False

    api_url = _norm_alerts_url(alerts_api_url)
    all_ok = True
    for payload in transformed_alerts:
        if "alert_type" not in payload:
            payload["alert_type"] = "Other"
        ok = await post_alert(http_client, api_url, payload)
        all_ok = all_ok and ok
    return all_ok


async def run_jetstream_consumer(nc: NATS, alerts_api_url: str):
    """Create a durable JetStream subscription and process messages with manual ack."""
    js = nc.jetstream()
    subjects = [subj.strip() for subj in nats_js_subjects.split(",")]

    # Single long‑lived HTTP client
    http_client = httpx.AsyncClient(follow_redirects=True)

    async def js_callback(msg):
        attempts = getattr(getattr(msg, "metadata", None), "num_delivered", 1)
        ok = await handle_js_message(msg, alerts_api_url, http_client)
        if ok:
            await msg.ack()
            logger.debug("Acked message on %s (attempt %s)", msg.subject, attempts)
        else:
            if attempts < MAX_REDELIVERIES:
                await msg.nak()  # redeliver with default policy
                logger.warning("NAK message on %s (attempt %s)", msg.subject, attempts)
            else:
                # Stop further redelivery to avoid poison message loop
                await msg.term()
                logger.error(
                    "Terminated message on %s after %s attempts", msg.subject, attempts
                )

    async def ensure_subscription(subject: str):
        # Create/attach durable consumer; manual_ack ensures we control acking
        durable = f"{nats_js_durable}-{subject.replace('.', '_')}"
        attempt = 0
        while True:
            attempt += 1
            try:
                sub = await js.subscribe(
                    subject,
                    stream=nats_js_stream,
                    durable=durable,
                    manual_ack=True,
                    cb=js_callback,
                    deliver_policy="all",
                )
                logger.info(
                    "JetStream subscribed: stream=%s subject=%s durable=%s",
                    nats_js_stream,
                    subject,
                    durable,
                )
                return sub
            except Exception as e:
                msg = str(e)
                if "consumer is already bound" in msg.lower():
                    logger.warning(
                        "Bind error durable=%s: %s; deleting then retrying",
                        durable,
                        msg,
                    )
                    try:
                        await js.delete_consumer(nats_js_stream, durable)
                        logger.info("Deleted durable=%s after bind error", durable)
                    except Exception as de:
                        logger.warning("Delete failed durable=%s: %s", durable, de)
                    await asyncio.sleep(1)
                    continue
                logger.error(
                    "Subscribe error subject=%s attempt=%s: %s", subject, attempt, msg
                )
                await asyncio.sleep(min(5, attempt))
                continue

    for subject in subjects:
        await ensure_subscription(subject)

    await nc.flush()

    try:
        # Keep the subscription alive
        while True:
            await asyncio.sleep(1)
    finally:
        await http_client.aclose()


async def main():
    """Main entry point to start the NATS listener."""
    logger.info("ENV Variables:")
    logger.info(f"NATS_SERVER: {nats_server}")
    # logger.info(f"NATS_TOPICS: {topics_list}")
    logger.info(f"NATS_JS_STREAM: {nats_js_stream}")
    logger.info(f"NATS_JS_SUBJECT: {nats_js_subjects}")
    logger.info(f"NATS_JS_DURABLE: {nats_js_durable}")
    logger.info(f"ALERTS_API_URL: {alerts_api_url}")
    logger.info(f"MAX_REDELIVERIES: {MAX_REDELIVERIES}")

    # topics = [topic.strip() for topic in topics_list.split(",")]

    while True:
        reconnect_delay = RECONNECT_DELAY
        nc = NATS()

        async def disconnected_cb():
            logger.warning("NATS disconnected; attempting reconnect...")

        async def reconnected_cb():
            logger.info("Reconnected to NATS at %s", nc.connected_url.netloc)

        async def closed_cb():
            logger.error("NATS connection closed.")

        try:
            await nc.connect(
                servers=[nats_server],
                allow_reconnect=True,
                reconnect_time_wait=reconnect_delay,
                max_reconnect_attempts=-1,
                disconnected_cb=disconnected_cb,
                reconnected_cb=reconnected_cb,
                closed_cb=closed_cb,
                name="alerts-populator-js-client",
                connect_timeout=10,
                ping_interval=10,
                max_outstanding_pings=5,
            )
            logger.info("Connected to NATS: %s", nats_server)

            # Run JetStream consumer until connection drops
            await run_jetstream_consumer(nc, alerts_api_url)

            # If run_jetstream_consumer returns, loop to reconnect
            reconnect_delay = RECONNECT_DELAY

        except (ConnectionClosedError, NoServersError, TimeoutError) as e:
            logger.warning("NATS error: %s; retry in %ss", e, reconnect_delay)
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, MAX_RECONNECT_DELAY)
            continue
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            await asyncio.sleep(reconnect_delay)


if __name__ == "__main__":
    asyncio.run(main())
