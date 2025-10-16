import json
from utils import (
    get_pod_id_by_name,
    get_node_id_by_name,
)


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
    alert_payloads = []
    input_json = json.loads(data)
    data = input_json.get("data", {})
    pod_name = data.get("pod", None)
    node_name = data.get("instance", None)
    pod_id = get_pod_id_by_name(pod_name)
    node_id = get_node_id_by_name(node_name)
    timestamp = data.get("timestamp", None)
    payload = {
        "alert_type": "Abnormal",
        "alert_model": input_json.get("model_name", pod_name),
        "alert_description": input_json.get("prediction", pod_name),
        "pod_name": pod_name,
        "pod_id": pod_id,
        "node_id": node_id,
        "node_name": node_name,
        "source_ip": input_json.get("source_ip", None),
        "source_port": input_json.get("source_port", None),
        "destination_ip": input_json.get("destination_ip", None),
        "destination_port": input_json.get("destination_port", None),
        "protocol": input_json.get("protocol", None),
        "created_at": timestamp,
    }
    alert_payloads.append(payload)
    return alert_payloads


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
