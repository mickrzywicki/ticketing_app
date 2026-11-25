import pytest

from apps.accounts.factories import UserFactory
from apps.tickets.factories import CommentFactory, TicketFactory
from apps.tickets.models import Comment

pytestmark = pytest.mark.django_db  # every test in this file may use the database


def comments_url(ticket):
    return f"/api/tickets/{ticket.id}/comments/"


def test_adding_comments_sets_author_current_user(api_client):
    customer = UserFactory()  # Creating Customer (User)
    ticket = TicketFactory(created_by=customer)  # Creating Ticker
    api_client.force_authenticate(customer)  # Sign in customer

    # Do a POST req
    response = api_client.post(comments_url(ticket), {"body": "Any update?"}, format="json")

    assert response.status_code == 201
    comment = Comment.objects.get(pk=response.json()["id"])
    assert comment.author == customer
    assert comment.ticket == ticket
    assert comment.body == "Any update?"


def test_lists_only_comments_of_given_ticket(api_client):
    customer = UserFactory()  # Creating Customer (User)
    ticket = TicketFactory(created_by=customer)  # Creating Ticket
    CommentFactory.create_batch(2, ticket=ticket)
    other_ticket = TicketFactory(created_by=customer)
    CommentFactory(ticket=other_ticket)
    api_client.force_authenticate(customer)  # Sign in customer

    response = api_client.get(comments_url(ticket))

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_customer_cannot_comment_on_someone_elses_ticket(api_client):
    customer = UserFactory()  # Creating Customer (User)
    other_customer = UserFactory()  # Creating Customer (User)
    ticket = TicketFactory(created_by=other_customer)  # Creating Ticket
    api_client.force_authenticate(customer)

    response = api_client.post(comments_url(ticket), {"body": "Any update?"}, format="json")

    assert response.status_code == 404
    assert Comment.objects.count() == 0
