import httpx
from celery import shared_task
from django.conf import settings

from .models import Comment


@shared_task(
    autoretry_for=(httpx.HTTPError,),  # retry on network errors and 4xx/5xx (raise_for_status)
    retry_backoff=True,  # wait 1s, 2s, 4s, 8s ... between attempts
    max_retries=5,
)
def notify_comment_created(comment_id: int) -> None:
    """Send a "comment.created" event to the notifier service."""

    try:
        comment = Comment.objects.select_related(
            "author", "ticket__created_by", "ticket__assignee"
        ).get(pk=comment_id)
    except Comment.DoesNotExist:
        return

    # Other version
    # ticket = comment.ticket
    # recipient = ticket.assignee if comment.author == ticket.created_by else ticket.created_by
    # if recipient is None:
    #     return

    if comment.author == comment.ticket.created_by:
        recipient = comment.ticket.assignee
        if recipient is None:
            return
    else:
        recipient = comment.ticket.created_by

    if not recipient.email:
        return

    event = {
        "type": "comment.created",
        "ticket_id": comment.ticket_id,
        "recipient": recipient.email,
        "message": (
            f"{comment.author.username} commented on ticket #{comment.ticket_id}: "
            f"{comment.body[:100]}"
        ),
    }

    response = httpx.post(f"{settings.NOTIFIER_URL}/events", json=event, timeout=5)
    response.raise_for_status()
