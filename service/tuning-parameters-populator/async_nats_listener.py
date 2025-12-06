"""Asynchronous NATS JetStream listener for alerts populator service."""

import asyncio
import logging
import os

from shared.js_forwarder import JetStreamForwarder, make_post_api_handler


MAX_REDELIVERIES = int(os.getenv("MAX_REDELIVERIES", "5"))
INIT_RECONNECT_DELAY = int(os.getenv("INIT_RECONNECT_DELAY", "2"))
MAX_RECONNECT_DELAY = int(os.getenv("MAX_RECONNECT_DELAY", "30"))
MAX_CONCURRENT_MSGS = int(os.getenv("MAX_CONCURRENT_MSGS", "5"))
MAX_ACK_WAIT_SECONDS = int(os.getenv("MAX_ACK_WAIT_SECONDS", "30"))

NATS_SERVER = os.getenv("NATS_SERVER", "nats://nats:4222")
NATS_JS_STREAM = os.getenv("NATS_JS_STREAM", "TUNING")
NATS_JS_SUBJECTS = [
    s.strip() for s in os.getenv("NATS_JS_SUBJECTS", "tuning.raw").split(",")
]
NATS_JS_DURABLE = os.getenv("NATS_JS_DURABLE", "tuning-params-populator")
TUNING_PARAMETERS_API_URL = os.getenv(
    "TUNING_PARAMETERS_API_URL",
    "http://api-service.default.svc.cluster.local:8080/tuning_parameters",
)

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


async def main():
    """Main entry point."""
    logger.info("ENV Variables:")
    logger.info(f"NATS_SERVER: {NATS_SERVER}")
    logger.info(f"NATS_JS_STREAM: {NATS_JS_STREAM}")
    logger.info(f"NATS_JS_SUBJECT: {NATS_JS_SUBJECTS}")
    logger.info(f"NATS_JS_DURABLE: {NATS_JS_DURABLE}")
    logger.info(f"TUNING_PARAMS_API_URL: {TUNING_PARAMETERS_API_URL}")
    logger.info(f"MAX_REDELIVERIES: {MAX_REDELIVERIES}")
    logger.info(f"INIT_RECONNECT_DELAY: {INIT_RECONNECT_DELAY}")
    logger.info(f"MAX_RECONNECT_DELAY: {MAX_RECONNECT_DELAY}")
    logger.info(f"MAX_CONCURRENT_MSGS: {MAX_CONCURRENT_MSGS}")
    logger.info(f"MAX_ACK_WAIT_SECONDS: {MAX_ACK_WAIT_SECONDS}")

    forwarder = JetStreamForwarder(
        nats_server=NATS_SERVER,
        stream=NATS_JS_STREAM,
        subjects=NATS_JS_SUBJECTS,
        durable_prefix=NATS_JS_DURABLE,
        max_redeliveries=MAX_REDELIVERIES,
        init_reconnect_delay=INIT_RECONNECT_DELAY,
        max_reconnect_delay=MAX_RECONNECT_DELAY,
        max_concurrent_msgs=MAX_CONCURRENT_MSGS,
        max_ack_wait_seconds=MAX_ACK_WAIT_SECONDS,
        handler=make_post_api_handler(TUNING_PARAMETERS_API_URL, NATS_JS_STREAM),
    )
    await forwarder.run()


if __name__ == "__main__":
    asyncio.run(main())
