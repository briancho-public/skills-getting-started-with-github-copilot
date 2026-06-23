"""
Unit tests for FastAPI endpoints using the AAA (Arrange-Act-Assert) pattern.

Test Coverage:
- GET /activities: Retrieve all activities
- POST /activities/{activity_name}/signup: Sign up a student for an activity
- DELETE /activities/{activity_name}/participants: Remove a participant from an activity

Each test follows the AAA pattern:
1. ARRANGE: Set up test data and preconditions using fixtures
2. ACT: Call the endpoint using the test client
3. ASSERT: Verify the response and state changes
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """
        ARRANGE: Client and activities data are ready via fixtures
        ACT: Make GET request to /activities
        ASSERT: Verify status 200 and all activities are returned
        """
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Soccer Club" in data
        
    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """
        ARRANGE: Client and activities data are ready via fixtures
        ACT: Make GET request to /activities
        ASSERT: Verify each activity has required fields
        """
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        
        # Check first activity has all required fields
        first_activity = data["Chess Club"]
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities, existing_activity, sample_email):
        """
        ARRANGE: Existing activity and new student email provided via fixtures
        ACT: POST request to signup endpoint with valid activity and email
        ASSERT: Verify status 200, success message, and student added to participants
        """
        # ARRANGE
        initial_participants = client.get("/activities").json()[existing_activity]["participants"].copy()
        
        # ACT
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert existing_activity in data["message"]
        
        # Verify participant was actually added
        updated_participants = client.get("/activities").json()[existing_activity]["participants"]
        assert sample_email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1
    
    def test_signup_nonexistent_activity(self, client, reset_activities, nonexistent_activity, sample_email):
        """
        ARRANGE: Non-existent activity name provided via fixture
        ACT: POST request to signup with non-existent activity
        ASSERT: Verify status 404 and appropriate error message
        """
        # ACT
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": sample_email}
        )
        
        # ASSERT
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_participant(self, client, reset_activities, existing_activity, existing_email):
        """
        ARRANGE: Activity with existing participant provided via fixtures
        ACT: POST request to signup with email already registered
        ASSERT: Verify status 400 and appropriate error message
        """
        # ACT
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": existing_email}
        )
        
        # ASSERT
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_multiple_activities_same_student(self, client, reset_activities, sample_email):
        """
        ARRANGE: Sample email and multiple existing activities via fixtures
        ACT: Sign up the same student for multiple activities
        ASSERT: Verify student is successfully added to multiple activities
        """
        # ARRANGE
        activities_to_join = ["Chess Club", "Programming Class", "Soccer Club"]
        
        # ACT & ASSERT
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": sample_email}
            )
            assert response.status_code == 200
        
        # Verify student is in all activities
        all_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert sample_email in all_activities[activity]["participants"]
    
    def test_signup_url_encoded_activity_name(self, client, reset_activities, sample_email):
        """
        ARRANGE: Activity name with spaces via fixture
        ACT: POST request with activity name containing spaces
        ASSERT: Verify signup works with URL-encoded names
        """
        # ARRANGE
        activity_name = "Chess Club"  # Contains space
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        updated_activities = client.get("/activities").json()
        assert sample_email in updated_activities[activity_name]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_remove_participant_success(self, client, reset_activities, existing_activity, existing_email):
        """
        ARRANGE: Existing activity and participant provided via fixtures
        ACT: DELETE request to remove participant from activity
        ASSERT: Verify status 200, success message, and participant removed
        """
        # ARRANGE
        initial_participants = client.get("/activities").json()[existing_activity]["participants"].copy()
        
        # ACT
        response = client.delete(
            f"/activities/{existing_activity}/participants",
            params={"email": existing_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert existing_email in data["message"]
        assert existing_activity in data["message"]
        
        # Verify participant was actually removed
        updated_participants = client.get("/activities").json()[existing_activity]["participants"]
        assert existing_email not in updated_participants
        assert len(updated_participants) == len(initial_participants) - 1
    
    def test_remove_nonexistent_activity(self, client, reset_activities, nonexistent_activity, sample_email):
        """
        ARRANGE: Non-existent activity name provided via fixture
        ACT: DELETE request for non-existent activity
        ASSERT: Verify status 404 and appropriate error message
        """
        # ACT
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants",
            params={"email": sample_email}
        )
        
        # ASSERT
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_remove_unregistered_participant(self, client, reset_activities, existing_activity, sample_email):
        """
        ARRANGE: Existing activity but unregistered student email via fixtures
        ACT: DELETE request to remove student not in activity
        ASSERT: Verify status 400 and appropriate error message
        """
        # ACT
        response = client.delete(
            f"/activities/{existing_activity}/participants",
            params={"email": sample_email}
        )
        
        # ASSERT
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_remove_then_readd_participant(self, client, reset_activities, existing_activity, sample_email):
        """
        ARRANGE: Existing activity and new student via fixtures
        ACT: Signup, remove, then signup again for same activity
        ASSERT: Verify signup->remove->signup sequence works correctly
        """
        # ACT 1: Sign up
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        activities_after_signup = client.get("/activities").json()
        assert sample_email in activities_after_signup[existing_activity]["participants"]
        
        # ACT 2: Remove
        response = client.delete(
            f"/activities/{existing_activity}/participants",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        activities_after_remove = client.get("/activities").json()
        assert sample_email not in activities_after_remove[existing_activity]["participants"]
        
        # ACT 3: Sign up again
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        activities_after_readd = client.get("/activities").json()
        assert sample_email in activities_after_readd[existing_activity]["participants"]
    
    def test_remove_multiple_participants(self, client, reset_activities, existing_activity):
        """
        ARRANGE: Existing activity with multiple participants via fixtures
        ACT: Remove multiple participants one by one
        ASSERT: Verify each removal works independently
        """
        # ARRANGE
        participants_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # ACT & ASSERT
        for email in participants_to_remove:
            response = client.delete(
                f"/activities/{existing_activity}/participants",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all were removed
        remaining_participants = client.get("/activities").json()[existing_activity]["participants"]
        for email in participants_to_remove:
            assert email not in remaining_participants
