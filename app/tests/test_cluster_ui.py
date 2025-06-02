"""
Tests for the cluster UI API endpoints.
"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.api.k8s.cluster_ui import parse_cpu, parse_memory
from app.main import app


def test_parse_cpu():
    """Test the CPU parsing function."""
    assert parse_cpu("1000m") == 1000
    assert parse_cpu("2") == 2000
    assert parse_cpu("500u") == 0.5
    assert parse_cpu("1000000000n") == 1000

def test_parse_memory():
    """Test the memory parsing function."""
    assert parse_memory("1024Mi") == 1024
    assert parse_memory("1Gi") == 1024
    assert parse_memory("2048Ki") == 2
    assert parse_memory("1048576") == 1  # bytes to Mi

@patch("app.api.k8s.cluster_ui.k8s_cluster_info.get_cluster_info")
def test_get_ui_cluster_statistic_info(mock_get_cluster_info):
    """
    Test the cluster statistic info endpoint with mock data.
    This test checks if the endpoint correctly calculates CPU and memory usage,
    availability, and utilization based on the mock cluster info.
    """
    # Mock cluster_info with two nodes
    mock_get_cluster_info.return_value = {
        "nodes": [
            {
                "usage": {"cpu": "1000m", "memory": "1024Mi"},
                "allocatable": {"cpu": "2000m", "memory": "2048Mi"},
            },
            {
                "usage": {"cpu": "500m", "memory": "512Mi"},
                "allocatable": {"cpu": "1000m", "memory": "1024Mi"},
            },
        ]
    }
    client = TestClient(app)
    resp = client.get("/ui_cluster_info/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cluster_cpu_usage"] == 1500
    assert data["cluster_memory_usage"] == 1536
    assert data["cluster_cpu_availability"] == 3000
    assert data["cluster_memory_availability"] == 3072
    assert data["cluster_cpu_utilization"] == 50.0
    assert data["cluster_memory_utilization"] == 50.0

@patch("app.api.k8s.cluster_ui.k8s_cluster_info.get_cluster_info")
def test_get_ui_cluster_statistic_info_zero_allocatable(mock_get_cluster_info):
    """
    Test the cluster statistic info endpoint with no allocatable resources.
    This test checks if the endpoint handles cases where allocatable resources are zero,
    resulting in zero utilization percentages.
    """
    # No allocatable resources
    mock_get_cluster_info.return_value = {
        "nodes": [
            {"usage": {"cpu": "0m", "memory": "0Mi"}, "allocatable": {"cpu": "0m", "memory": "0Mi"}}
        ]
    }
    client = TestClient(app)
    resp = client.get("/ui_cluster_info/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cluster_cpu_utilization"] == 0.0
    assert data["cluster_memory_utilization"] == 0.0
