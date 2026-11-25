import pytest

from apps.accounts.factories import AgentFactory, UserFactory
from apps.tickets.factories import TicketFactory
from apps.tickets.models import Ticket

pytestmark = pytest.mark.django_db  # every test in this file may use the database

URL = "/api/tickets/"


def test_requires_authentication(api_client):
    response = api_client.get(URL)

    assert response.status_code == 401


def test_customer_sees_only_own_tickets(api_client):
    customer = UserFactory()
    own = TicketFactory(created_by=customer)
    TicketFactory()  # someone else's ticket
    api_client.force_authenticate(customer)  # skip JWT in tests, like sign_in in Devise

    response = api_client.get(URL)

    assert response.status_code == 200
    assert [t["id"] for t in response.json()["results"]] == [own.id]


def test_agent_sees_all_tickets(api_client):
    TicketFactory.create_batch(3)
    api_client.force_authenticate(AgentFactory())

    response = api_client.get(URL)

    assert response.json()["count"] == 3


def test_customer_cannot_open_someone_elses_ticket(api_client):
    other_ticket = TicketFactory()
    api_client.force_authenticate(UserFactory())

    response = api_client.get(f"{URL}{other_ticket.id}/")

    assert response.status_code == 404  # hidden by get_queryset, not just forbidden


def test_create_sets_author_from_request_user(api_client):
    customer = UserFactory()
    api_client.force_authenticate(customer)

    response = api_client.post(
        URL, {"title": "Login broken", "description": "500 on /login"}, format="json"
    )

    assert response.status_code == 201
    ticket = Ticket.objects.get(pk=response.json()["id"])
    assert ticket.created_by == customer
    assert ticket.status == Ticket.Status.OPEN
