import factory
from django.contrib.auth import get_user_model

from .models import User


class UserFactory(factory.django.DjangoModelFactory):
    """Rails/FactoryBot: factory :user do ... end"""

    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user{n}")  # sequence(:username) { |n| "user#{n}" }
    email = factory.LazyAttribute(lambda u: f"{u.username}@example.com")
    password = factory.django.Password("s3cret-pass!")  # stored hashed
    role = User.Role.CUSTOMER


class AgentFactory(UserFactory):
    """FactoryBot trait-like subclass: create(:user, :agent)"""

    role = User.Role.AGENT
