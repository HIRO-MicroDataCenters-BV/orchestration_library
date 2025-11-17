"""
Helper functions for the application.
"""
import time
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig
import asyncio

def metrics(method: str, endpoint: str) -> dict:
    """
    Create a metrics details dictionary.

    Args:
        method (str): The HTTP method.
        endpoint (str): The API endpoint.

    Returns:
        dict: A dictionary containing metrics details.
    """
    return {
        "start_time": time.time(),
        "method": method,
        "endpoint": endpoint,
    }

def publish_msg_to_nats_js(
    nats_server: str,
    stream: str,
    subject: str,
    message: str,
    timeout: int = 5,
    logger=None,
) -> None:
    """
    Publish a message to a NATS JetStream subject.

    Args:
        nats_server (str): The NATS server URL.
        stream (str): The JetStream stream name.
        subject (str): The subject to publish the message to.
        message (str): The message to publish.
        timeout (int): Timeout for publishing the message.
        logger: Logger for logging messages.

    Returns:
        None
    """
    async def _publish():
        nc = NATS()
        await nc.connect(servers=[nats_server], reconnect_time_wait=2)
        js = nc.jetstream()

        # Ensure the stream exists
        try:
            await js.stream_info(stream)
        except Exception:
            if logger:
                logger.info(f"Creating stream {stream}")
            sc = StreamConfig(name=stream, subjects=[subject])
            await js.add_stream(sc)

        # Publish the message
        await js.publish(subject, message.encode())

        await nc.drain()

    asyncio.run(asyncio.wait_for(_publish(), timeout=timeout))