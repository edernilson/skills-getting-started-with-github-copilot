from fastapi.testclient import TestClient
import urllib.parse
import copy

from src import app as application

client = TestClient(application.app)


def setup_function():
    # backup global in-memory activities
    global _activities_backup
    _activities_backup = copy.deepcopy(application.activities)


def teardown_function():
    # restore original activities state
    application.activities.clear()
    application.activities.update(copy.deepcopy(_activities_backup))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_delete_participant_flow():
    activity = "Chess Club"
    email = "testuser@example.com"

    # signup
    resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # verify present
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email in data[activity]["participants"]

    # duplicate signup should return 400
    resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}")
    assert resp.status_code == 400

    # delete participant
    resp = client.delete(f"/activities/{urllib.parse.quote(activity)}/participants?email={urllib.parse.quote(email)}")
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")

    # verify removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]


def test_delete_missing_participant():
    activity = "Chess Club"
    email = "noone@example.com"
    resp = client.delete(f"/activities/{urllib.parse.quote(activity)}/participants?email={urllib.parse.quote(email)}")
    assert resp.status_code == 404
