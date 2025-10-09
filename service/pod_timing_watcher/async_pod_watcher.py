import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone

import aiohttp
from kubernetes_asyncio import client, config, watch


API_URL = os.environ.get(
    "WORKLOAD_TIMING_API_URL", "http://localhost:30015/workload_timing/"
)  # your FastAPI endpoint

# Configure logger
logger = logging.getLogger(__name__)


def to_utc(dt):
    if dt and not dt.tzinfo:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def now_utc():
    return datetime.now(timezone.utc)


async def get_k8s_core_v1_client():
    """
    Load config (in-cluster first, fallback to local kubeconfig) and return CoreV1Api.
    """
    try:
        # in-cluster loader is sync in kubernetes_asyncio
        config.load_incluster_config()
        logger.info("Loaded in-cluster Kubernetes config")
    except Exception:
        logger.info("Falling back to local kubeconfig")
        await config.load_kube_config()
    return client.CoreV1Api()


def parse_pod_event(pod):
    """Extract timestamps and format payload for /workload_timing/."""
    metadata = pod.metadata
    status = pod.status
    spec = pod.spec

    pod_name = metadata.name
    namespace = metadata.namespace
    pod_uid = metadata.uid
    node_name = spec.node_name if spec and spec.node_name else None
    scheduler_type = getattr(spec, "scheduler_name", "default-scheduler")
    phase = status.phase if status else None
    reason = getattr(status, "reason", None)
    creation_time = to_utc(metadata.creation_timestamp)
    deletion_time = to_utc(metadata.deletion_timestamp)

    scheduled_timestamp = None
    ready_timestamp = None
    completed = False

    # Get scheduled time from pod condition (if exists)
    if status.conditions:
        for cond in status.conditions:
            if cond.type == "PodScheduled" and cond.status == "True":
                scheduled_timestamp = to_utc(cond.last_transition_time)
            if cond.type == "Ready" and cond.status == "True":
                ready_timestamp = to_utc(cond.last_transition_time)

    # Mark completed if succeeded or failed
    if phase in ["Succeeded", "Failed"]:
        completed = True

    # Create payload
    payload = {
        "id": str(uuid.uuid4()),
        "pod_name": pod_name,
        "namespace": namespace,
        "node_name": node_name or "unknown",
        "scheduler_type": scheduler_type or "default-scheduler",
        "pod_uid": pod_uid,
        "created_timestamp": creation_time.isoformat() if creation_time else None,
        "scheduled_timestamp": (
            scheduled_timestamp.isoformat() if scheduled_timestamp else None
        ),
        "ready_timestamp": ready_timestamp.isoformat() if ready_timestamp else None,
        "deleted_timestamp": deletion_time.isoformat() if deletion_time else None,
        "phase": phase,
        "reason": reason,
        "is_completed": completed,
        "recorded_at": now_utc().isoformat(),
    }
    logger.debug("Parsed pod data: %s", payload)
    return payload


async def _fetch_existing_id(session: aiohttp.ClientSession, pod_name: str, namespace: str) -> str | None:
    """
    Call GET /workload_timing?pod_name=&namespace= to find existing entry.
    Handles server responses that may be a list or single object.
    """
    params = {"pod_name": pod_name, "namespace": namespace}
    try:
        async with session.get(API_URL, params=params, timeout=10) as resp:
            if resp.status != 200:
                logger.debug("GET existing returned %s", resp.status)
                return None
            try:
                data = await resp.json()
            except Exception:
                return None
            # If API returns a list
            if isinstance(data, list):
                if not data:
                    return None
                first = data[0]
                return first.get("id")
            # Single object
            if isinstance(data, dict):
                return data.get("id")
    except Exception as e:
        logger.debug("GET existing failed: %s", e)
    return None

async def _patch_workload_timing(session: aiohttp.ClientSession, wt_id: str, payload: dict):
    patch_url = f"{API_URL}{wt_id}"
    async with session.patch(patch_url, json=payload, timeout=10) as resp:
        if resp.status == 200:
            logger.info("Updated workload timing id=%s pod=%s ns=%s",
                        wt_id, payload.get("pod_name"), payload.get("namespace"))
        else:
            logger.error("PATCH %s failed status=%s body=%s",
                         wt_id, resp.status, await resp.text())

async def send_to_fastapi(session, data):
    """Send timing data to FastAPI asynchronously."""
    try:
        pod_name = data.get("pod_name")
        namespace = data.get("namespace")
        # Check whether an entry existed or not?
        existing_id = await _fetch_existing_id(session, pod_name, namespace)
        if existing_id:
            await _patch_workload_timing(session, existing_id, data)
            return
        async with session.post(API_URL, json=data) as resp:
            if resp.status != 200:
                logger.error(f"Failed ({resp.status}): {await resp.text()}")
            else:
                logger.info(f"Sent timings for {data['pod_name']} ({data['namespace']})")
    except Exception as e:
        logger.error(f"Error sending data: {e}")


async def watch_pods(session: aiohttp.ClientSession):
    """Watch pod events asynchronously using Kubernetes API."""
    v1 = await get_k8s_core_v1_client()
    w = watch.Watch()

    # list/watching all namespaces; 
    # could filter with field_selector or label_selector
    try:
        async for event in w.stream(
            v1.list_pod_for_all_namespaces, timeout_seconds=60
        ):
            pod_obj = event.get("object")
            if not pod_obj:
                continue
            event_type = event.get("type")
            # if event_type in ("ADDED", "MODIFIED", "DELETED"):
            if event_type in ("ADDED"):
                data = parse_pod_event(pod_obj)
                await send_to_fastapi(session, data)
    except Exception as e:
        logger.error("Watch failed: %s", e)
        raise
    finally:
        await w.close()


async def main():
    # Reuse one HTTP session
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await watch_pods(session)
            except Exception:
                await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
