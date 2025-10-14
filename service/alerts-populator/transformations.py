import json


def build_alert_api_payload(input_json: dict, alert_type: str) -> json:
    # Example transformation logic for network attack alerts
    payload = {
        "alert_type": alert_type,
        "alert_model": input_json.get("model", "unknown"),
        "alert_description": input_json.get("description", input_json.get("model", "unknown") + " alert detected"),
        "pod_id": input_json.get("pod_id", None),
        "node_id": input_json.get("node_id", None),
        "source_ip": input_json.get("source_ip", None),
        "source_port": input_json.get("source_port", None),
        "destination_ip": input_json.get("destination_ip", None),
        "destination_port": input_json.get("destination_port", None),
        "protocol": input_json.get("protocol", None)
    }
    return payload

def transform_network_attack(data: str) -> json:
    # Example transformation logic for network attack alerts
    json_data = json.loads(data)
    return build_alert_api_payload(json_data, "Network-Attack")

def transform_abnormal(data: str) -> json:
    # Example transformation logic for abnormal alerts
    return build_alert_api_payload(json.loads(data), "Abnormal")

def default_transform_func(data: str) -> json:
    return build_alert_api_payload(json.loads(data), "Other")

def get_transformation_func(alert_type: str):
    match alert_type:
        case "alerts.network-attack":
            return transform_network_attack
        case "alerts.abnormal":
            return transform_abnormal
        case _:
            return default_transform_func
