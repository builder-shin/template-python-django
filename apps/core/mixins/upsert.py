"""Upsert action mixin for find-or-create + update."""

import json as _json
import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.exceptions import JsonApiError

logger = logging.getLogger(__name__)


class UpsertMixin:
    """Provides the upsert action: find-or-create + update via raw attribute assignment.

    NOTE: This bypasses HookableSerializerMixin's create/update hooks
    because it uses setattr() instead of serializer.save(). If you need
    create_after_init/update_after_init hooks to fire during upsert,
    use upsert_after_init/upsert_after_assign/upsert_after_save hooks instead.
    """

    def upsert_find_params(self) -> dict | None:
        return None

    def upsert_after_init(self, instance) -> None:
        pass

    def upsert_after_assign(self, instance) -> None:
        pass

    def upsert_after_save(self, instance, success: bool, created: bool) -> None:
        pass

    def _parse_raw_body(self):
        """Parse JSONAPI raw body once and cache.

        Raises JsonApiError(400) if the body is not valid JSON.
        """
        if not hasattr(self, "_cached_raw_body"):
            try:
                self._cached_raw_body = _json.loads(self.request._request.body)
            except (ValueError, UnicodeDecodeError) as exc:
                raise JsonApiError(
                    "BadRequest",
                    "Request body is not valid JSON.",
                    400,
                ) from exc
        return self._cached_raw_body

    @action(detail=False, methods=["put"], url_path="upsert")
    def upsert(self, request, *args, **kwargs):
        find_params = self.upsert_find_params()
        if not find_params:
            raise JsonApiError("BadRequest", "upsert_find_params를 뷰셋에서 정의해야 합니다.", 400)

        model_class = self.get_serializer().Meta.model
        with transaction.atomic():
            try:
                instance = model_class.objects.select_for_update().get(**find_params)
                created = False
            except model_class.DoesNotExist:
                instance = model_class(**find_params)
                created = True

            self.upsert_after_init(instance)

            # Parse raw body to extract attributes, bypassing JSONAPI parser's id requirement
            raw_body = self._parse_raw_body()
            flat_data = raw_body.get("data", {}).get("attributes", {})

            serializer = self.get_serializer(instance, data=flat_data, partial=True)
            serializer.is_valid(raise_exception=True)

            for attr, value in serializer.validated_data.items():
                setattr(instance, attr, value)

            self.upsert_after_assign(instance)

            m2m_field_names = {f.name for f in instance.__class__._meta.many_to_many}
            try:
                instance.full_clean()
                instance.save()
                for attr, value in serializer.validated_data.items():
                    if attr in m2m_field_names:
                        getattr(instance, attr).set(value)
                success = True
            except ValidationError as e:
                self.upsert_after_save(instance, False, created)
                raise JsonApiError(
                    "ValidationFailed",
                    "; ".join(
                        f"{field}: {', '.join(messages)}" if field != "__all__" else ", ".join(messages)
                        for field, messages in e.message_dict.items()
                    ),
                    422,
                ) from e
            except Exception as err:
                logger.exception("Unexpected error in upsert save for %s(pk=%s)", type(instance).__name__, instance.pk)
                self.upsert_after_save(instance, False, created)
                raise JsonApiError("SaveFailed", "리소스 저장에 실패했습니다.", 422) from err

        self.upsert_after_save(instance, success, created)

        output_serializer = self.get_serializer(instance)
        http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(output_serializer.data, status=http_status)
