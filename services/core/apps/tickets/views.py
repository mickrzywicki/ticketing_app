from django.db import transaction
from django.db.models import QuerySet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from apps.accounts.models import User

from .models import Ticket
from .serializers import CommentSerializer, TicketSerializer
from .tasks import notify_comment_created


class TicketViewSet(viewsets.ModelViewSet):
    """CRUD for tickets: list, retrieve, create, update, partial_update, destroy.

    Rails equivalent: TicketsController with index/show/create/update/destroy.
    Authentication (JWT) and IsAuthenticated come from REST_FRAMEWORK in settings.
    """

    serializer_class = TicketSerializer
    filterset_fields = ["status", "priority"]  # ?status=open&priority=high
    ordering_fields = ["created_at", "priority"]  # ?ordering=-created_at

    @property
    def current_user(self) -> User:
        # For the type checker request.user may be AnonymousUser; IsAuthenticated
        # guarantees it isn't, and the assert documents (and enforces) that.
        user = self.request.user
        assert isinstance(user, User)
        return user

    def get_queryset(self) -> QuerySet[Ticket]:
        # Rails: current_user.staff? ? Ticket.all : current_user.created_tickets
        # select_related = Rails includes(...) for belongs_to: avoids N+1 queries.
        tickets = Ticket.objects.select_related("created_by", "assignee")
        if getattr(self, "swagger_fake_view", False):
            # OpenAPI schema generation calls this without a logged-in user.
            return tickets.none()
        if self.current_user.is_support_staff:
            return tickets
        return tickets.filter(created_by=self.current_user)

    def perform_create(self, serializer: BaseSerializer[Ticket]) -> None:
        # Rails: current_user.created_tickets.create!(ticket_params)
        serializer.save(created_by=self.current_user)

    @action(detail=True, methods=["get", "post"], serializer_class=CommentSerializer)
    def comments(self, request, pk=None):
        """List comments of a ticket (GET) or add a new one (POST)."""

        ticket = self.get_object()
        if request.method == "GET":
            serializer = self.get_serializer(ticket.comments.all(), many=True)
            return Response(serializer.data)
        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save(ticket=ticket, author=self.current_user)
            transaction.on_commit(lambda: notify_comment_created.delay(comment.id))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
