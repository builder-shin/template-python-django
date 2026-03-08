from django.db import models


class BaseQuerySet(models.QuerySet):
    """도메인 QuerySet의 공통 메서드를 제공하는 베이스 QuerySet."""


class BaseModel(models.Model):
    """공통 타임스탬프 필드와 save 시 full_clean 호출을 제공하는 추상 기본 모델."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def pre_save(self):
        """서브클래스에서 override하여 save 전 전처리 로직을 추가한다."""

    def save(self, *args, **kwargs):  # noqa: DJ012
        self.pre_save()
        if not kwargs.get("update_fields"):
            self.full_clean()
        super().save(*args, **kwargs)
