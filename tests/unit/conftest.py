"""
Pytest configuration and fixtures for unit tests.

This module provides reusable fixtures following the AAA (Arrange-Act-Assert) pattern:
- Arrange: Fixtures set up test data, app instance, and test client
- Act: Tests use the client to call endpoints
- Assert: Tests verify responses and state changes
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    ARRANGE: Provides a FastAPI TestClient for making requests to endpoints.
    
    This fixture creates a TestClient connected to the main FastAPI app,
    allowing tests to make HTTP requests without starting a real server.
    
    Returns:
        TestClient: A test client for the FastAPI application
    """
    return TestClient(app)


@pytest.fixture
def reset_activities(monkeypatch):
    """
    ARRANGE: Resets the in-memory activities database before and after each test.
    
    This fixture ensures test isolation by resetting the shared activities dictionary
    to a known state before each test runs. This prevents test pollution where
    one test's changes affect another test.
    
    Args:
        monkeypatch: Pytest's monkeypatch fixture for modifying module state
        
    Yields:
        None: The fixture yields control to the test
    """
    from src import app as app_module
    
    # Save original activities state
    original_activities = {
        key: {
            "description": val["description"],
            "schedule": val["schedule"],
            "max_participants": val["max_participants"],
            "participants": val["participants"].copy()
        }
        for key, val in app_module.activities.items()
    }
    
    yield
    
    # Restore original activities after test
    app_module.activities.clear()
    app_module.activities.update(original_activities)


@pytest.fixture
def sample_email():
    """
    ARRANGE: Provides a valid sample email for testing signup/removal operations.
    
    Returns:
        str: A valid email address
    """
    return "test.student@mergington.edu"


@pytest.fixture
def existing_email():
    """
    ARRANGE: Provides an email of a student already signed up for an activity.
    
    Returns:
        str: Email of an existing participant
    """
    return "michael@mergington.edu"


@pytest.fixture
def existing_activity():
    """
    ARRANGE: Provides the name of an activity that exists in the database.
    
    Returns:
        str: Name of an existing activity
    """
    return "Chess Club"


@pytest.fixture
def nonexistent_activity():
    """
    ARRANGE: Provides the name of an activity that does not exist.
    
    Returns:
        str: Name of a non-existent activity
    """
    return "Nonexistent Club"
