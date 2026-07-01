import pytest

from app.models.alert import Alert
from app.models.endpoint import Endpoint

def test_get_alerts_empty(client):
    response = client.get("/api/v1/alerts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_create_and_get_alert(client, db_session):
    # Create an endpoint first to satisfy foreign keys
    new_endpoint = Endpoint(
        id="HOST-TEST-01",
        hostname="Test Host",
        ip_address="192.168.1.100",
        os_type="windows"
    )
    db_session.add(new_endpoint)
    db_session.commit()

    # Create an alert directly in DB
    new_alert = Alert(
        endpoint_id="HOST-TEST-01",
        title="Test Alert",
        severity="high",
        rule_type="behavioral"
    )
    db_session.add(new_alert)
    db_session.commit()
    db_session.refresh(new_alert)

    # Get the alert
    get_response = client.get(f"/api/v1/alerts/{new_alert.id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Test Alert"
