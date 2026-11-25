from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model.

    Defined before the first migration so it can be extended later
    (switching AUTH_USER_MODEL mid-project is painful in Django).
    """

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        AGENT = "agent", "Agent"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)

    @property  # Rails: def staff_member? ... end  (called without parentheses)
    def is_support_staff(self) -> bool:
        """Agents and admins can see and handle every ticket."""
        return self.role in {self.Role.AGENT, self.Role.ADMIN}
