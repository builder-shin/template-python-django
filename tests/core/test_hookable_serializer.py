from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.core.mixins.crud_actions import HookableSerializerMixin


class _FakeModel:
    """테스트용 최소 모델."""

    _meta = MagicMock()

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def save(self):
        pass


class _FakeSerializer(HookableSerializerMixin):
    """테스트용 Serializer."""

    class Meta:
        model = _FakeModel

    def __init__(self, context=None):
        self.context = context or {}


@pytest.fixture
def view_with_hooks():
    """lifecycle hook이 있는 mock view."""
    view = MagicMock()
    view.create_after_init = MagicMock()
    view.create_after_save = MagicMock()
    view.update_after_assign = MagicMock()
    view.update_after_save = MagicMock()
    return view


class TestHookableSerializerCreate:
    def test_create_calls_lifecycle_hooks(self, view_with_hooks):
        """create 성공 시 after_init + after_save(True) 호출."""
        _FakeModel._meta.many_to_many = []
        serializer = _FakeSerializer(context={"view": view_with_hooks})

        instance = serializer.create({"name": "test"})

        view_with_hooks.create_after_init.assert_called_once_with(instance)
        view_with_hooks.create_after_save.assert_called_once_with(instance, True)

    def test_create_django_validation_error_calls_hook_with_false(self, view_with_hooks):
        """create 시 DjangoValidationError 발생 → after_save(False) 호출."""
        _FakeModel._meta.many_to_many = []
        _FakeModel.save = MagicMock(side_effect=DjangoValidationError({"name": ["필수 필드입니다."]}))
        serializer = _FakeSerializer(context={"view": view_with_hooks})

        with pytest.raises(DRFValidationError):
            serializer.create({"name": ""})

        view_with_hooks.create_after_save.assert_called_once()
        assert view_with_hooks.create_after_save.call_args[0][1] is False

        # 복원
        _FakeModel.save = lambda self: None

    def test_create_generic_exception_calls_hook_with_false(self, view_with_hooks):
        """create 시 일반 예외 → after_save(False) 호출."""
        _FakeModel._meta.many_to_many = []
        _FakeModel.save = MagicMock(side_effect=RuntimeError("DB error"))
        serializer = _FakeSerializer(context={"view": view_with_hooks})

        with pytest.raises(RuntimeError, match="DB error"):
            serializer.create({"name": "test"})

        view_with_hooks.create_after_save.assert_called_once()
        assert view_with_hooks.create_after_save.call_args[0][1] is False

        _FakeModel.save = lambda self: None


class TestHookableSerializerUpdate:
    def test_update_calls_lifecycle_hooks(self, view_with_hooks):
        """update 성공 시 after_assign + after_save(True) 호출."""
        _FakeModel._meta.many_to_many = []
        serializer = _FakeSerializer(context={"view": view_with_hooks})
        instance = _FakeModel(name="old")

        result = serializer.update(instance, {"name": "new"})

        assert result.name == "new"
        view_with_hooks.update_after_assign.assert_called_once_with(instance)
        view_with_hooks.update_after_save.assert_called_once_with(instance, True)

    def test_update_django_validation_error_calls_hook_with_false(self, view_with_hooks):
        """update 시 DjangoValidationError → after_save(False) 호출."""
        _FakeModel._meta.many_to_many = []
        _FakeModel.save = MagicMock(side_effect=DjangoValidationError({"name": ["이미 존재합니다."]}))
        serializer = _FakeSerializer(context={"view": view_with_hooks})
        instance = _FakeModel(name="old")

        with pytest.raises(DRFValidationError):
            serializer.update(instance, {"name": "dup"})

        view_with_hooks.update_after_save.assert_called_once()
        assert view_with_hooks.update_after_save.call_args[0][1] is False

        _FakeModel.save = lambda self: None

    def test_update_generic_exception_calls_hook_with_false(self, view_with_hooks):
        """update 시 일반 예외 → after_save(False) 호출."""
        _FakeModel._meta.many_to_many = []
        _FakeModel.save = MagicMock(side_effect=RuntimeError("DB error"))
        serializer = _FakeSerializer(context={"view": view_with_hooks})
        instance = _FakeModel(name="old")

        with pytest.raises(RuntimeError, match="DB error"):
            serializer.update(instance, {"name": "new"})

        view_with_hooks.update_after_save.assert_called_once()
        assert view_with_hooks.update_after_save.call_args[0][1] is False

        _FakeModel.save = lambda self: None
