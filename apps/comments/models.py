from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from apps.core.models import HARD_CASCADE_SOFT_CHILDREN, SOFT_CASCADE, BaseModel, SoftDeleteMixin


class Comment(SoftDeleteMixin, BaseModel):
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField(
        validators=[MinLengthValidator(1), MaxLengthValidator(2000)],
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )

    soft_delete_cascade = {
        "post": SOFT_CASCADE,
        "parent": HARD_CASCADE_SOFT_CHILDREN,
    }

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=["post", "created_at"], name="idx_comments_post_created"),
        ]

    def __str__(self):
        return f"Comment by {self.user} on Post {self.post_id}"

    def clean(self):
        super().clean()
        errors = {}
        if self.parent and self.parent.post_id != self.post_id:
            errors["parent"] = "대댓글은 같은 글의 댓글에만 달 수 있습니다."
        if errors:
            raise ValidationError(errors)
