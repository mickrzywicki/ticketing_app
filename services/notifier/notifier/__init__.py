"""Notifier microservice.

Receives events from the core service (e.g. "comment.created") and turns them
into notifications. Uses the Flask "application factory" pattern: create_app()
builds a fresh app, which makes testing with different config easy.
"""

from flask import Flask


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_prefixed_env("NOTIFIER")  # NOTIFIER_FOO=bar -> app.config["FOO"]
    if config:
        app.config.update(config)

    # Without an explicit level, app.logger inherits WARNING under Gunicorn and
    # logger.info(...) calls are silently dropped. NOTIFIER_LOG_LEVEL overrides it.
    app.logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))

    # Blueprints group routes, a bit like a Rails controller + its routes.
    from .routes import bp

    app.register_blueprint(bp)
    return app
