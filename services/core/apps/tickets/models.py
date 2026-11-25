from django.conf import settings
from django.db import models


class Ticket(models.Model):
    """A support request created by a customer and handled by an agent."""

    # Like a Rails `enum status: {...}`, but stored as readable strings in the DB.
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    title = models.CharField(max_length=200)  # Rails: t.string
    description = models.TextField()  # Rails: t.text
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)

    # Rails: belongs_to :created_by, class_name: "User"
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # can't delete a user who still has tickets
        related_name="created_tickets",  # user.created_tickets.all()
    )
    # Rails: belongs_to :assignee, class_name: "User", optional: true
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # if the agent is deleted, the ticket becomes unassigned
        null=True,  # column may be NULL in the database
        blank=True,  # field may be empty in validation (serializers, admin)
        related_name="assigned_tickets",
    )

    # Rails: t.timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # set once on create
    updated_at = models.DateTimeField(auto_now=True)  # updated on every save

    class Meta:
        ordering = ["-created_at"]  # Rails: default_scope { order(created_at: :desc) }
        indexes = [models.Index(fields=["status", "priority"])]

    def __str__(self) -> str:  # Rails: to_s; shown in admin and shell
        return f"#{self.pk} {self.title}"


class Comment(models.Model):
    ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="authored_comments",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self.ticket_id}"
