"""
Helper functions for the application.
"""

import asyncio
import json
import logging
import time
from traceback import print_exception
from typing import Any
from httpx import Response
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig
from nats.js.errors import NotFoundError, Error as JetStreamError
from nats.errors import Error as NATSError
import requests

logger = logging.getLogger(__name__)


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


async def publish_msg_to_nats_js(
    nats_details: dict, message: Any, timeout: int = 5
) -> None:
    """
    Publish a message to a NATS JetStream subject.

    Args:
        nats_details (dict): Dictionary containing NATS connection details:
            nats_server (str): The NATS server URL.
            stream (str): The JetStream stream name.
            subject (str): The subject to publish the message to.
        message (Any): The message to publish.
        timeout (int): Timeout for publishing the message.
        logger: Logger for logging messages.

    Returns:
        None
    """
    nats_server = nats_details.get("nats_server")
    stream = nats_details.get("stream")
    subject = nats_details.get("subject")
    logger.info(
        "Publishing message to NATS JetStream: server=%s, stream=%s, subject=%s",
        nats_server,
        stream,
        subject,
    )
    # Normalize message to string
    try:
        if isinstance(message, str):
            msg_str = message
        elif hasattr(message, "model_dump_json"):
            msg_str = message.model_dump_json()
        elif hasattr(message, "model_dump"):
            msg_str = json.dumps(message.model_dump())
        elif isinstance(message, dict):
            msg_str = json.dumps(message)
        else:
            # Fallback to repr
            msg_str = json.dumps({"value": repr(message)})
    except (TypeError, ValueError) as e:
        if logger:
            logger.warning("Failed to serialize message, using repr: %s", e)
        msg_str = repr(message)

    async def _publish():
        nc = NATS()
        try:
            await nc.connect(servers=[nats_server], reconnect_time_wait=2)
        except NATSError as e:
            if logger:
                logger.error("Failed to connect to NATS server %s: %s", nats_server, e)
            return
        js = nc.jetstream()

        # Ensure the stream exists
        try:
            await js.stream_info(stream)
        except (JetStreamError, NotFoundError, NATSError) as e:
            if logger:
                logger.info("Creating stream %s (reason: %s)", stream, e)
            try:
                sc = StreamConfig(name=stream, subjects=[subject])
                await js.add_stream(sc)
            except (JetStreamError, NATSError) as err:
                if logger:
                    logger.error("Failed to create stream %s: %s", stream, err)
                await nc.drain()
                return

        try:
            # Publish the message
            await js.publish(subject, msg_str.encode())
        except (JetStreamError, NATSError) as e:
            if logger:
                logger.error("Failed to publish message to %s: %s", subject, e)
        await nc.drain()

    await asyncio.wait_for(_publish(), timeout=timeout)


def send_http_request(
    method: str, url: str, params=None, data=None, headers=None
) -> Response:
    """
    Send an HTTP request using the provided session.

    Args:
        method (str): The HTTP method (e.g., 'GET', 'POST').
        url (str): The URL to send the request to.
        params (dict, optional): Query parameters for the request.
        data (Any, optional): The request payload.
        headers (dict, optional): Headers for the request.
    Returns:
        Response: The response from the HTTP request.
    """
    try:
        logger.info(
            "Sending %s request to %s with params=%s and data=%s",
            method,
            url,
            params,
            data,
        )
        response = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return response
    except requests.Timeout:
        logger.error("HTTP request to %s timed out", url)
        raise
    except requests.RequestException as e:
        logger.error("HTTP request failed: %s", print_exception(e))
        raise
