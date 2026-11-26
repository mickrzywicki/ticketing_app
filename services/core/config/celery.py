"""Celery app. Rails equivalent: Sidekiq configuration.

Run a worker with:  uv run celery -A config worker -l info
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("helpdesk")
# Read every setting prefixed with CELERY_ from Django settings (CELERY_BROKER_URL, ...).
app.config_from_object("django.conf:settings", namespace="CELERY")
# Find tasks.py in every installed app (like Sidekiq loading app/jobs).
app.autodiscover_tasks()
