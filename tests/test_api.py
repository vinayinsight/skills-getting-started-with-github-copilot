from urllib.parse import quote

from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    endpoint = "/"

    # Act
    response = client.get(endpoint, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Programming Class" in payload

    programming_class = payload["Programming Class"]
    assert "description" in programming_class
    assert "schedule" in programming_class
    assert "max_participants" in programming_class
    assert "participants" in programming_class


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Programming Class"
    email = "new.student@mergington.edu"
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_returns_bad_request_for_duplicate_participant(client):
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_validation_error_when_email_missing(client):
    # Arrange
    activity_name = "Programming Class"
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 422


def test_unregister_from_activity_removes_participant(client):
    # Arrange
    activity_name = "Programming Class"
    email = "remove.me@mergington.edu"
    activities[activity_name]["participants"].append(email)
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.delete(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.delete(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_not_found_when_participant_not_registered(client):
    # Arrange
    activity_name = "Programming Class"
    email = "not.registered@mergington.edu"
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.delete(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_returns_validation_error_when_email_missing(client):
    # Arrange
    activity_name = "Programming Class"
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 422


def test_signup_supports_url_encoded_activity_and_email(client):
    # Arrange
    activity_name = "Chess Club1"
    email = "encoded+student@mergington.edu"
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
