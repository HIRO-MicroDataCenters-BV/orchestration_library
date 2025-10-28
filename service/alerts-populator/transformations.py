import json
from utils import (
    get_pod_id_by_name,
    get_node_id_by_name,
)

def safe_json_loads(data: str):
    try:
        return json.loads(data), None
    except Exception as e:
        return None, e

def build_alert_api_payload(input_json: dict, alert_type: str) -> json:
    # Example transformation logic for network attack alerts
    payload = {
        "alert_type": alert_type,
        "alert_model": input_json.get("model", "unknown"),
        "alert_description": input_json.get(
            "description", input_json.get("model", "unknown") + " alert detected"
        ),
        "pod_id": input_json.get("pod_id", None),
        "node_id": input_json.get("node_id", None),
        "pod_name": input_json.get("pod_name", None),
        "node_name": input_json.get("node_name", None),
        "source_ip": input_json.get("source_ip", None),
        "source_port": input_json.get("source_port", None),
        "destination_ip": input_json.get("destination_ip", None),
        "destination_port": input_json.get("destination_port", None),
        "protocol": input_json.get("protocol", None),
    }
    return payload


def transform_network_attack(data: str) -> json:
    # Example transformation logic for network attack alerts
    alert_payloads = []
    json_data = json.loads(data)
    alert_payloads.append(build_alert_api_payload(json_data, "Network-Attack"))
    return alert_payloads


def transform_abnormal(data: str) -> json:
    # Example transformation logic for abnormal alerts
    # Expected input json string is :
    #     {
    #   "timestamp": "2025-10-15T23:51:31.752364",
    #   "data": {
    #     "pod": "submariner-lighthouse-coredns-765db7f584-nsk89",
    #     "instance": "master",
    #     "timestamp": "2025-10-15T23:51:01.031000",
    #     "prediction": "CPU HOG"
    #   },
    #   "model_name": "tis"
    # }
    parsed, err = safe_json_loads(data)
    if err:
        return [{"alert_type": "ParseError", "alert_description": f"Invalid JSON: {err}", "raw": data[:200]}]
    input_json = parsed
    data = input_json.get("data", {})
    pod_name = data.get("pod")
    node_name = data.get("instance")
    payload = {
        "alert_type": "Abnormal",
        "alert_model": input_json.get("model_name", pod_name),
        "alert_description": data.get("prediction", pod_name),
        "pod_name": pod_name,
        "pod_id": get_pod_id_by_name(pod_name),
        "node_id": get_node_id_by_name(node_name),
        "node_name": node_name,
        "source_ip": input_json.get("source_ip"),
        "source_port": input_json.get("source_port"),
        "destination_ip": input_json.get("destination_ip"),
        "destination_port": input_json.get("destination_port"),
        "protocol": input_json.get("protocol"),
        "created_at": data.get("timestamp"),
    }
    return [payload]


def default_transform_func(data: str) -> json:
    alert_payloads = []
    alert_payloads.append(build_alert_api_payload(json.loads(data), "Other"))
    return alert_payloads


def get_transformation_func(subject: str):
    match subject:
        case "alerts.network-attack":
            return transform_network_attack
        case "anomalies":
            return transform_abnormal
        case _:
            return default_transform_func
