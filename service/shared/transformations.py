import json
import logging
import os
from .utils import (
    get_pod_id_by_name,
    get_node_id_by_name,
)

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
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


def transform_event(data: str, alert_type: str) -> list[dict]:
    """
    Shared transformation for attack / abnormal alerts.
    Returns a single-element list with the normalized payload or [] on parse error.
    """
    parsed, err = safe_json_loads(data)
    if err:
        logger.error("Error parsing JSON(%s) of Alert type (%s): %s", data, alert_type, err)
        return []

    root = parsed or {}
    data_section = root.get("data", {}) or {}
    pod_name = data_section.get("pod")
    node_name = data_section.get("instance")

    # Short-circuit if both pod_name and node_name are missing
    if pod_name is None and node_name is None:
        logger.warning("Both pod_name and node_name are missing in alert: %s", alert_type)
        return []

    pod_id = get_pod_id_by_name(pod_name) if pod_name else None
    node_id = get_node_id_by_name(node_name) if node_name else None

    payload = {
        "alert_type": alert_type,
        "alert_model": root.get("model_name", pod_name),
        "alert_description": data_section.get("prediction", pod_name),
        "pod_name": pod_name,
        "pod_id": pod_id,
        "node_id": node_id,
        "node_name": node_name,
        "source_ip": root.get("source_ip"),
        "source_port": root.get("source_port"),
        "destination_ip": root.get("destination_ip"),
        "destination_port": root.get("destination_port"),
        "protocol": root.get("protocol"),
        "created_at": data_section.get("timestamp"),
    }
    return [payload]

def transform_attack(data: str) -> list[dict]:
    """Transform raw attack alert JSON string into API payload list."""
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
    return transform_event(data, "Attack")

def transform_abnormal(data: str) -> list[dict]:
    """Transform raw abnormal alert JSON string into API payload list."""
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
    return transform_event(data, "Abnormal")

def default_transform_func(data: str) -> json:
    alert_payloads = []
    alert_payloads.append(build_alert_api_payload(json.loads(data), "Other"))
    return alert_payloads

def transform_hp3_predictions_params(data: str):
    parsed, err = safe_json_loads(data)
    if err:
        logger.error("Error parsing JSON(%s): %s", data, err)
        return []
    payload = {
        "output_1": parsed.get("o1", 0.0),
        "output_2": parsed.get("o2", 0.0),
        "output_3": parsed.get("o3", 0.0),
        "alpha": parsed.get("alpha", 0.0),
        "beta": parsed.get("beta", 0.0),
        "gamma": parsed.get("gamma", 0.2),
    }
    timestamp = parsed.get("timestamp", None)
    if timestamp:
        payload["created_at"] = timestamp
    return [payload]

def get_alert_transformation_func(subject: str):
    match subject:
        case "attack":
            return transform_attack
        case "anomalies":
            return transform_abnormal
        case _:
            return default_transform_func

def get_tuning_params_transformation_func(subject: str):
    match subject:
        case "hp3.predictions":
            return transform_hp3_predictions_params
        case _:
            return default_transform_func

def get_transformation_func(stream: str):
    match stream:
        case "PREDICTIONS":
            return get_alert_transformation_func
        case "HP3":
            return get_tuning_params_transformation_func