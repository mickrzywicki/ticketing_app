import factory

from apps.accounts.factories import UserFactory

from .models import Ticket


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    title = factory.Sequence(lambda n: f"Ticket {n}")
    description = "Something does not work."
    created_by = factory.SubFactory(UserFactory)  # FactoryBot: association :created_by
