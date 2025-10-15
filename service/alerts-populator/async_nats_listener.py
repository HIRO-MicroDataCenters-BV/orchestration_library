import asyncio
import logging
import os
import sys
import httpx
from nats.aio.client import Client as NATS
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
from transformations import get_transformation_func


RECONNECT_DELAY = 2       # seconds
MAX_RECONNECT_DELAY = 30  # seconds

nats_server = os.getenv("NATS_SERVER", "nats://nats:4222")
topics_list = os.getenv("NATS_TOPICS", "alerts.network-attack, alerts.abnormal")
alerts_api_url = os.getenv(
    "ALERTS_API_URL", "http://api-service.default.svc.cluster.local:8080/alerts"
)

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

async def message_handler(msg, alerts_api_url):
    """Process incoming NATS messages and forward transformed data to the alerts API."""
    alerts_api_url = alerts_api_url.rstrip("/") + "/"
    subject = msg.subject
    data = msg.data.decode()

    transform_func = get_transformation_func(subject)
    transformed_alerts = transform_func(data)

    for payload in transformed_alerts:
        if "alert_type" not in payload:
            payload["alert_type"] = "Other"
        async with httpx.AsyncClient() as client:
            response = await client.post(alerts_api_url, json=payload)
            logger.info(f"Response status: {response.status_code}, body: {response.text}")
        logger.info(f"Sent transformed data {payload} from {subject} to {alerts_api_url}")


async def connect_nats(topics, alerts_api_url):
    """Establish and maintain a NATS connection with reconnect logic."""
    reconnect_delay = RECONNECT_DELAY
    while True:
        nc = NATS()

        async def disconnected_cb():
            logger.warning("Disconnected from NATS. Attempting to reconnect...")

        async def reconnected_cb():
            logger.info(f"Reconnected to NATS at {nc.connected_url.netloc}")
            # re-subscribe after reconnect
            for topic in topics:
                await nc.subscribe(topic, cb=nats_callback)
                logger.info(f"Resubscribed to topic: {topic}")

        async def closed_cb():
            logger.error("Connection to NATS closed permanently.")

        async def nats_callback(msg):
            await message_handler(msg, alerts_api_url)

        try:
            await nc.connect(
                servers=[nats_server],
                reconnect_time_wait=reconnect_delay,
                max_reconnect_attempts=-1,  # retry indefinitely
                disconnected_cb=disconnected_cb,
                reconnected_cb=reconnected_cb,
                closed_cb=closed_cb,
                name="alerts-populator-client",
            )
            print(f"Connected to NATS server: {nats_server}")

            for topic in topics:
                await nc.subscribe(topic, cb=nats_callback)
                logger.info(f"Subscribed to topic: {topic}")

            reconnect_delay = RECONNECT_DELAY # Reset reconnect delay after successful connection

            # Keep running until disconnected
            while True:
                await asyncio.sleep(1)

        except (ConnectionClosedError, NoServersError, TimeoutError) as e:
            logger.warning(f"Connection error: {e}. Retrying in {reconnect_delay}s...")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, MAX_RECONNECT_DELAY)
            continue
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await asyncio.sleep(reconnect_delay)


async def main():
    """Main entry point to start the NATS listener."""
    logger.info("ENV Variables:")
    logger.info(f"NATS_SERVER: {nats_server}")
    logger.info(f"NATS_TOPICS: {topics_list}")
    logger.info(f"ALERTS_API_URL: {alerts_api_url}")

    topics = [topic.strip() for topic in topics_list.split(",")]

    await connect_nats(topics, alerts_api_url)


if __name__ == "__main__":
    asyncio.run(main())
