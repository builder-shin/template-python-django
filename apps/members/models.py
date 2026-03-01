from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models


class MemberQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Member.Status.ACTIVE)

    def suspended(self):
        return self.filter(status=Member.Status.SUSPENDED)

    def by_user(self, user_id):
        return self.filter(user_id=user_id)

    def recent(self):
        return self.order_by("-created_at")


class Member(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MemberQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"], name="idx_members_status"),
        ]

    def __str__(self):
        return self.nickname

    def clean(self):
        super().clean()
        if self.nickname:
            self.nickname = self.nickname.strip()

    def save(self, *args, **kwargs):  # noqa: DJ012
        if self.nickname:
            self.nickname = self.nickname.strip()
        if not kwargs.get("update_fields"):
            self.full_clean()
        super().save(*args, **kwargs)

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
