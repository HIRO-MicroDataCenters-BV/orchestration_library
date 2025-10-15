import json
from utils import get_node_id_by_ip, get_node_name_by_ip, get_pod_id_by_name


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
    # {
    #   "outputs": [
    #     {
    #   "data": [
    #     "{\"pod\": \"agent-644d8b675-jfxw8\", \"instance\": \"172.31.33.42:10250\", \"timestamp\": \"2025-10-14T21:51:46.454000\", \"prediction\": \"CPU HOG\"}",
    #     "{\"pod\": \"agent-644d8b675-jfxw8\", \"instance\": \"172.31.33.42:10250\", \"timestamp\": \"2025-10-14T21:52:16.454000\", \"prediction\": \"CPU HOG\"}"
    #   ]
    #     }
    #   ],
    #   "parameters": {
    #     "exclude_predictions": "Normal"
    # }
    # }
    alert_payloads = []
    input_json = json.loads(data)
    for output in input_json.get("outputs", []):
        for data_row in output.get("data", []):
            json_data_row = json.loads(data_row)
            print("json_data_row:", json_data_row)
            instance_ip = json_data_row.get("instance", None)
            if instance_ip and ":" in instance_ip:
                instance_ip = instance_ip.split(":")[0]
            print("instance_ip:", instance_ip)
            pod_name = json_data_row.get("pod", None)
            print("pod_name:", pod_name)
            pod_id = get_pod_id_by_name(pod_name)
            print("pod_id:", pod_id)
            node_id = get_node_id_by_ip(instance_ip)
            print("node_id:", node_id)
            node_name = get_node_name_by_ip(instance_ip)
            print("node_name:", node_name)
            payload = {
                "alert_type": "Abnormal",
                "alert_model": json_data_row.get("model", pod_name),
                "alert_description": json_data_row.get(
                    "prediction", pod_name
                ),
                "pod_name": pod_name,
                "pod_id": pod_id,
                "node_id": node_id,
                "node_name": node_name,
                "source_ip": input_json.get("source_ip", None),
                "source_port": input_json.get("source_port", None),
                "destination_ip": input_json.get("destination_ip", None),
                "destination_port": input_json.get("destination_port", None),
                "protocol": input_json.get("protocol", None),
            }
            if "timestamp" in json_data_row.keys():
                payload["created_at"] = json_data_row.get("timestamp", None)
            alert_payloads.append(payload)
    return alert_payloads


def default_transform_func(data: str) -> json:
    alert_payloads = []
    alert_payloads.append(build_alert_api_payload(json.loads(data), "Other"))
    return alert_payloads


def get_transformation_func(alert_type: str):
    match alert_type:
        case "alerts.network-attack":
            return transform_network_attack
        case "alerts.abnormal":
            return transform_abnormal
        case _:
            return default_transform_func
