"""
Generic JetStream forwarder that consumes messages from specified
subjects and processes them using a user-defined async handler.
"""

import asyncio
import logging
import os
import httpx
from nats.aio.client import Client as NATS
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError

from .http_post import post_json
from .transformations import get_transformation_func


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def make_post_api_handler(post_api_url: str, stream: str):
    """Generate a handler function that posts messages to the given API URL."""

    async def handler(subject: str, data_bytes: bytes, attempt: int) -> bool:
        """Handle incoming NATS message."""
        logger.info("Handling message for subject: %s", subject)
        data = data_bytes.decode()
        transform_type_func = get_transformation_func(stream)
        transform_func = transform_type_func(subject)
        payloads = transform_func(data)
        if not isinstance(payloads, list):
            logger.error("Transformer returned non-list: %s", type(payloads))
            return False
        async with httpx.AsyncClient(follow_redirects=True) as client:
            all_ok = True
            for p in payloads:
                ok, status_code, response_text = await post_json(
                    client, post_api_url, p
                )
                logger.info(
                    "Posted payload to %s: status=%s response=%s",
                    post_api_url,
                    status_code,
                    response_text,
                )
                all_ok = all_ok and ok
            return all_ok

    return handler


class JetStreamForwarder:
    """Generic JetStream forwarder."""

    def __init__(
        self,
        nats_server: str,
        stream: str,
        subjects: list[str],
        durable_prefix: str,
        handler,  # async function (subject, data_bytes, attempt) -> bool
        max_redeliveries: int = 5,
        init_reconnect_delay: int = 2,
        max_reconnect_delay: int = 30,
        max_ack_wait_seconds: int = 30,
        max_concurrent_msgs: int = 20,
        max_ack_pending: int = None,
        max_queue_size: int = None,
    ):
        self.nats_server = nats_server
        self.stream = stream
        self.subjects = subjects
        self.durable_prefix = durable_prefix
        self.max_redeliveries = max_redeliveries
        self.init_reconnect_delay = init_reconnect_delay
        self.max_reconnect_delay = max_reconnect_delay
        self.max_concurrent_msgs = max_concurrent_msgs
        self.max_ack_wait_seconds = max_ack_wait_seconds
        self.max_ack_pending = (
            max_ack_pending
            if max_ack_pending is not None
            else self.max_concurrent_msgs * 2
        )
        self.max_queue_size = (
            max_queue_size if max_queue_size is not None else self.max_ack_pending
        )
        self.handler = handler

    async def consume(self, nc: NATS):
        """Consume messages from JetStream subjects."""
        js = nc.jetstream()
        msg_queue: asyncio.Queue = asyncio.Queue(maxsize=self.max_queue_size)

        async def worker(worker_id: int):
            """Worker to process messages from the queue."""
            while True:
                msg = await msg_queue.get()
                attempts = getattr(getattr(msg, "metadata", None), "num_delivered", 1)
                try:
                    ok = await self.handler(msg.subject, msg.data, attempts)
                    if ok:
                        await msg.ack()
                        logger.debug(
                            "[worker-%d] Acked message on %s (attempt %s)",
                            worker_id,
                            msg.subject,
                            attempts,
                        )
                    else:
                        if attempts < self.max_redeliveries:
                            await msg.nak()
                            logger.warning(
                                "[worker-%d] NAK message on %s (attempt %s)",
                                worker_id,
                                msg.subject,
                                attempts,
                            )
                        else:
                            await msg.term()
                            logger.error(
                                "[worker-%d] Terminated message on %s after %s attempts",
                                worker_id,
                                msg.subject,
                                attempts,
                            )
                except Exception as e:
                    try:
                        if attempts < self.max_redeliveries:
                            await msg.nak()
                    except Exception:
                        logger.error(
                            "[worker-%d] Exception processing message on %s (attempt %s): %s",
                            worker_id,
                            msg.subject,
                            attempts,
                            str(e),
                        )
                finally:
                    msg_queue.task_done()

        workers = [
            asyncio.create_task(worker(i)) for i in range(self.max_concurrent_msgs)
        ]

        async def js_callback(msg):
            """JetStream message callback with queueing."""
            await msg_queue.put(msg)

        async def subscribe(subject: str):
            """Subscribe to a JetStream subject."""
            durable = f"{self.durable_prefix}-{subject.replace('.', '_')}"
            attempt = 0
            created = False
            while True:
                attempt += 1
                try:
                    sub_params = {
                        "subject": subject,
                        "stream": self.stream,
                        "durable": durable,
                        "manual_ack": True,
                        "cb": js_callback,
                        "config": {
                            "ack_policy": "explicit",
                            "ack_wait": self.max_ack_wait_seconds,
                            "max_ack_pending": self.max_ack_pending,
                            "max_deliver": self.max_redeliveries,
                        },
                    }
                    if not created:
                        sub_params["deliver_policy"] = "new"
                        created = True
                    sub = await js.subscribe(**sub_params)
                    if not created:
                        logger.info(
                            "Created and subscribed "
                            "stream=%s subject=%s durable=%s "
                            "max_concurrent_msgs=%s max_ack_wait_seconds=%s",
                            self.stream,
                            subject,
                            durable,
                            self.max_concurrent_msgs,
                            self.max_ack_wait_seconds,
                        )
                    else:
                        logger.info(
                            "Attached the existing "
                            "stream=%s subject=%s durable=%s "
                            "max_concurrent_msgs=%s max_ack_wait_seconds=%s",
                            self.stream,
                            subject,
                            durable,
                            self.max_concurrent_msgs,
                            self.max_ack_wait_seconds,
                        )
                    return sub
                except Exception as e:
                    msg = str(e)
                    if "consumer is already bound" in msg.lower():
                        await asyncio.sleep(5)
                        created = True
                        continue
                    logger.error(
                        "Subscribe error subject=%s attempt=%s: %s",
                        subject,
                        attempt,
                        msg,
                    )
                    await asyncio.sleep(min(5, attempt))
                    continue

        for subject in self.subjects:
            await subscribe(subject)
        await nc.flush()
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            for w in workers:
                w.cancel()

    async def run(self):
        """Run the JetStream forwarder with reconnection logic."""
        while True:
            reconnect_delay = self.init_reconnect_delay
            nc = NATS()

            async def disconnected_cb():
                logger.warning("NATS disconnected; reconnecting...")

            async def reconnected_cb():
                logger.info("Reconnected to NATS at %s", nc.connected_url.netloc)

            async def closed_cb():
                logger.error("NATS connection closed.")

            try:
                await nc.connect(
                    servers=[self.nats_server],
                    allow_reconnect=True,
                    reconnect_time_wait=reconnect_delay,
                    max_reconnect_attempts=-1,
                    disconnected_cb=disconnected_cb,
                    reconnected_cb=reconnected_cb,
                    closed_cb=closed_cb,
                    name="generic-js-forwarder",
                    connect_timeout=10,
                    ping_interval=10,
                    max_outstanding_pings=5,
                )
                logger.info("Connected to %s", self.nats_server)
                await self.consume(nc)
                reconnect_delay = self.init_reconnect_delay
            except (ConnectionClosedError, NoServersError, TimeoutError) as e:
                logger.warning("NATS error: %s; retry in %ss", e, reconnect_delay)
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, self.max_reconnect_delay)
            except Exception as e:
                logger.error("Unexpected error: %s", e)
                await asyncio.sleep(reconnect_delay)
