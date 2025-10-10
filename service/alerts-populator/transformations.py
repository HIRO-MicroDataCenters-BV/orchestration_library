def transform_network_attach(data: str) -> dict:
    # Example transformation logic for network attach alerts
    return {"level": "critical", "message": data.upper()}

def transform_abnormal(data: str) -> dict:
    # Example transformation logic for abnormal alerts
    return {"level": "warning", "message": data.lower()}

def default_transform_func(data: str) -> dict:
    return {"message": data}

def get_transformation_func(alert_type: str):
    match alert_type:
        case "alerts.network-attach":
            return transform_network_attach
        case "alerts.abnormal":
            return transform_abnormal
        case _:
            return default_transform_func
