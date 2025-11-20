"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    activities.clear()
    activities.update({
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
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_includes_participant_info(self, client):
        """Test that activities include participant information"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        assert "participants" in chess_club
        assert "michael@mergington.edu" in chess_club["participants"]
        assert chess_club["max_participants"] == 12


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_existing_activity(self, client):
        """Test successful signup for an existing activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]

        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_for_full_activity(self, client):
        """Test signup when activity is at max capacity"""
        # Fill up Chess Club to max capacity
        activities["Chess Club"]["participants"] = [
            f"student{i}@mergington.edu" for i in range(12)
        ]

        response = client.post(
            "/activities/Chess Club/signup?email=latestudent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Activity is full"

    def test_signup_increments_participant_count(self, client):
        """Test that signup increases participant count"""
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Programming Class"]["participants"])

        client.post(
            "/activities/Programming Class/signup?email=newstudent@mergington.edu"
        )

        final_response = client.get("/activities")
        final_count = len(final_response.json()["Programming Class"]["participants"])

        assert final_count == initial_count + 1


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_unregister_existing_participant(self, client):
        """Test successful removal of an existing participant"""
        response = client.delete(
            "/activities/Chess Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed michael@mergington.edu from Chess Club" in data["message"]

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant(self, client):
        """Test removal of a participant not in the activity"""
        response = client.delete(
            "/activities/Chess Club/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Participant not found in this activity"

    def test_unregister_from_nonexistent_activity(self, client):
        """Test removal from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Activity/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_decrements_participant_count(self, client):
        """Test that unregister decreases participant count"""
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])

        client.delete(
            "/activities/Chess Club/participants/michael@mergington.edu"
        )

        final_response = client.get("/activities")
        final_count = len(final_response.json()["Chess Club"]["participants"])

        assert final_count == initial_count - 1

    def test_unregister_and_signup_again(self, client):
        """Test that a participant can be removed and sign up again"""
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Remove participant
        delete_response = client.delete(f"/activities/{activity}/participants/{email}")
        assert delete_response.status_code == 200

        # Sign up again
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200

        # Verify participant is back
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
