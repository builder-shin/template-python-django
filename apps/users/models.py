from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models


class User(AbstractUser):
    class Status(models.IntegerChoices):
        ACTIVE = 0, "active"
        SUSPENDED = 1, "suspended"
        WITHDRAWN = 2, "withdrawn"

    email = models.EmailField("email address", unique=True)

    nickname = models.CharField(
        max_length=50,
        blank=True,
        default="",
        validators=[MinLengthValidator(2), MaxLengthValidator(50)],
    )
    bio = models.TextField(blank=True, default="")
    avatar_url = models.URLField(blank=True, null=True)
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta(AbstractUser.Meta):
        indexes = [
            models.Index(fields=["status"], name="idx_users_status"),
        ]

    def __str__(self):
        return self.nickname or self.username

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        if self.nickname:
            self.nickname = self.nickname.strip()
        if not kwargs.get("update_fields"):
            self.full_clean()
        super().save(*args, **kwargs)
