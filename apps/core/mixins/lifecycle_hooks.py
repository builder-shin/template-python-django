"""Lifecycle hook stubs for ApiViewSet CRUD operations."""

from django.db import models


class LifecycleHookMixin:
    """Provides lifecycle hook stubs called during CRUD and upsert operations.

    Hook 호출 순서:
      create: create_after_init(할당 시점) -> save -> create_after_save
      update: update_after_init -> 속성 할당 -> update_after_assign -> save -> update_after_save
      destroy: destroy_after_init -> delete -> destroy_after_save

    create/update hooks는 HookableSerializerMixin이 호출.
    destroy/show/new hooks는 ApiViewSet이 직접 호출.
    upsert hooks는 UpsertMixin에 정의되어 있음.
    """

    def create_after_init(self, instance: models.Model) -> None:
        pass

    def create_after_save(self, instance: models.Model, success: bool) -> None:
        pass

    def update_after_init(self, instance: models.Model) -> None:
        pass

    def update_after_assign(self, instance: models.Model) -> None:
        pass

    def update_after_save(self, instance: models.Model, success: bool) -> None:
        pass

    def destroy_after_init(self, instance: models.Model) -> None:
        pass

    def destroy_after_save(self, instance: models.Model, success: bool) -> None:
        pass

    def show_after_init(self, instance: models.Model) -> None:
        pass

    def new_after_init(self, instance: models.Model) -> None:
        pass
