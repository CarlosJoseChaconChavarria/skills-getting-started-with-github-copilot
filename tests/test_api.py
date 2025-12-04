import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Sample activities data for testing"""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        }
    }


class TestActivitiesAPI:
    """Test cases for the Activities API"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")

        assert response.status_code == 200
        activities = response.json()

        # Check that we get a dictionary of activities
        assert isinstance(activities, dict)
        assert len(activities) > 0

        # Check structure of first activity
        first_activity = next(iter(activities.values()))
        required_keys = ["description", "schedule", "max_participants", "participants"]
        for key in required_keys:
            assert key in first_activity

    def test_get_activities_contains_expected_data(self, client):
        """Test that activities contain expected data"""
        response = client.get("/activities")
        activities = response.json()

        # Check that Chess Club exists and has correct data
        assert "Chess Club" in activities
        chess_club = activities["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]

    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        # Use an activity that exists
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert f"Signed up {email} for {activity_name}" == result["message"]

        # Verify the student was added to the activity
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        activity_name = "NonExistent Activity"
        email = "student@mergington.edu"

        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Activity not found"

    def test_signup_duplicate_registration(self, client):
        """Test signup when student is already registered"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # This student is already registered

        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        assert response.status_code == 400
        result = response.json()
        assert result["detail"] == "Student already signed up for this activity"

    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # This student is registered

        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert f"Unregistered {email} from {activity_name}" == result["message"]

        # Verify the student was removed from the activity
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity"""
        activity_name = "NonExistent Activity"
        email = "student@mergington.edu"

        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Activity not found"

    def test_unregister_student_not_registered(self, client):
        """Test unregister when student is not registered"""
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"  # This student is not registered

        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        assert response.status_code == 400
        result = response.json()
        assert result["detail"] == "Student is not registered for this activity"

    def test_root_redirect(self, client):
        """Test root endpoint redirects to static file"""
        response = client.get("/")

        assert response.status_code == 200  # FastAPI TestClient follows redirects by default
        # The redirect response should contain the static file content
        assert "Mergington High School" in response.text