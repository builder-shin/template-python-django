from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from apps.core.models import BaseModel, BaseQuerySet


class MemberQuerySet(BaseQuerySet):
    def active(self):
        return self.filter(status=Member.Status.ACTIVE)

    def suspended(self):
        return self.filter(status=Member.Status.SUSPENDED)


class Member(BaseModel):
    class Status(models.IntegerChoices):
        ACTIVE = 0, "active"
        SUSPENDED = 1, "suspended"
        WITHDRAWN = 2, "withdrawn"

    user_id = models.CharField(max_length=255, unique=True, db_index=True)
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

    objects = MemberQuerySet.as_manager()

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

    def is_active(self):
        return self.status == self.Status.ACTIVE

    def suspend(self):
        self.status = self.Status.SUSPENDED
        self.save()
        return True

    def withdraw(self):
        self.status = self.Status.WITHDRAWN
        self.save()
        return True

    def display_name(self):
        return self.nickname if self.nickname else f"User#{self.user_id}"
