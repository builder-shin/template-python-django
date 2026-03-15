"""SoftDeleteMixin — 선택적 soft delete 기능을 제공하는 독립 Mixin.

Phase 1: SoftDeleteQuerySet, SoftDeleteManager, SoftDeleteAllManager
Phase 2: SoftDeleteMixin (delete, restore, is_deleted)
Phase 3: Cascade policies (SOFT_CASCADE, HARD_CASCADE_SOFT_CHILDREN, SOFT_CASCADE_HARD_CHILDREN)
"""

from __future__ import annotations

from django.db import models, transaction
from django.utils import timezone

# ---------------------------------------------------------------------------
# Cascade policy constants
# ---------------------------------------------------------------------------
SOFT_CASCADE = "SOFT_CASCADE"
HARD_CASCADE_SOFT_CHILDREN = "HARD_CASCADE_SOFT_CHILDREN"
SOFT_CASCADE_HARD_CHILDREN = "SOFT_CASCADE_HARD_CHILDREN"

ALL_POLICIES = {SOFT_CASCADE, HARD_CASCADE_SOFT_CHILDREN, SOFT_CASCADE_HARD_CHILDREN}


# ---------------------------------------------------------------------------
# Phase 1: QuerySet + Manager
# ---------------------------------------------------------------------------


class SoftDeleteQuerySet(models.QuerySet):
    """alive/dead/all_with_deleted 필터 + bulk soft delete 안전장치."""

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)

    def delete(self):
        """Bulk soft delete — UPDATE deleted_at. Cascade 미적용.

        cascade가 필요한 경우 각 인스턴스의 .delete()를 호출하세요.
        """
        count = self.update(deleted_at=timezone.now())
        return (count, {self.model._meta.label: count})

    def hard_delete(self):
        """Bulk 물리 삭제."""
        return super().delete()


class SoftDeleteManager(models.Manager):
    """기본 Manager — deleted_at IS NULL 자동 필터."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def alive(self):
        return self.get_queryset()

    def dead(self):
        return SoftDeleteQuerySet(self.model, using=self._db).dead()


class SoftDeleteAllManager(models.Manager):
    """필터 없는 Manager — all_objects 용."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


# ---------------------------------------------------------------------------
# Phase 2 + 3: Mixin
# ---------------------------------------------------------------------------


class SoftDeleteMixin(models.Model):
    """선택적 soft delete 기능을 제공하는 추상 Mixin.

    Usage::

        class MyModel(SoftDeleteMixin, BaseModel):
            soft_delete_cascade = {
                "parent_fk_field": SOFT_CASCADE,
            }
    """

    deleted_at = models.DateTimeField(null=True, blank=True, default=None, db_index=True)
    deleted_by_cascade = models.BooleanField(default=False)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteAllManager()

    soft_delete_cascade: dict[str, str] = {}

    class Meta:
        abstract = True

    # -- properties --

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    # -- delete / restore --

    def delete(self, using=None, keep_parents=False, *, hard_delete=False, _visited=None, _cascade=False):
        if _visited is None:
            _visited = set()

        with transaction.atomic():
            if hard_delete:
                self._cascade_on_hard_delete(_visited=_visited)
                return super().delete(using=using, keep_parents=keep_parents)

            key = (self._meta.label, self.pk)
            if key in _visited:
                return
            _visited.add(key)

            self.deleted_at = timezone.now()
            self.deleted_by_cascade = _cascade
            self.save(update_fields=["deleted_at", "deleted_by_cascade"])
            self._cascade_on_soft_delete(_visited=_visited)

    def restore(self, *, _visited=None):
        if not self.is_deleted:
            return

        if _visited is None:
            _visited = set()
        key = (self._meta.label, self.pk)
        if key in _visited:
            return
        _visited.add(key)

        with transaction.atomic():
            self.deleted_at = None
            self.deleted_by_cascade = False
            self.save(update_fields=["deleted_at", "deleted_by_cascade"])
            self._cascade_on_restore(_visited=_visited)

    # -- cascade helpers --

    def _get_related_objects_with_policy(self):
        """역참조 관계를 순회하여 (related_model, fk_field, fk_name, policy) 튜플을 yield."""
        for rel in self._meta.related_objects:
            related_model = rel.related_model
            fk_field_name = rel.field.name

            if not hasattr(related_model, "soft_delete_cascade"):
                continue

            policy = related_model.soft_delete_cascade.get(fk_field_name)
            if policy is None:
                continue

            if policy not in ALL_POLICIES:
                raise ValueError(
                    f"{related_model.__name__}.soft_delete_cascade['{fk_field_name}'] = "
                    f"'{policy}' is not a valid policy. Use one of: {ALL_POLICIES}"
                )

            yield related_model, rel.field, fk_field_name, policy

    def _cascade_on_soft_delete(self, *, _visited):
        """부모 soft delete 시 자식에 대한 cascade 처리."""
        for related_model, _fk_field, fk_name, policy in self._get_related_objects_with_policy():
            children_qs = related_model.all_objects.filter(**{fk_name: self})

            if policy == SOFT_CASCADE:
                for child in list(children_qs.alive()):
                    child.delete(_visited=_visited, _cascade=True)

            elif policy == SOFT_CASCADE_HARD_CHILDREN:
                # 경고: alive 자식만 물리 삭제됨 — 부모 복원 시 자식 복원 불가
                children_qs.alive().hard_delete()

            # HARD_CASCADE_SOFT_CHILDREN: 부모 soft delete 시에는 아무것도 하지 않음
            # (부모 hard delete 시에만 동작)

    def _cascade_on_hard_delete(self, *, _visited):
        """부모 hard delete 시 HARD_CASCADE_SOFT_CHILDREN 정책의 자식 처리."""
        key = (self._meta.label, self.pk)
        if key in _visited:
            return
        _visited.add(key)

        for related_model, fk_field, fk_name, policy in self._get_related_objects_with_policy():
            if policy != HARD_CASCADE_SOFT_CHILDREN:
                continue

            if not fk_field.null:
                raise ValueError(
                    f"HARD_CASCADE_SOFT_CHILDREN requires a nullable FK, "
                    f"but {related_model.__name__}.{fk_name} is non-nullable. "
                    f"Use SOFT_CASCADE instead."
                )

            children_qs = related_model.all_objects.filter(**{fk_name: self})
            # 자식을 soft delete로 마킹하고 FK를 NULL로 설정
            for child in list(children_qs.alive()):
                child.deleted_at = timezone.now()
                setattr(child, fk_name, None)
                child.save(update_fields=["deleted_at", fk_name])

    def _cascade_on_restore(self, *, _visited):
        """부모 restore 시 SOFT_CASCADE 정책의 자식 복원."""
        for related_model, _fk_field, fk_name, policy in self._get_related_objects_with_policy():
            if policy != SOFT_CASCADE:
                continue

            children_qs = related_model.all_objects.filter(**{fk_name: self}, deleted_by_cascade=True)
            for child in children_qs.dead():
                child.restore(_visited=_visited)
