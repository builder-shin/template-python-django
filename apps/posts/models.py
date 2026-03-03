from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from apps.core.models import BaseModel


class Post(BaseModel):
    class Status(models.IntegerChoices):
        DRAFT = 0, "draft"
        PUBLISHED = 1, "published"
        ARCHIVED = 2, "archived"

    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2), MaxLengthValidator(200)],
    )
    content = models.TextField(blank=True, default="")
    view_count = models.PositiveIntegerField(default=0)
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.DRAFT,
    )
    published_at = models.DateTimeField(null=True, blank=True)
    member = models.ForeignKey(
        "members.Member",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    external_id = models.CharField(max_length=255, null=True, blank=True, unique=True)

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=["status"], name="idx_posts_status"),
        ]
        constraints = [
            models.UniqueConstraint(
                Lower("title"),
                "member",
                name="unique_post_title_per_member",
            ),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        errors = {}
        if self.status == self.Status.PUBLISHED and self.published_at and self.published_at > timezone.now():
            errors["published_at"] = "발행일은 미래 날짜일 수 없습니다."
        if self.status == self.Status.PUBLISHED and not self.content:
            errors["content"] = "게시 상태에서는 내용이 필수입니다."
        if errors:
            raise ValidationError(errors)

    def pre_save(self):
        self._strip_title()
        self._set_published_at_if_published()

    def _strip_title(self):
        if self.title:
            self.title = self.title.strip()

    def _set_published_at_if_published(self):
        if not self._state.adding:
            return
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
