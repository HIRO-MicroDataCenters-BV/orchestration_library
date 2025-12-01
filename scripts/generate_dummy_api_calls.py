"""
Script to generate dummy API calls for testing workload request decisions and actions.
Sends a mix of successful and failed requests to specified endpoints.
"""
from datetime import datetime, timedelta
import json
import random
import uuid
import requests
import argparse
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"  # update if needed

# ENUMS
DECISION_STATUS = ["pending", "succeeded", "failed"]
ACTION_TYPE = ["bind", "create", "delete", "move", "swap_x", "swap_y"]
ACTION_STATUS = ["pending", "succeeded", "failed"]
POD_PARENT_TYPE = ["deployment", "statefulset", "daemonset", "job"]


def random_time():
    start = datetime.utcnow() - timedelta(minutes=random.randint(1, 30))
    end = start + timedelta(seconds=random.randint(1, 15))
    return start.isoformat(), end.isoformat()


def random_name(prefix):
    return f"{prefix}-{random.randint(1000, 9999)}"


# -------------------------------------------------------------------
# Payload Builders
# -------------------------------------------------------------------


def build_decision_payload():
    start, end = random_time()
    return {
        "is_elastic": random.choice([True, False]),
        "queue_name": random.choice(["queue-a", "queue-b", "queue-c"]),
        "demand_cpu": round(random.uniform(0.1, 2.5), 2),
        "demand_memory": random.randint(128, 2048),
        "demand_slack_cpu": round(random.uniform(0.1, 1.0), 2),
        "demand_slack_memory": random.randint(64, 1024),
        "pod_name": random_name("pod"),
        "pod_id": str(uuid.uuid4()),
        "namespace": random.choice(["default", "prod", "dev"]),
        "node_id": str(uuid.uuid4()),
        "node_name": random_name("node"),
        "action_type": random.choice(ACTION_TYPE),
        "decision_status": random.choice(DECISION_STATUS),
        "pod_parent_id": str(uuid.uuid4()),
        "pod_parent_name": random_name("deployment"),
        "pod_parent_kind": random.choice(POD_PARENT_TYPE),
        "decision_start_time": start,
        "decision_end_time": end,
    }


def build_action_payload():
    start, end = random_time()
    return {
        "created_pod_name": random_name("pod"),
        "created_pod_namespace": random.choice(["default", "prod", "dev"]),
        "created_node_name": random_name("node"),
        "deleted_pod_name": random_name("pod-del"),
        "deleted_pod_namespace": "default",
        "deleted_node_name": random_name("node-del"),
        "bound_pod_name": random_name("pod-bind"),
        "bound_pod_namespace": "default",
        "bound_node_name": random_name("node-bind"),
        "action_type": random.choice(ACTION_TYPE),
        "action_status": random.choice(ACTION_STATUS),
        "action_start_time": start,
        "action_end_time": end,
        "action_reason": random.choice(["scaling", "rebalance", "node-pressure"]),
        "pod_parent_name": random_name("deploy"),
        "pod_parent_type": random.choice(POD_PARENT_TYPE),
        "pod_parent_uid": str(uuid.uuid4()),
    }


def call_api(url: str, json_data: dict):
    """
    Makes an API call.
    If should_fail=True, intentionally sends invalid payload or invalid URL
    to force non-200 response.
    """

    payload_str = json.dumps(json_data)
    headers = {"Accept": "application/json"}  # Content-Type is set automatically for json=
    try:
        resp = requests.post(url, timeout=5, data=payload_str, headers=headers)
        return resp.status_code
    except Exception:
        return 0


def generate_calls(
    base_url: str,
    endpoint: str,
    total_calls: int,
    fail_percentage: int,
):

    num_fail = int((fail_percentage / 100) * total_calls)
    num_success = total_calls - num_fail

    if endpoint == "/workload_request_decision":
        payload = build_decision_payload()
    elif endpoint == "/workload_action":
        payload = build_action_payload()
    else:
        print(f"Unknown endpoint: {endpoint}")
        return
    
    if not endpoint.endswith("/"):
        endpoint = endpoint + "/"
    full_url = urljoin(base_url, endpoint)

    calls = [False] * num_success + [True] * num_fail
    random.shuffle(calls)

    success_count = 0
    fail_count = 0

    for should_fail in calls:
        modified_payload = payload.copy()
        if should_fail:
            if endpoint.__contains__("workload_request_decision"):
                modified_payload["decision_start_time"] = None  # invalid value
            elif endpoint.__contains__("workload_action"):
                modified_payload["action_start_time"] = None  # invalid value
            else:
                print(f"Unknown endpoint: {endpoint}")
                return
        # print(f"Modified Payload: {payload_str}")
        status = call_api(full_url, modified_payload)
        if status == 200:
            print(f"✔ Success: {status}")
            success_count += 1
        else:
            print(f"✘ Failed: {status}")
            fail_count += 1

    print("\n========== SUMMARY ==========")
    print(f"Total Calls:  {total_calls}")
    print(f"Success (200 status): {success_count}")
    print(f"Failed (!=200 status): {fail_count}")
    print("================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="API Success/Failure Load Generator for workload_request_decision and workload_action APIs"
    )

    parser.add_argument(
        "--base-url", required=True, help="Base URL (e.g., http://localhost:8000)"
    )
    # parser.add_argument("--endpoint", required=True, help="API endpoint (e.g., /workload_request_decision)")
    parser.add_argument("--calls", type=int, default=10, help="Total number of calls")
    parser.add_argument(
        "--fail-percent",
        type=int,
        default=30,
        help="Percentage of calls that should fail",
    )

    args = parser.parse_args()

    generate_calls(
        base_url=args.base_url,
        endpoint="/workload_request_decision",
        total_calls=args.calls,
        fail_percentage=args.fail_percent,
    )
    generate_calls(
        base_url=args.base_url,
        endpoint="/workload_action",
        total_calls=args.calls,
        fail_percentage=args.fail_percent,
    )


############################################################
## Example usage:
# python scripts/generate_dummy_api_calls.py --base-url http://localhost:8000 --calls 10 --fail-percent 30
############################################################
