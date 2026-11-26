from flask import Blueprint, jsonify

bp = Blueprint("notifier", __name__)


@bp.get("/health")
def health():
    return jsonify(status="ok")


# TODO: POST /events: receive an event from core and create a notification.
