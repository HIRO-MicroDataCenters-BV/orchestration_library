def transform_critical(data: str) -> dict:
    # Example transformation logic for critical alerts
    return {"level": "critical", "message": data.upper()}

def transform_warning(data: str) -> dict:
    # Example transformation logic for warning alerts
    return {"level": "warning", "message": data.lower()}

TRANSFORMATION_MAP = {
    "alerts.critical": transform_critical,
    "alerts.warning": transform_warning,
}
