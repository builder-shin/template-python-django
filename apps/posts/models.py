from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db.models import Avg, F
from django.db.models.functions import Lower
from django.utils import timezone


class PostQuerySet(models.QuerySet):
    def recent(self):
        return self.order_by("-created_at")

    def published_only(self):
        return self.filter(status=Post.Status.PUBLISHED)

    def draft(self):
        return self.filter(status=Post.Status.DRAFT)

    def archived(self):
        return self.filter(status=Post.Status.ARCHIVED)

    def active(self):
        return self.exclude(status=Post.Status.ARCHIVED)

    def by_user(self, user_id):
        return self.filter(user_id=user_id)

    def search_by_title(self, query):
        if not query:
            return self
        return self.filter(title__icontains=query)

    def popular(self, min_views=100):
        return self.filter(view_count__gte=min_views)

    def created_between(self, start_date, end_date):
        from datetime import datetime, time as dt_time
        if hasattr(start_date, 'date'):
            start = start_date
        else:
            start = datetime.combine(start_date, dt_time.min)
        if hasattr(end_date, 'date'):
            end = end_date
        else:
            end = datetime.combine(end_date, dt_time.max)
        return self.filter(created_at__range=(start, end))

    def today_count(self):
        today = timezone.now().date()
        return self.filter(created_at__date=today).count()

    def most_popular(self, limit=10):
        return self.filter(status=Post.Status.PUBLISHED).order_by("-view_count")[:limit]

    def statistics(self):
        return {
            "total": self.count(),
            "published": self.filter(status=Post.Status.PUBLISHED).count(),
            "draft": self.filter(status=Post.Status.DRAFT).count(),
            "archived": self.filter(status=Post.Status.ARCHIVED).count(),
            "average_views": round(self.aggregate(avg=Avg("view_count"))["avg"] or 0, 2),
        }


class Post(models.Model):
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
    user_id = models.CharField(max_length=255, db_index=True)
    external_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"], name="idx_posts_status"),
        ]
        constraints = [
            models.UniqueConstraint(
                Lower("title"), "user_id",
                name="unique_post_title_per_user",
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

    def save(self, *args, **kwargs):
        self._strip_title()
        self._set_published_at_if_published()
        if not kwargs.get("update_fields"):
            self.full_clean()
        super().save(*args, **kwargs)

    def _strip_title(self):
        if self.title:
            self.title = self.title.strip()

    def _set_published_at_if_published(self):
        if not self._state.adding:
            return
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

    def increment_view_count(self):
        Post.objects.filter(pk=self.pk).update(
            view_count=F("view_count") + 1,
        )
        self.refresh_from_db(fields=["view_count"])

    def publishable(self):
        return self.status == self.Status.DRAFT and bool(self.title) and bool(self.content)

    def publish(self):
        if not self.publishable():
            return False
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.save()
        return True

    def archive(self):
        self.status = self.Status.ARCHIVED
        self.save()
        return True

    def days_since_published(self):
        if not self.published_at:
            return None
        return (timezone.now() - self.published_at).days

    def summary(self, length=100):
        if not self.content:
            return ""
        if len(self.content) <= length:
            return self.content
        truncated = self.content[:length].rsplit(" ", 1)[0]
        return truncated + "..."

    def author_name(self):
        return f"User#{self.user_id}" if self.user_id else "Unknown"

    def comment_count(self):
        if not self.pk:
            return 0
        return self.comments.count()
