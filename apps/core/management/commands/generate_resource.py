"""
generate_resource — Django 리소스 스캐폴드 생성기

사용법:
    python manage.py generate_resource products \
        --fields "name:CharField content:TextField price:IntegerField status:IntegerChoices" \
        --user-scoped

복수형 snake_case 리소스 이름을 받아 모델, 뷰, 시리얼라이저, 필터, URL, 테스트 파일을 자동 생성합니다.
"""

import os
import re
import textwrap

from django.core.management.base import BaseCommand, CommandError

try:
    import inflect

    _inflect_engine = inflect.engine()
except ImportError:
    _inflect_engine = None


# ---------------------------------------------------------------------------
# 이름 변환 유틸리티
# ---------------------------------------------------------------------------


def _to_pascal(snake: str) -> str:
    """snake_case -> PascalCase"""
    return "".join(word.capitalize() for word in snake.split("_"))


def _singularize(plural: str) -> str:
    """복수형 -> 단수형 (inflect 사용, 실패 시 원본 반환)"""
    if _inflect_engine is None:
        # inflect 미설치 시 단순 규칙
        if plural.endswith("ies"):
            return plural[:-3] + "y"
        if plural.endswith(("ses", "xes", "zes")):
            return plural[:-2]
        if plural.endswith("s") and not plural.endswith("ss"):
            return plural[:-1]
        return plural
    result = _inflect_engine.singular_noun(plural)
    if result is False:
        # 이미 단수형인 경우
        return plural
    return result


# ---------------------------------------------------------------------------
# 필드 타입 매핑
# ---------------------------------------------------------------------------

FIELD_TYPE_MAP = {
    "CharField": ("models.CharField", "max_length=255"),
    "TextField": ("models.TextField", 'blank=True, default=""'),
    "IntegerField": ("models.IntegerField", "default=0"),
    "BooleanField": ("models.BooleanField", "default=False"),
    "DateTimeField": ("models.DateTimeField", "null=True, blank=True"),
    "DateField": ("models.DateField", "null=True, blank=True"),
    "DecimalField": ("models.DecimalField", "max_digits=10, decimal_places=2, default=0"),
    "FloatField": ("models.FloatField", "default=0.0"),
    "IntegerChoices": ("models.IntegerField", "choices=Status.choices, default=0"),
}

# 테스트에서 objects.create() 시 사용할 기본 값
FIELD_TEST_DEFAULTS = {
    "CharField": '"test-value"',
    "TextField": '"test content"',
    "IntegerField": "1",
    "BooleanField": "True",
    "DateTimeField": "None",
    "DateField": "None",
    "DecimalField": '"9.99"',
    "FloatField": "1.0",
    "IntegerChoices": "0",
}


# ---------------------------------------------------------------------------
# 템플릿 생성 함수들
# ---------------------------------------------------------------------------


def _gen_apps_py(resource_name: str, plural_pascal: str) -> str:
    return textwrap.dedent(f"""\
        from django.apps import AppConfig


        class {plural_pascal}Config(AppConfig):
            default_auto_field = "django.db.models.BigAutoField"
            name = "apps.{resource_name}"
    """)


def _gen_models_py(
    resource_name: str,
    singular_pascal: str,
    fields: list[tuple[str, str]],
    user_scoped: bool,
) -> str:
    has_choices = any(ft == "IntegerChoices" for _, ft in fields)

    lines = [
        "from django.db import models",
        "",
        "",
    ]

    # QuerySet 클래스
    lines.append(f"class {singular_pascal}QuerySet(models.QuerySet):")
    lines.append("    def recent(self):")
    lines.append('        return self.order_by("-created_at")')
    lines.append("")
    if user_scoped:
        lines.append("    def by_user(self, user_id):")
        lines.append("        return self.filter(user_id=user_id)")
        lines.append("")
    lines.append("")

    # 모델 클래스
    lines.append(f"class {singular_pascal}(models.Model):")

    # IntegerChoices 내부 클래스
    if has_choices:
        lines.append("    class Status(models.IntegerChoices):")
        lines.append('        ACTIVE = 0, "active"')
        lines.append('        INACTIVE = 1, "inactive"')
        lines.append("")

    # 필드 정의
    for fname, ftype in fields:
        if ftype not in FIELD_TYPE_MAP:
            raise CommandError(f"지원하지 않는 필드 타입입니다: {ftype}\n지원 타입: {', '.join(FIELD_TYPE_MAP.keys())}")
        django_field, opts = FIELD_TYPE_MAP[ftype]
        lines.append(f"    {fname} = {django_field}({opts})")

    # user_id 필드
    if user_scoped:
        lines.append("    user_id = models.CharField(max_length=255, db_index=True)")

    # 타임스탬프 필드
    lines.append("    created_at = models.DateTimeField(auto_now_add=True)")
    lines.append("    updated_at = models.DateTimeField(auto_now=True)")
    lines.append("")

    # objects 매니저
    lines.append(f"    objects = {singular_pascal}QuerySet.as_manager()")
    lines.append("")

    # Meta
    lines.append("    class Meta:")
    lines.append('        ordering = ["-created_at"]')
    lines.append("")

    # __str__
    first_char_field = next((fn for fn, ft in fields if ft == "CharField"), None)
    str_field = first_char_field or "pk"
    lines.append("    def __str__(self):")
    if str_field == "pk":
        lines.append(f'        return f"{singular_pascal}#{{self.pk}}"')
    else:
        lines.append(f"        return self.{str_field}")
    lines.append("")

    # save with full_clean
    lines.append("    def save(self, *args, **kwargs):")
    lines.append('        if not kwargs.get("update_fields"):')
    lines.append("            self.full_clean()")
    lines.append("        super().save(*args, **kwargs)")

    return "\n".join(lines) + "\n"


def _gen_views_py(
    resource_name: str,
    singular_pascal: str,
    plural_pascal: str,
    singular_snake: str,
    user_scoped: bool,
) -> str:
    lines = []

    # Imports
    lines.append("from apps.core.views import ApiViewSet")
    if user_scoped:
        lines.append("from apps.core.exceptions import JsonApiError")
    lines.append("")
    lines.append(f"from .models import {singular_pascal}")
    lines.append(f"from .serializers import {singular_pascal}Serializer")
    lines.append(f"from .filters import {singular_pascal}FilterSet")
    lines.append("")
    lines.append("")

    # ViewSet 클래스
    lines.append(f"class {plural_pascal}ViewSet(ApiViewSet):")
    lines.append(f"    serializer_class = {singular_pascal}Serializer")
    lines.append(f"    filterset_class = {singular_pascal}FilterSet")
    if user_scoped:
        lines.append('    resource_label = "리소스"')
    lines.append("")

    # allowed_includes
    lines.append("    @property")
    lines.append("    def allowed_includes(self):")
    lines.append("        # TODO: 관계 필드는 수동으로 추가하세요 (참고: apps/comments/)")
    lines.append("        return []")
    lines.append("")

    # get_queryset
    lines.append("    def get_queryset(self):")
    lines.append(f"        return {singular_pascal}.objects.all()")
    lines.append("")

    # get_index_scope
    if user_scoped:
        lines.append("    def get_index_scope(self):")
        lines.append("        user = self.request.user")
        lines.append('        if user and hasattr(user, "id") and user.id:')
        lines.append(f"            return {singular_pascal}.objects.by_user(user.id)")
        lines.append(f"        return {singular_pascal}.objects.none()")
        lines.append("")
        lines.append("    def _check_ownership(self, instance, action_label: str) -> None:")
        lines.append("        if str(instance.user_id) != str(self.request.user.id):")
        lines.append(f'            raise JsonApiError("Forbidden", f"본인의 {{self.resource_label}}만 {{action_label}}할 수 없습니다.", 403)')
        lines.append("")
        lines.append("    def create_after_init(self, instance) -> None:")
        lines.append('        instance.user_id = str(self.request.user.id)')
        lines.append("")
        lines.append("    def update_after_init(self, instance) -> None:")
        lines.append('        self._check_ownership(instance, "수정")')
        lines.append("")
        lines.append("    def destroy_after_init(self, instance) -> None:")
        lines.append('        self._check_ownership(instance, "삭제")')
    else:
        lines.append("    def get_index_scope(self):")
        lines.append(f"        return {singular_pascal}.objects.all()")

    return "\n".join(lines) + "\n"


def _gen_serializers_py(
    resource_name: str,
    singular_pascal: str,
    fields: list[tuple[str, str]],
    user_scoped: bool,
) -> str:
    lines = []

    lines.append("from rest_framework_json_api import serializers")
    lines.append("from apps.core.mixins.crud_actions import HookableSerializerMixin")
    lines.append(f"from .models import {singular_pascal}")
    lines.append("")
    lines.append("")

    # Serializer 클래스
    lines.append(f"class {singular_pascal}Serializer(HookableSerializerMixin, serializers.ModelSerializer):")

    # TODO 주석 (관계 필드)
    lines.append("    # TODO: 관계 필드는 수동으로 추가하세요 (참고: apps/comments/)")
    lines.append("    # included_serializers = {}")
    lines.append("    # related_field = ResourceRelatedField(queryset=RelatedModel.objects.all())")
    lines.append("")

    # Meta 클래스
    lines.append("    class Meta:")
    lines.append(f"        model = {singular_pascal}")

    # fields 목록 구성
    field_names = [fn for fn, _ in fields]
    all_fields = list(field_names)
    if user_scoped:
        all_fields.append("user_id")
    all_fields.extend(["created_at", "updated_at"])

    fields_str = "[\n"
    for fn in all_fields:
        fields_str += f'            "{fn}",\n'
    fields_str += "        ]"
    lines.append(f"        fields = {fields_str}")

    # read_only_fields
    ro_fields = ["created_at", "updated_at"]
    if user_scoped:
        ro_fields.insert(0, "user_id")
    ro_str = "[" + ", ".join(f'"{f}"' for f in ro_fields) + "]"
    lines.append(f"        read_only_fields = {ro_str}")
    lines.append(f'        resource_name = "{resource_name}"')

    return "\n".join(lines) + "\n"


def _gen_filters_py(
    singular_pascal: str,
    fields: list[tuple[str, str]],
    user_scoped: bool,
) -> str:
    lines = []
    lines.append("import django_filters")
    lines.append("")
    lines.append(f"from .models import {singular_pascal}")
    lines.append("")
    lines.append("")
    lines.append(f"class {singular_pascal}FilterSet(django_filters.FilterSet):")
    lines.append("    class Meta:")
    lines.append(f"        model = {singular_pascal}")
    lines.append("        fields = {")

    # Map field types to appropriate lookups
    FIELD_LOOKUPS = {  # noqa: N806
        "CharField": '["exact", "icontains", "istartswith", "iendswith"]',
        "TextField": '["exact", "icontains"]',
        "IntegerField": '["exact", "in", "gt", "gte", "lt", "lte"]',
        "BooleanField": '["exact"]',
        "DateTimeField": '["exact", "gt", "gte", "lt", "lte"]',
        "DateField": '["exact", "gt", "gte", "lt", "lte"]',
        "DecimalField": '["exact", "gt", "gte", "lt", "lte"]',
        "FloatField": '["exact", "gt", "gte", "lt", "lte"]',
        "IntegerChoices": '["exact", "in"]',
    }

    for fname, ftype in fields:
        lookups = FIELD_LOOKUPS.get(ftype, '["exact"]')
        lines.append(f'            "{fname}": {lookups},')

    # Add timestamp fields
    lines.append('            "created_at": ["exact", "gt", "gte", "lt", "lte"],')
    lines.append('            "updated_at": ["exact", "gt", "gte", "lt", "lte"],')

    if user_scoped:
        lines.append('            "user_id": ["exact", "in"],')

    lines.append("        }")

    return "\n".join(lines) + "\n"


def _gen_urls_py(
    resource_name: str,
    singular_snake: str,
    plural_pascal: str,
) -> str:
    return textwrap.dedent(f"""\
        from django.urls import path, include
        from rest_framework.routers import DefaultRouter
        from .views import {plural_pascal}ViewSet

        router = DefaultRouter(trailing_slash=False)
        router.register(r"{resource_name}", {plural_pascal}ViewSet, basename="{singular_snake}")

        urlpatterns = [
            path("", include(router.urls)),
        ]
    """)


def _gen_test_models_py(
    resource_name: str,
    singular_pascal: str,
    singular_snake: str,
    fields: list[tuple[str, str]],
    user_scoped: bool,
) -> str:
    lines = []
    lines.append("import pytest")
    lines.append("")
    lines.append(f"from apps.{resource_name}.models import {singular_pascal}")
    lines.append("")
    lines.append("")
    lines.append("@pytest.mark.django_db")
    lines.append(f"class Test{singular_pascal}Model:")

    # test_create
    lines.append(f"    def test_create_{singular_snake}(self):")

    # create kwargs 구성
    create_kwargs = []
    for fn, ft in fields:
        if ft in FIELD_TEST_DEFAULTS:
            create_kwargs.append(f"{fn}={FIELD_TEST_DEFAULTS[ft]}")
    if user_scoped:
        create_kwargs.append('user_id="user-1"')

    kwargs_str = ", ".join(create_kwargs)
    lines.append(f"        instance = {singular_pascal}.objects.create({kwargs_str})")
    lines.append("        assert instance.pk is not None")

    # 첫 번째 CharField 값 검증
    first_char = next((fn for fn, ft in fields if ft == "CharField"), None)
    if first_char:
        lines.append(f'        assert instance.{first_char} == "test-value"')
    lines.append("")

    # test_str
    lines.append("    def test_str(self):")
    lines.append(f"        instance = {singular_pascal}.objects.create({kwargs_str})")
    lines.append("        assert str(instance)")

    return "\n".join(lines) + "\n"


def _gen_test_api_py(  # noqa: C901
    resource_name: str,
    singular_pascal: str,
    fields: list[tuple[str, str]],
    user_scoped: bool,
) -> str:
    lines = []
    lines.append("import pytest")
    lines.append("from rest_framework.test import APIClient")
    lines.append("")
    lines.append(f"from apps.{resource_name}.models import {singular_pascal}")
    lines.append("from tests.conftest import jsonapi_payload")
    lines.append("")
    lines.append("")
    lines.append("@pytest.mark.django_db")
    lines.append(f"class Test{singular_pascal}API:")

    # -- test_index_with_auth
    lines.append("    def test_index_with_auth(self, mock_authenticated, jsonapi_headers):")

    # create kwargs for test data
    create_kwargs_parts = []
    for fn, ft in fields:
        if ft in FIELD_TEST_DEFAULTS:
            create_kwargs_parts.append(f"{fn}={FIELD_TEST_DEFAULTS[ft]}")
    if user_scoped:
        create_kwargs_parts.append("user_id=str(mock_authenticated.id)")
    create_kwargs_str = ", ".join(create_kwargs_parts)

    lines.append(f"        {singular_pascal}.objects.create({create_kwargs_str})")
    lines.append("")
    lines.append("        client = APIClient()")
    lines.append("        client.force_authenticate(user=mock_authenticated)")
    lines.append(f'        response = client.get("/api/v1/{resource_name}", **jsonapi_headers)')
    lines.append("        assert response.status_code == 200")
    lines.append("        data = response.json()")
    lines.append('        assert "data" in data')
    if user_scoped:
        lines.append('        assert len(data["data"]) == 1')
    lines.append("")

    # -- test_create_valid
    lines.append("    def test_create_valid(self, mock_authenticated, jsonapi_headers):")

    # payload attributes
    payload_attrs = {}
    for fn, ft in fields:
        if ft == "CharField":
            payload_attrs[fn] = '"New Value"'
        elif ft == "TextField":
            payload_attrs[fn] = '"New content"'
        elif ft == "IntegerField" or ft == "IntegerChoices":
            payload_attrs[fn] = "0"
        elif ft == "BooleanField":
            payload_attrs[fn] = "False"
        elif ft == "DecimalField":
            payload_attrs[fn] = '"1.00"'
        elif ft == "FloatField":
            payload_attrs[fn] = "1.0"
        # DateTimeField / DateField are nullable, skip in create payload

    attrs_inner = ", ".join(f'"{k}": {v}' for k, v in payload_attrs.items())

    lines.append("        client = APIClient()")
    lines.append("        client.force_authenticate(user=mock_authenticated)")
    lines.append(f'        payload = jsonapi_payload({{{attrs_inner}}}, "{resource_name}")')
    lines.append("        response = client.post(")
    lines.append(f'            "/api/v1/{resource_name}",')
    lines.append("            data=payload,")
    lines.append('            format="vnd.api+json",')
    lines.append("            **jsonapi_headers,")
    lines.append("        )")
    lines.append("        assert response.status_code == 201")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 자동 등록 헬퍼
# ---------------------------------------------------------------------------


def _auto_register_settings(base_dir: str, resource_name: str, plural_pascal: str) -> bool:
    """config/settings/base.py 에 앱 등록"""
    settings_path = os.path.join(base_dir, "config", "settings", "base.py")
    if not os.path.isfile(settings_path):
        return False

    with open(settings_path, encoding="utf-8") as f:
        content = f.read()

    marker = "# Local apps"
    if marker not in content:
        return False

    new_line = f'    "apps.{resource_name}.apps.{plural_pascal}Config",'

    # 이미 등록되어 있으면 스킵
    if new_line in content:
        return True

    # marker 이후의 마지막 "apps. 로 시작하는 줄 찾기
    lines = content.split("\n")
    marker_idx = None
    last_app_idx = None
    for i, line in enumerate(lines):
        if marker in line:
            marker_idx = i
        if marker_idx is not None and line.strip().startswith('"apps.'):
            last_app_idx = i

    if last_app_idx is None:
        return False

    lines.insert(last_app_idx + 1, new_line)

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return True


def _auto_register_urls(base_dir: str, resource_name: str) -> bool:
    """config/urls.py 에 URL 등록"""
    urls_path = os.path.join(base_dir, "config", "urls.py")
    if not os.path.isfile(urls_path):
        return False

    with open(urls_path, encoding="utf-8") as f:
        content = f.read()

    marker = "# API v1 endpoints"
    if marker not in content:
        return False

    new_line = f'    path("api/v1/", include("apps.{resource_name}.urls")),'

    # 이미 등록되어 있으면 스킵
    if new_line in content:
        return True

    # marker 이후의 마지막 path("api/v1/ 줄 찾기
    lines = content.split("\n")
    marker_idx = None
    last_path_idx = None
    for i, line in enumerate(lines):
        if marker in line:
            marker_idx = i
        if marker_idx is not None and line.strip().startswith('path("api/v1/'):
            last_path_idx = i

    if last_path_idx is None:
        return False

    lines.insert(last_path_idx + 1, new_line)

    with open(urls_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return True


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


class Command(BaseCommand):
    help = "새 API 리소스(모델, 뷰, 시리얼라이저, 필터, URL, 테스트)를 자동 생성합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "resource_name",
            type=str,
            help="리소스 이름 (복수형 snake_case, 예: products, order_items)",
        )
        parser.add_argument(
            "--fields",
            type=str,
            default="",
            help='필드 정의 (공백 구분, "name:CharField content:TextField")',
        )
        parser.add_argument(
            "--user-scoped",
            action="store_true",
            default=False,
            help="user_id 필드 및 소유권 훅 자동 추가",
        )
        parser.add_argument(
            "--no-tests",
            action="store_true",
            default=False,
            help="테스트 파일 생성 건너뛰기",
        )
        parser.add_argument(
            "--model-name",
            type=str,
            default="",
            help="모델 이름 직접 지정 (inflect 단수화 결과를 오버라이드)",
        )

    def handle(self, *args, **options):  # noqa: C901
        resource_name = options["resource_name"].strip()
        user_scoped = options["user_scoped"]
        no_tests = options["no_tests"]
        model_name_override = options["model_name"].strip()

        # 유효성 검사: snake_case 복수형
        if not re.match(r"^[a-z][a-z0-9_]*$", resource_name):
            raise CommandError(f"리소스 이름은 snake_case여야 합니다: {resource_name}\n예: products, order_items")

        # 필드 파싱
        fields: list[tuple[str, str]] = []
        raw_fields = options["fields"].strip()
        if raw_fields:
            for pair in raw_fields.split():
                if ":" not in pair:
                    raise CommandError(f"잘못된 필드 형식입니다: {pair}\n올바른 형식: name:CharField")
                fname, ftype = pair.split(":", 1)
                if ftype not in FIELD_TYPE_MAP:
                    raise CommandError(
                        f"지원하지 않는 필드 타입입니다: {ftype}\n지원 타입: {', '.join(FIELD_TYPE_MAP.keys())}"
                    )
                fields.append((fname, ftype))

        # 이름 변환
        if model_name_override:
            singular_snake = model_name_override.lower()
            singular_pascal = (
                _to_pascal(model_name_override)
                if "_" in model_name_override
                else model_name_override[0].upper() + model_name_override[1:]
            )
        else:
            singular_snake = _singularize(resource_name)
            singular_pascal = _to_pascal(singular_snake)

        plural_pascal = _to_pascal(resource_name)

        # 프로젝트 루트 디렉토리 결정 (manage.py 기준)
        base_dir = os.getcwd()
        apps_dir = os.path.join(base_dir, "apps", resource_name)
        tests_dir = os.path.join(base_dir, "tests", resource_name)

        # 이미 존재하는지 확인
        if os.path.isdir(apps_dir):
            raise CommandError(f"앱 디렉토리가 이미 존재합니다: {apps_dir}\n기존 앱을 삭제한 후 다시 시도하세요.")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"=== 리소스 생성 시작: {resource_name} ==="))
        self.stdout.write(f"  모델: {singular_pascal}")
        self.stdout.write(f"  뷰셋: {plural_pascal}ViewSet")
        self.stdout.write(f"  시리얼라이저: {singular_pascal}Serializer")
        self.stdout.write(f"  필터: {singular_pascal}FilterSet")
        self.stdout.write(f"  User-scoped: {user_scoped}")
        self.stdout.write(f"  필드: {fields if fields else '(없음)'}")
        self.stdout.write("")

        # 디렉토리 생성
        os.makedirs(apps_dir, exist_ok=True)
        os.makedirs(os.path.join(apps_dir, "migrations"), exist_ok=True)
        self._write_file(os.path.join(apps_dir, "migrations", "__init__.py"), "")

        # 1. __init__.py
        self._write_file(os.path.join(apps_dir, "__init__.py"), "")

        # 2. apps.py
        self._write_file(
            os.path.join(apps_dir, "apps.py"),
            _gen_apps_py(resource_name, plural_pascal),
        )

        # 3. models.py
        self._write_file(
            os.path.join(apps_dir, "models.py"),
            _gen_models_py(resource_name, singular_pascal, fields, user_scoped),
        )

        # 4. views.py
        self._write_file(
            os.path.join(apps_dir, "views.py"),
            _gen_views_py(resource_name, singular_pascal, plural_pascal, singular_snake, user_scoped),
        )

        # 5. serializers.py
        self._write_file(
            os.path.join(apps_dir, "serializers.py"),
            _gen_serializers_py(resource_name, singular_pascal, fields, user_scoped),
        )

        # 6. filters.py
        self._write_file(
            os.path.join(apps_dir, "filters.py"),
            _gen_filters_py(singular_pascal, fields, user_scoped),
        )

        # 7. urls.py
        self._write_file(
            os.path.join(apps_dir, "urls.py"),
            _gen_urls_py(resource_name, singular_snake, plural_pascal),
        )

        # 테스트 파일
        if not no_tests:
            os.makedirs(tests_dir, exist_ok=True)

            # 8. tests/__init__.py
            self._write_file(os.path.join(tests_dir, "__init__.py"), "")

            # 9. test_models.py
            self._write_file(
                os.path.join(tests_dir, "test_models.py"),
                _gen_test_models_py(resource_name, singular_pascal, singular_snake, fields, user_scoped),
            )

            # 10. test_api.py
            self._write_file(
                os.path.join(tests_dir, "test_api.py"),
                _gen_test_api_py(resource_name, singular_pascal, fields, user_scoped),
            )

        # 자동 등록
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("--- 자동 등록 ---"))

        if _auto_register_settings(base_dir, resource_name, plural_pascal):
            self.stdout.write(
                self.style.SUCCESS(
                    f"  config/settings/base.py: apps.{resource_name}.apps.{plural_pascal}Config 등록 완료"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"  config/settings/base.py: '# Local apps' 주석을 찾을 수 없습니다.\n"
                    f'  수동으로 추가하세요: "apps.{resource_name}.apps.{plural_pascal}Config"'
                )
            )

        if _auto_register_urls(base_dir, resource_name):
            self.stdout.write(self.style.SUCCESS(f"  config/urls.py: apps.{resource_name}.urls 등록 완료"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"  config/urls.py: '# API v1 endpoints' 주석을 찾을 수 없습니다.\n"
                    f'  수동으로 추가하세요: path("api/v1/", include("apps.{resource_name}.urls")),'
                )
            )

        # 완료 메시지
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"=== {resource_name} 리소스 생성 완료 ==="))
        self.stdout.write("")
        self.stdout.write("다음 단계:")
        self.stdout.write(f"  1. python manage.py makemigrations {resource_name}")
        self.stdout.write("  2. python manage.py migrate")
        self.stdout.write("  3. 관계 필드가 필요하면 수동으로 추가하세요 (참고: apps/comments/)")
        self.stdout.write("")

    def _write_file(self, path: str, content: str):
        """파일을 생성하고 결과를 출력합니다."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        # 프로젝트 루트 기준 상대 경로 출력
        rel = os.path.relpath(path, os.getcwd())
        self.stdout.write(f"  생성: {rel}")
