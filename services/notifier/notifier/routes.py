from flask import Blueprint, current_app, jsonify, request

bp = Blueprint("notifier", __name__)


@bp.get("/health")
def health():
    return jsonify(status="ok")


REQUIRED_FIELDS = ("type", "ticket_id", "recipient", "message")


@bp.post("/events")
def receive_event():
    """Receive an event from core and send a notification.

    Example payload:
        {"type": "comment.created", "ticket_id": 12,
         "recipient": "alice@example.com", "message": "Bob commented on #12"}
    """
    event = request.get_json(silent=True)

    if not isinstance(event, dict):
        return jsonify(error="Request body must be a JSON object"), 400

    missing = [field for field in REQUIRED_FIELDS if field not in event]
    if missing:
        return jsonify(error="Missing required fields", missing=missing), 400

    current_app.logger.info("Notify %s: %s", event["recipient"], event["message"])

    return jsonify(status="accepted"), 202
