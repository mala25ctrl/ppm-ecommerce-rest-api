from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        CUSTOMER = 'CUSTOMER', 'Customer'

    role = models.CharField(max_length=10, choices=Role, default=Role.CUSTOMER)

    def __str__(self):
        return f"{self.username} ({self.role})"
