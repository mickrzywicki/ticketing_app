from rest_framework import serializers

from apps.accounts.models import User

from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    """Ticket <-> JSON. Rails equivalent: strong params + a JSON serializer in one class."""

    # Show the author's username instead of a bare user id in responses.
    created_by: serializers.StringRelatedField[User] = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "created_by",
            "assignee",
            "created_at",
            "updated_at",
        ]
        # Client can't send these; they are set by the server.
        # Rails: they are simply left out of params.permit(...)
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
