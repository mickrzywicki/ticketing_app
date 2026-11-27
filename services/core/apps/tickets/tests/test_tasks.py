from unittest.mock import patch

import httpx
import pytest

from apps.accounts.factories import AgentFactory, UserFactory
from apps.tickets.factories import CommentFactory, TicketFactory
from apps.tickets.tasks import notify_comment_created

pytestmark = pytest.mark.django_db

POST = "apps.tickets.tasks.httpx.post"  # patch where it's used, not where it's defined


def test_notifies_ticket_author_when_someone_else_comments():
    customer = UserFactory(email="alice@example.com")
    ticket = TicketFactory(created_by=customer)
    comment = CommentFactory(ticket=ticket, author=AgentFactory(username="bob"), body="On it")

    with patch(POST) as post:
        notify_comment_created(comment.id)  # called directly: runs now, no Celery

    post.assert_called_once()
    event = post.call_args.kwargs["json"]
    assert event == {
        "type": "comment.created",
        "ticket_id": ticket.id,
        "recipient": "alice@example.com",
        "message": f"bob commented on ticket #{ticket.id}: On it",
    }


def test_notifies_assignee_when_author_comments():
    customer = UserFactory(username="Alice", email="alice@example.com")
    ticket = TicketFactory(
        created_by=customer, assignee=AgentFactory(username="bob", email="bob@example.com")
    )
    comment = CommentFactory(ticket=ticket, author=customer, body="On it")

    with patch(POST) as post:
        notify_comment_created(comment.id)

    post.assert_called_once()
    event = post.call_args.kwargs["json"]
    assert event == {
        "type": "comment.created",
        "ticket_id": ticket.id,
        "recipient": "bob@example.com",
        "message": f"Alice commented on ticket #{ticket.id}: On it",
    }


def test_skips_when_author_comments_and_nobody_assigned():
    customer = UserFactory(email="alice@example.com")
    ticket = TicketFactory(created_by=customer)
    comment = CommentFactory(ticket=ticket, author=customer, body="On it")

    with patch(POST) as post:
        notify_comment_created(comment.id)

    post.assert_not_called()


def test_skips_when_recipient_has_no_email():
    customer = UserFactory(username="Alice", email="")
    ticket = TicketFactory(created_by=customer)
    comment = CommentFactory(ticket=ticket, author=AgentFactory(username="bob"), body="On it")

    with patch(POST) as post:
        notify_comment_created(comment.id)

    post.assert_not_called()


def test_skips_when_comment_was_deleted():
    comment = CommentFactory()
    comment_id = comment.id
    comment.delete()

    with patch(POST) as post:
        notify_comment_created(comment_id)

    post.assert_not_called()


def test_raises_on_error_response_so_celery_retries():
    customer = UserFactory(email="alice@example.com")
    ticket = TicketFactory(created_by=customer)
    comment = CommentFactory(ticket=ticket, author=AgentFactory(username="bob"), body="On it")

    with patch(POST) as post:
        post.return_value = httpx.Response(
            503, request=httpx.Request("POST", "http://notifier/events")
        )
        with pytest.raises(httpx.HTTPStatusError):
            notify_comment_created(comment.id)
