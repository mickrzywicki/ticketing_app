import pytest

VALID_EVENT = {
    "type": "comment.created",
    "ticket_id": 12,
    "recipient": "alice@example.com",
    "message": "Bob commented on ticket #12",
}


def test_valid_event_is_accepted(client):
    response = client.post("/events", json=VALID_EVENT)

    assert response.status_code == 202
    assert response.get_json() == {"status": "accepted"}

# Testing only one param missing
# def test_missing_field_returns_400(client):
#     response = client.post("/events", json={k: v for k, v in VALID_EVENT.items() if k != "recipient"})

#     assert response.status_code == 400
#     assert response.get_json() == {"error": "Missing required fields", "missing": ["recipient"]}

# Works like .each with it inside. RSpec style
@pytest.mark.parametrize("field", ["type", "ticket_id", "recipient", "message"])
def test_missing_fields_returns_400(client, field):
    response = client.post("/events", json={k: v for k, v in VALID_EVENT.items() if k != field})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing required fields", "missing": [field]}


def test_non_json_body_returns_400(client):
    response = client.post("/events", data="{not valid json", content_type="application/json")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Request body must be a JSON object"}
