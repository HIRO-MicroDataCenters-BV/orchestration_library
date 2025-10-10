import asyncio
import os
import json
import httpx
from nats.aio.client import Client as NATS
from transformations import TRANSFORMATION_MAP


nats_server = os.getenv("NATS_SERVER", "nats://nats:4222")
topics_json = os.getenv("NATS_TOPICS", '["alerts.critical", "alerts.warning"]')
post_url = os.getenv(
    "POST_API_URL", "http://api-service.default.svc.cluster.local:8080/alerts"
)


async def message_handler(msg, post_url):
    subject = msg.subject
    data = msg.data.decode()

    transform_func = TRANSFORMATION_MAP.get(subject, lambda x: {"message": x})
    transformed = transform_func(data)

    async with httpx.AsyncClient() as client:
        await client.post(post_url, json=transformed)

    print(f"Sent transformed data from {subject} to {post_url}")


async def main():
    topics = json.loads(topics_json)

    nc = NATS()
    await nc.connect(servers=[nats_server])

    for topic in topics:
        await nc.subscribe(
            topic,
            cb=lambda msg, url=post_url: asyncio.create_task(message_handler(msg, url)),
        )

    print(f"Listening on NATS server {nats_server} for topics: {topics}")
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await nc.drain()


if __name__ == "__main__":
    asyncio.run(main())
