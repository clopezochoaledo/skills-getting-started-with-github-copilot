"""
Tests for the Mergington High School API

Tests cover the happy-path scenarios for all endpoints:
- GET / (root redirect)
- GET /activities (retrieve all activities)
- POST /activities/{activity_name}/signup (sign up for an activity)
- DELETE /activities/{activity_name}/participant (unregister from an activity)
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_root_redirect():
    """Test that GET / redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [307, 302]  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_all_activities():
    """Test that GET /activities returns all available activities with correct structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    
    # Verify all 7 activities are returned
    assert len(activities) == 7
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    assert "Art Studio" in activities
    assert "Drama Club" in activities
    assert "Debate Team" in activities
    assert "Robotics Club" in activities
    
    # Verify structure of an activity
    activity = activities["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)
    
    # Verify Chess Club has initial participants
    assert len(activity["participants"]) > 0


def test_signup_for_activity():
    """Test that a student can successfully sign up for an activity"""
    activity_name = "Programming Class"
    email = "test_student@mergington.edu"
    
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify student was actually added by checking activities endpoint
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]


def test_unregister_from_activity():
    """Test that a student can successfully unregister from an activity"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This student is pre-signed up
    
    response = client.delete(
        f"/activities/{activity_name}/participant",
        params={"email": email}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify student was actually removed by checking activities endpoint
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]
