import asyncio
import os
import httpx
from nats.aio.client import Client as NATS
from transformations import get_transformation_func


nats_server = os.getenv("NATS_SERVER", "nats://nats:4222")
topics_list = os.getenv("NATS_TOPICS", "alerts.network-attach, alerts.abnormal")
alerts_api_url = os.getenv(
    "ALERTS_API_URL", "http://api-service.default.svc.cluster.local:8080/alerts"
)


async def message_handler(msg, alerts_api_url):
    subject = msg.subject
    data = msg.data.decode()

    transform_func = get_transformation_func(subject)
    transformed = transform_func(data)

    async with httpx.AsyncClient() as client:
        await client.post(alerts_api_url, json=transformed)

    print(f"Sent transformed data from {subject} to {alerts_api_url}")


async def main():
    print("ENV Variables:")
    print(f"NATS_SERVER: {nats_server}")
    print(f"NATS_TOPICS: {topics_list}")
    print(f"ALERTS_API_URL: {alerts_api_url}")

    topics = [topic.strip() for topic in topics_list.split(",")]

    nc = NATS()
    await nc.connect(servers=[nats_server])

    async def nats_callback(msg):
        await message_handler(msg, alerts_api_url)

    for topic in topics:
        await nc.subscribe(topic, cb=nats_callback)

    print(f"Listening on NATS server {nats_server} for topics: {topics}")
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await nc.drain()


if __name__ == "__main__":
    asyncio.run(main())
