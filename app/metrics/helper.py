"""
Helper functions for metrics collection.

This module provides utility functions to simplify the process of recording
metrics for API requests and other events.
"""

import time
from typing import Any, Dict, Optional, List
from app.metrics.custom_metrics import (
    api_requests_total,
    api_requests_latency_seconds,
    workload_action_requests_total,
    workload_action_requests_latency_seconds,
    workload_request_decision_requests_total,
    workload_request_decision_requests_latency_seconds,
    alerts_requests_total,
    alerts_requests_latency_seconds,
    tuning_parameters_requests_total,
    tuning_parameters_requests_latency_seconds,
    k8s_pod_requests_total,
    k8s_pod_requests_latency_seconds,
    k8s_pod_parent_requests_total,
    k8s_pod_parent_requests_latency_seconds,
    k8s_user_pod_requests_total,
    k8s_user_pod_requests_latency_seconds,
    k8s_node_requests_total,
    k8s_node_requests_latency_seconds,
    k8s_get_token_requests_total,
    k8s_get_token_requests_latency_seconds,
    k8s_cluster_info_requests_total,
    k8s_cluster_info_requests_latency_seconds,
)

DEFAULT_COUNTER_METRICS = [api_requests_total]
DEFAULT_HISTOGRAM_METRICS = [api_requests_latency_seconds]


def record_api_metrics(
    metrics_details: Dict[str, Any],
    status_code: int,
    exception: Optional[Exception] = None,
    counter_metrics: Optional[List] = None,
    histogram_metrics: Optional[List] = None,
):
    """
    Generalized function to record metrics for any API request.

    Args:
        metrics_details (Dict[str, Any]): Details about the request for metrics.
        status_code (int): HTTP status code of the response.
        counter_metrics (Optional[List]): List of Counter metrics to update.
        histogram_metrics (Optional[List]): List of Histogram metrics to update.
        exception (Optional[Exception]): Exception raised during the request, if any.
    """
    if (
        not metrics_details
        or "method" not in metrics_details
        or "endpoint" not in metrics_details
        or "start_time" not in metrics_details
    ):
        return

    metrics_details["status_code"] = status_code
    metrics_details["exception"] = str(exception) if exception else None
    metrics_details["latency"] = time.time() - metrics_details["start_time"]

    counter_metrics = set((counter_metrics or []) + DEFAULT_COUNTER_METRICS)
    histogram_metrics = set((histogram_metrics or []) + DEFAULT_HISTOGRAM_METRICS)

    for metric in counter_metrics:
        metric.labels(
            method=metrics_details["method"],
            endpoint=metrics_details["endpoint"],
            status_code=metrics_details["status_code"],
            exception=metrics_details.get("exception"),
        ).inc()
    for metric in histogram_metrics:
        metric.labels(
            method=metrics_details["method"],
            endpoint=metrics_details["endpoint"],
            status_code=metrics_details["status_code"],
            exception=metrics_details.get("exception"),
        ).observe(metrics_details["latency"])


def record_workload_action_metrics(
    metrics_details: Dict[str, Any],
    status_code: int,
    exception: Optional[Exception] = None,
):
    """
    Record metrics for workload action requests.

    Args:
        metrics_details (Dict[str, Any]): Details about the request for metrics.
        status_code (int): HTTP status code of the response.
        exception (Optional[Exception]): Exception raised during the request, if any.
    """
    if (
        not metrics_details
        or "method" not in metrics_details
        or "endpoint" not in metrics_details
        or "start_time" not in metrics_details
    ):
        return
    record_api_metrics(
        metrics_details=metrics_details,
        status_code=status_code,
        exception=exception,
        counter_metrics=[workload_action_requests_total],
        histogram_metrics=[workload_action_requests_latency_seconds],
    )

def record_workload_request_decision_metrics(
    metrics_details: Dict[str, Any],
    status_code: int,
    exception: Optional[Exception] = None,
):
    """
    Record metrics for workload request decision API requests.

    Args:
        metrics_details (Dict[str, Any]): Details about the request for metrics.
        status_code (int): HTTP status code of the response.
        exception (Optional[Exception]): Exception raised during the request, if any.
    """
    if (
        not metrics_details
        or "method" not in metrics_details
        or "endpoint" not in metrics_details
        or "start_time" not in metrics_details
    ):
        return
    record_api_metrics(
        metrics_details=metrics_details,
        status_code=status_code,
        exception=exception,
        counter_metrics=[workload_request_decision_requests_total],
        histogram_metrics=[workload_request_decision_requests_latency_seconds],
    )

def record_alerts_metrics(
    metrics_details: Dict[str, Any],
    status_code: int,
    exception: Optional[Exception] = None,
):
    """
    Record metrics for alerts API requests.

    Args:
        metrics_details (Dict[str, Any]): Details about the request for metrics.
        status_code (int): HTTP status code of the response.
        exception (Optional[Exception]): Exception raised during the request, if any.
    """
    if (
        not metrics_details
        or "method" not in metrics_details
        or "endpoint" not in metrics_details
        or "start_time" not in metrics_details
    ):
        return
    record_api_metrics(
        metrics_details=metrics_details,
        status_code=status_code,
        exception=exception,
        counter_metrics=[alerts_requests_total],
        histogram_metrics=[alerts_requests_latency_seconds],
    )

def record_tuning_parameters_metrics(
    metrics_details: Dict[str, Any],
    status_code: int,
    exception: Optional[Exception] = None,
):
    """
    Record metrics for tuning parameters API requests.

    Args:
        metrics_details (Dict[str, Any]): Details about the request for metrics.
        status_code (int): HTTP status code of the response.
        exception (Optional[Exception]): Exception raised during the request, if any.
    """
    if (
        not metrics_details
        or "method" not in metrics_details
        or "endpoint" not in metrics_details
        or "start_time" not in metrics_details
    ):
        return
    record_api_metrics(
        metrics_details=metrics_details,
        status_code=status_code,
        exception=exception,
        counter_metrics=[tuning_parameters_requests_total],
        histogram_metrics=[tuning_parameters_requests_latency_seconds],
    )

def record_k8s_pod_metrics(
    metrics_details: Dict[str, Any],
    status_code: int,
    exception: Optional[Exception] = None,
):
    """
    Record metrics for Kubernetes pod API requests.

    Args:
        metrics_details (Dict[str, Any]): Details about the request for metrics.
        status_code (int): HTTP status code of the response.
        exception (Optional[Exception]): Exception raised during the request, if any.
    """
    if (
        not metrics_details
        or "method" not in metrics_details
        or "endpoint" not in metrics_details
        or "start_time" not in metrics_details
    ):
        return
    record_api_metrics(
        metrics_details=metrics_details,
        status_code=status_code,
        exception=exception,
        counter_metrics=[k8s_pod_requests_total],
        histogram_metrics=[k8s_pod_requests_latency_seconds],
    )

def record_k8s_pod_parent_metrics(
    metrics_details: Dict[str, Any],
    status_code: int,
    exception: Optional[Exception] = None,
):
    """
    Record metrics for Kubernetes pod parent API requests.

    Args:
        metrics_details (Dict[str, Any]): Details about the request for metrics.
        status_code (int): HTTP status code of the response.
        exception (Optional[Exception]): Exception raised during the request, if any.
    """
    if (
        not metrics_details
        or "method" not in metrics_details
        or "endpoint" not in metrics_details
        or "start_time" not in metrics_details
    ):
        return
    record_api_metrics(
        metrics_details=metrics_details,
        status_code=status_code,
        exception=exception,
        counter_metrics=[k8s_pod_parent_requests_total],
        histogram_metrics=[k8s_pod_parent_requests_latency_seconds],
    )

def record_k8s_user_pod_metrics(
    metrics_details: Dict[str, Any],
    status_code: int,
    exception: Optional[Exception] = None,
):
    """
    Record metrics for Kubernetes user pod API requests.

    Args:
        metrics_details (Dict[str, Any]): Details about the request for metrics.
        status_code (int): HTTP status code of the response.
        exception (Optional[Exception]): Exception raised during the request, if any.
    """
    if (
        not metrics_details
        or "method" not in metrics_details
        or "endpoint" not in metrics_details
        or "start_time" not in metrics_details
    ):
        return
    record_api_metrics(
        metrics_details=metrics_details,
        status_code=status_code,
        exception=exception,
        counter_metrics=[k8s_user_pod_requests_total],
        histogram_metrics=[k8s_user_pod_requests_latency_seconds],
    )

def record_k8s_node_metrics(
    metrics_details: Dict[str, Any],
    status_code: int,
    exception: Optional[Exception] = None,
):
    """
    Record metrics for Kubernetes node API requests.

    Args:
        metrics_details (Dict[str, Any]): Details about the request for metrics.
        status_code (int): HTTP status code of the response.
        exception (Optional[Exception]): Exception raised during the request, if any.
    """
    if (
        not metrics_details
        or "method" not in metrics_details
        or "endpoint" not in metrics_details
        or "start_time" not in metrics_details
    ):
        return
    record_api_metrics(
        metrics_details=metrics_details,
        status_code=status_code,
        exception=exception,
        counter_metrics=[k8s_node_requests_total],
        histogram_metrics=[k8s_node_requests_latency_seconds],
    )

def record_k8s_get_token_metrics(
    metrics_details: Dict[str, Any],
    status_code: int,
    exception: Optional[Exception] = None,
):
    """
    Record metrics for Kubernetes get token API requests.

    Args:
        metrics_details (Dict[str, Any]): Details about the request for metrics.
        status_code (int): HTTP status code of the response.
        exception (Optional[Exception]): Exception raised during the request, if any.
    """
    if (
        not metrics_details
        or "method" not in metrics_details
        or "endpoint" not in metrics_details
        or "start_time" not in metrics_details
    ):
        return
    record_api_metrics(
        metrics_details=metrics_details,
        status_code=status_code,
        exception=exception,
        counter_metrics=[k8s_get_token_requests_total],
        histogram_metrics=[k8s_get_token_requests_latency_seconds],
    )

def record_k8s_cluster_info_metrics(
    metrics_details: Dict[str, Any],
    status_code: int,
    exception: Optional[Exception] = None,
):
    """
    Record metrics for Kubernetes cluster info API requests.

    Args:
        metrics_details (Dict[str, Any]): Details about the request for metrics.
        status_code (int): HTTP status code of the response.
        exception (Optional[Exception]): Exception raised during the request, if any.
    """
    if (
        not metrics_details
        or "method" not in metrics_details
        or "endpoint" not in metrics_details
        or "start_time" not in metrics_details
    ):
        return
    record_api_metrics(
        metrics_details=metrics_details,
        status_code=status_code,
        exception=exception,
        counter_metrics=[k8s_cluster_info_requests_total],
        histogram_metrics=[k8s_cluster_info_requests_latency_seconds],
    )
