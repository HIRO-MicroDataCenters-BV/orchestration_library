import asyncio
import json
import logging
import os
from typing import Any, Optional

from nats.aio.client import Client as NATS
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

class JetStreamPublisher:
    """
    Generic JetStream publisher that:
    - Maintains a connection with reconnect/backoff
    - Accepts messages via enqueue()
    - Publishes them to JetStream subjects with optional JSON serialization
    """

    def __init__(
        self,
        nats_server: str,
        stream: str,
        subjects: list[str],
        max_reconnect_delay: int = 30,
        init_reconnect_delay: int = 1,
        queue_maxsize: int = 1000,
        publish_timeout: float = 5.0,
        ensure_stream: bool = True,
    ):
        self.nats_server = nats_server
        self.stream = stream
        self.subjects = subjects
        self.max_reconnect_delay = max_reconnect_delay
        self.init_reconnect_delay = init_reconnect_delay
        self.publish_timeout = publish_timeout
        self.ensure_stream = ensure_stream
        self._queue: asyncio.Queue[tuple[str, bytes]] = asyncio.Queue(maxsize=queue_maxsize)
        self._stop = asyncio.Event()
        self._nc: Optional[NATS] = None
        self._js = None

    async def enqueue(self, subject: str, payload: Any):
        """
        Enqueue a payload for publishing.
        Payload can be bytes, str, dict, list. Dict/list will be JSON-encoded.
        """
        if subject not in self.subjects:
            logger.warning("Subject %s not registered; allowed=%s", subject, self.subjects)
        if isinstance(payload, bytes):
            data = payload
        elif isinstance(payload, str):
            data = payload.encode()
        else:
            try:
                data = json.dumps(payload, separators=(",", ":")).encode()
            except Exception as e:
                logger.error("Serialization failed for subject=%s: %s", subject, e)
                return
        try:
            await self._queue.put((subject, data))
        except asyncio.CancelledError:
            logger.warning("Enqueue cancelled for subject=%s", subject)
            raise

    async def connect(self):
        nc = NATS()

        async def disconnected_cb():
            logger.warning("Publisher disconnected.")

        async def reconnected_cb():
            logger.info("Publisher reconnected %s", nc.connected_url.netloc)

        async def closed_cb():
            logger.error("Publisher connection closed.")

        await nc.connect(
            servers=[self.nats_server],
            allow_reconnect=True,
            name="generic-js-publisher",
            disconnected_cb=disconnected_cb,
            reconnected_cb=reconnected_cb,
            closed_cb=closed_cb,
            connect_timeout=10,
            ping_interval=10,
            max_outstanding_pings=5,
        )
        self._nc = nc
        self._js = nc.jetstream()
        logger.info("Connected to %s", self.nats_server)
        if self.ensure_stream:
            await self.ensure_stream()

    async def ensure_stream(self):
        """
        Ensure the JetStream stream exists with subjects provided.
        Will attempt to update subjects if stream exists.
        """
        try:
            info = await self._js.stream_info(self.stream)
            existing = set(info.config.subjects or [])
            desired = set(self.subjects)
            if desired - existing:
                new_subjects = sorted(existing | desired)
                await self._js.update_stream(
                    {
                        "name": self.stream,
                        "subjects": new_subjects,
                    }
                )
                logger.info("Updated stream=%s subjects=%s", self.stream, new_subjects)
        except Exception:
            # Assume not found; create
            try:
                await self._js.add_stream(
                    {
                        "name": self.stream,
                        "subjects": self.subjects,
                        "retention": "limits",  # options: limits, interest, workqueue
                    }
                )
                logger.info("Created stream=%s subjects=%s", self.stream, self.subjects)
            except Exception as e:
                logger.error("Failed ensure/create stream=%s: %s", self.stream, e)
                raise

    async def publisher_loop(self):
        """
        Dequeue and publish messages until stopped.
        """
        while not self._stop.is_set():
            try:
                subject, data = await asyncio.wait_for(self._queue.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

            try:
                ack = await asyncio.wait_for(
                    self._js.publish(subject, data),
                    timeout=self.publish_timeout,
                )
                logger.debug(
                    "Published subject=%s seq=%s size=%s",
                    subject,
                    getattr(ack, "seq", None),
                    len(data),
                )
            except (TimeoutError, ConnectionClosedError, NoServersError) as e:
                logger.warning("Publish transient error subject=%s: %s", subject, e)
                # Requeue for retry
                try:
                    self._queue.put_nowait((subject, data))
                except asyncio.QueueFull:
                    logger.error("Queue full; dropping message subject=%s", subject)
            except Exception as e:
                logger.error("Publish error subject=%s: %s", subject, e)

    async def run(self):
        """
        Run publisher with reconnection handling.
        """
        reconnect_delay = self.init_reconnect_delay
        while not self._stop.is_set():
            try:
                await self.connect()
                reconnect_delay = self.init_reconnect_delay
                await self.publisher_loop()
            except Exception as e:
                if self._stop.is_set():
                    break
                logger.warning(
                    "Publisher loop error: %s; reconnect in %ss", e, reconnect_delay
                )
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, self.max_reconnect_delay)
            finally:
                if self._nc and not self._nc.is_closed:
                    try:
                        await self._nc.close()
                    except Exception:
                        pass
                self._nc = None
                self._js = None

    async def stop(self):
        """
        Signal stop and drain queue.
        """
        self._stop.set()
        # Drain remaining messages (best-effort)
        if self._nc and self._js:
            while not self._queue.empty():
                subject, data = self._queue.get_nowait()
                try:
                    await self._js.publish(subject, data)
                except Exception as e:
                    logger.warning("Drain publish failed subject=%s: %s", subject, e)
        if self._nc and not self._nc.is_closed:
            try:
                await self._nc.close()
            except Exception:
                pass


# Example usage
async def main():
    publisher = JetStreamPublisher(
        nats_server=os.environ.get("NATS_SERVER", "nats://localhost:4222"),
        stream="KPI_METRICS",
        subjects=["kpi.metrics.geometric_mean", "kpi.metrics.latest"],
    )

    async def produce_dummy():
        # Simulate producing metrics
        for i in range(5):
            await publisher.enqueue(
                "kpi.metrics.geometric_mean",
                {
                    "request_decision_id": f"req-{i}",
                    "geometric_mean": 1.234 + i,
                    "timestamp": asyncio.get_event_loop().time(),
                },
            )
            await asyncio.sleep(0.5)

    runner = asyncio.create_task(publisher.run())
    producer = asyncio.create_task(produce_dummy())

    await producer
    await asyncio.sleep(2)  # allow publishes
    await publisher.stop()
    await runner

if __name__ == "__main__":
    asyncio.run(main())