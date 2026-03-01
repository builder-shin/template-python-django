from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models


class CommentQuerySet(models.QuerySet):
    def by_post(self, post_id):
        return self.filter(post_id=post_id)

    def by_user(self, user_id):
        return self.filter(user_id=user_id)

    def recent(self):
        return self.order_by("-created_at")

    def root_comments(self):
        return self.filter(parent__isnull=True)


class Comment(models.Model):
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField(
        validators=[MinLengthValidator(1), MaxLengthValidator(2000)],
    )
    user_id = models.CharField(max_length=255, db_index=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CommentQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["post", "created_at"], name="idx_comments_post_created"),
        ]

    def __str__(self):
        return f"Comment by {self.user_id} on Post {self.post_id}"

    def clean(self):
        super().clean()
        errors = {}
        if self.parent and self.parent.post_id != self.post_id:
            errors["parent"] = "대댓글은 같은 글의 댓글에만 달 수 있습니다."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):  # noqa: DJ012
        if not kwargs.get("update_fields"):
            self.full_clean()
        super().save(*args, **kwargs)

    def is_reply(self):
        return self.parent_id is not None

    def reply_count(self):
        return self.replies.count()

    def author_name(self):
        return f"User#{self.user_id}" if self.user_id else "Unknown"
