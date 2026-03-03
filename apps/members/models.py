from django.conf import settings
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from apps.core.models import BaseModel


class Member(BaseModel):
    class Status(models.IntegerChoices):
        ACTIVE = 0, "active"
        SUSPENDED = 1, "suspended"
        WITHDRAWN = 2, "withdrawn"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member",
    )
    nickname = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(2), MaxLengthValidator(50)],
    )
    bio = models.TextField(blank=True, default="")
    avatar_url = models.URLField(blank=True, null=True)
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=["status"], name="idx_members_status"),
        ]

    def __str__(self):
        return self.nickname

    def pre_save(self):
        if self.nickname:
            self.nickname = self.nickname.strip()

    def clean(self):
        super().clean()
        if self.nickname:
            self.nickname = self.nickname.strip()
