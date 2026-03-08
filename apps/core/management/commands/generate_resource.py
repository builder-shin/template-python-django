"""
generate_resource — Django 리소스 스캐폴드 생성기

사용법:
    python manage.py generate_resource products \
        --fields "name:CharField content:TextField price:IntegerField status:IntegerChoices" \
        --user-scoped

복수형 snake_case 리소스 이름을 받아 모델, 뷰(필터 포함), 시리얼라이저, URL, 테스트 파일을 자동 생성합니다.
"""

import os
import re
import textwrap

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core.utils import singularize, to_pascal

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
    "IntegerChoices": ("models.IntegerField", "choices=Status.choices, default=Status.ACTIVE"),
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
    ]
    if user_scoped:
        lines.append("from django.conf import settings")
    lines += [
        "",
        "from apps.core.models import BaseModel, BaseQuerySet",
        "",
        "",
    ]

    # QuerySet 클래스
    lines.append(f"class {singular_pascal}QuerySet(BaseQuerySet):")
    lines.append("    pass")
    lines.append("")
    lines.append("")

    # 모델 클래스
    lines.append(f"class {singular_pascal}(BaseModel):")

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

    # user FK 필드
    if user_scoped:
        lines.append(
            "    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,"
            ' related_name="%(class)ss")'
        )

    # objects 매니저
    lines.append(f"    objects = {singular_pascal}QuerySet.as_manager()")
    lines.append("")

    # Meta
    lines.append("    class Meta(BaseModel.Meta):")
    lines.append("        pass")
    lines.append("")

    # __str__
    first_char_field = next((fn for fn, ft in fields if ft == "CharField"), None)
    str_field = first_char_field or "pk"
    lines.append("    def __str__(self):")
    if str_field == "pk":
        lines.append(f'        return f"{singular_pascal}#{{self.pk}}"')
    else:
        lines.append(f"        return self.{str_field}")

    return "\n".join(lines) + "\n"


def _gen_views_py(
    resource_name: str,
    singular_pascal: str,
    plural_pascal: str,
    singular_snake: str,
    fields: list[tuple[str, str]],
    user_scoped: bool,
) -> str:
    # Map field types to appropriate lookups
    FIELD_LOOKUPS = {  # noqa: N806
        "CharField": '["exact", "icontains", "istartswith", "iendswith"]',
        "TextField": '["exact", "icontains"]',
        "IntegerField": '["exact", "in", "gt", "gte", "lt", "lte"]',
        "BooleanField": '["exact"]',
        "DateTimeField": "TIMESTAMP_LOOKUPS",
        "DateField": "TIMESTAMP_LOOKUPS",
        "DecimalField": '["exact", "gt", "gte", "lt", "lte"]',
        "FloatField": '["exact", "gt", "gte", "lt", "lte"]',
        "IntegerChoices": '["exact", "in"]',
    }

    lines = []

    # Imports
    lines.append("from apps.core.filters import TIMESTAMP_LOOKUPS")
    lines.append("from apps.core.views import ApiViewSet")
    lines.append("")
    lines.append("")

    # ViewSet 클래스 (filterset_class는 allowed_filters dict에서 동적 생성)
    lines.append(f"class {plural_pascal}ViewSet(ApiViewSet):")
    lines.append("")

    # select_related_extra for user-scoped resources
    if user_scoped:
        lines.append('    select_related_extra = ["user"]')
        lines.append("")

    # allowed_includes
    lines.append("    @property")
    lines.append("    def allowed_includes(self):")
    lines.append("        # TODO: 관계 필드는 수동으로 추가하세요 (참고: apps/comments/)")
    lines.append("        return []")
    lines.append("")

    # allowed_filters
    lines.append("    @property")
    lines.append("    def allowed_filters(self):")
    lines.append("        return {")

    for fname, ftype in fields:
        lookups = FIELD_LOOKUPS.get(ftype, '["exact"]')
        lines.append(f'            "{fname}": {lookups},')

    lines.append('            "created_at": TIMESTAMP_LOOKUPS,')
    lines.append('            "updated_at": TIMESTAMP_LOOKUPS,')

    if user_scoped:
        lines.append('            "user": ["exact", "in"],')

    lines.append("        }")
    lines.append("")

    # get_index_scope
    if user_scoped:
        lines.append("    def get_index_scope(self):")
        lines.append("        qs = super().get_index_scope()")
        lines.append("        if self.request.user.is_authenticated:")
        lines.append("            return qs.filter(user=self.request.user)")
        lines.append(f"        return {singular_pascal}.objects.none()")
        lines.append("")
        lines.append("    def create_after_init(self, instance) -> None:")
        lines.append("        instance.user = self.request.user")
    return "\n".join(lines) + "\n"


def _gen_serializers_py(
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
    all_fields.extend(["created_at", "updated_at"])

    fields_str = "[\n"
    for fn in all_fields:
        fields_str += f'            "{fn}",\n'
    fields_str += "        ]"
    lines.append(f"        fields = {fields_str}")

    # read_only_fields
    ro_fields = ["created_at", "updated_at"]
    ro_str = "[" + ", ".join(f'"{f}"' for f in ro_fields) + "]"
    lines.append(f"        read_only_fields = {ro_str}")

    return "\n".join(lines) + "\n"


def _gen_urls_py(
    resource_name: str,
    singular_snake: str,
    plural_pascal: str,
) -> str:
    return textwrap.dedent(f"""\
        from apps.core.urls import make_urlpatterns
        from .views import {plural_pascal}ViewSet

        urlpatterns = make_urlpatterns(
            ("{resource_name}", {plural_pascal}ViewSet, "{singular_snake}"),
        )
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
    if user_scoped:
        lines.append(f"    def test_create_{singular_snake}(self, auth_user):")
    else:
        lines.append(f"    def test_create_{singular_snake}(self):")

    # create kwargs 구성
    create_kwargs = []
    for fn, ft in fields:
        if ft in FIELD_TEST_DEFAULTS:
            create_kwargs.append(f"{fn}={FIELD_TEST_DEFAULTS[ft]}")
    if user_scoped:
        create_kwargs.append("user=auth_user")

    kwargs_str = ", ".join(create_kwargs)
    lines.append(f"        instance = {singular_pascal}.objects.create({kwargs_str})")
    lines.append("        assert instance.pk is not None")

    # 첫 번째 CharField 값 검증
    first_char = next((fn for fn, ft in fields if ft == "CharField"), None)
    if first_char:
        lines.append(f'        assert instance.{first_char} == "test-value"')
    lines.append("")

    # test_str
    if user_scoped:
        lines.append("    def test_str(self, auth_user):")
    else:
        lines.append("    def test_str(self):")
    lines.append(f"        instance = {singular_pascal}.objects.create({kwargs_str})")
    lines.append("        assert str(instance)")

    return "\n".join(lines) + "\n"


FIELD_PAYLOAD_DEFAULTS = {
    "CharField": '"New Value"',
    "TextField": '"New content"',
    "IntegerField": "0",
    "IntegerChoices": "0",
    "BooleanField": "False",
    "DecimalField": '"1.00"',
    "FloatField": "1.0",
}


def _build_create_kwargs(fields: list[tuple[str, str]], user_scoped: bool) -> str:
    """테스트에서 objects.create() 호출에 사용할 kwargs 문자열 생성."""
    parts = []
    for fn, ft in fields:
        if ft in FIELD_TEST_DEFAULTS:
            parts.append(f"{fn}={FIELD_TEST_DEFAULTS[ft]}")
    if user_scoped:
        parts.append("user=mock_authenticated")
    return ", ".join(parts)


def _build_payload_attrs(fields: list[tuple[str, str]]) -> str:
    """테스트에서 jsonapi_payload에 전달할 attrs 문자열 생성."""
    attrs = {}
    for fn, ft in fields:
        if ft in FIELD_PAYLOAD_DEFAULTS:
            attrs[fn] = FIELD_PAYLOAD_DEFAULTS[ft]
    return ", ".join(f'"{k}": {v}' for k, v in attrs.items())


def _gen_test_api_py(
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

    create_kwargs_str = _build_create_kwargs(fields, user_scoped)
    lines.append(f"        {singular_pascal}.objects.create({create_kwargs_str})")
    lines.append("")
    lines.append("        client = APIClient()")
    lines.append("        client.force_authenticate(user=mock_authenticated)")
    lines.append(f'        response = client.get("/api/v1/{resource_name}", **jsonapi_headers)')
    lines.append("        assert response.status_code == 200")
    lines.append("        data = response.json()")
    lines.append('        assert "data" in data')
    lines.append('        assert len(data["data"]) >= 1')
    lines.append("")

    # -- test_create_valid
    lines.append("    def test_create_valid(self, mock_authenticated, jsonapi_headers):")

    attrs_inner = _build_payload_attrs(fields)
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


def _insert_after_last_match(filepath: str, marker: str, line_prefix: str, new_line: str) -> bool:
    """파일에서 marker 이후 line_prefix로 시작하는 마지막 줄 뒤에 new_line을 삽입."""
    if not os.path.isfile(filepath):
        return False

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    if marker not in content:
        return False

    if new_line in content:
        return True

    lines = content.split("\n")
    marker_idx = None
    last_match_idx = None
    for i, line in enumerate(lines):
        if marker in line:
            marker_idx = i
        if marker_idx is not None and line.strip().startswith(line_prefix):
            last_match_idx = i

    if last_match_idx is None:
        return False

    lines.insert(last_match_idx + 1, new_line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return True


def _auto_register_settings(base_dir: str, resource_name: str, plural_pascal: str) -> bool:
    """config/settings/base.py 에 앱 등록"""
    return _insert_after_last_match(
        filepath=os.path.join(base_dir, "config", "settings", "base.py"),
        marker="# Local apps",
        line_prefix='"apps.',
        new_line=f'    "apps.{resource_name}.apps.{plural_pascal}Config",',
    )


def _auto_register_urls(base_dir: str, resource_name: str) -> bool:
    """config/urls.py 에 URL 등록"""
    return _insert_after_last_match(
        filepath=os.path.join(base_dir, "config", "urls.py"),
        marker="# API v1 endpoints",
        line_prefix='path("api/v1/',
        new_line=f'    path("api/v1/", include("apps.{resource_name}.urls")),',
    )


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


class Command(BaseCommand):
    help = "새 API 리소스(모델, 뷰, 시리얼라이저, URL, 테스트)를 자동 생성합니다."

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
            help="user FK 필드 및 소유권 훅 자동 추가",
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

    def handle(self, *args, **options):
        resource_name = options["resource_name"].strip()
        user_scoped = options["user_scoped"]
        no_tests = options["no_tests"]
        model_name_override = options["model_name"].strip()

        # 유효성 검사: snake_case 복수형
        if not re.match(r"^[a-z][a-z0-9_]*$", resource_name):
            raise CommandError(f"리소스 이름은 snake_case여야 합니다: {resource_name}\n예: products, order_items")

        fields = self._parse_fields(options["fields"].strip())

        # 이름 변환
        if model_name_override:
            singular_snake = model_name_override.lower()
            singular_pascal = (
                to_pascal(model_name_override)
                if "_" in model_name_override
                else model_name_override[0].upper() + model_name_override[1:]
            )
        else:
            singular_snake = singularize(resource_name)
            singular_pascal = to_pascal(singular_snake)

        plural_pascal = to_pascal(resource_name)

        # 프로젝트 루트 디렉토리 결정 (manage.py 기준)
        base_dir = str(settings.BASE_DIR)
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
        self.stdout.write(f"  User-scoped: {user_scoped}")
        self.stdout.write(f"  필드: {fields if fields else '(없음)'}")
        self.stdout.write("")

        self._generate_app_files(
            apps_dir,
            resource_name,
            singular_pascal,
            plural_pascal,
            singular_snake,
            fields,
            user_scoped,
        )

        if not no_tests:
            self._generate_test_files(tests_dir, resource_name, singular_pascal, singular_snake, fields, user_scoped)

        self._auto_register_and_report(base_dir, resource_name, plural_pascal)

        # 완료 메시지
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"=== {resource_name} 리소스 생성 완료 ==="))
        self.stdout.write("")
        self.stdout.write("다음 단계:")
        self.stdout.write(f"  1. python manage.py makemigrations {resource_name}")
        self.stdout.write("  2. python manage.py migrate")
        self.stdout.write("  3. 관계 필드가 필요하면 수동으로 추가하세요 (참고: apps/comments/)")
        self.stdout.write("")

    def _parse_fields(self, raw_fields: str) -> list[tuple[str, str]]:
        """필드 문자열을 파싱하고 유효성을 검사합니다."""
        fields: list[tuple[str, str]] = []
        if not raw_fields:
            return fields
        for pair in raw_fields.split():
            if ":" not in pair:
                raise CommandError(f"잘못된 필드 형식입니다: {pair}\n올바른 형식: name:CharField")
            fname, ftype = pair.split(":", 1)
            if not re.match(r"^[a-z_][a-z0-9_]*$", fname):
                raise CommandError(f"잘못된 필드 이름입니다: {fname}\n소문자 snake_case만 허용됩니다.")
            if ftype not in FIELD_TYPE_MAP:
                raise CommandError(
                    f"지원하지 않는 필드 타입입니다: {ftype}\n지원 타입: {', '.join(FIELD_TYPE_MAP.keys())}"
                )
            fields.append((fname, ftype))
        return fields

    def _generate_app_files(
        self,
        apps_dir,
        resource_name,
        singular_pascal,
        plural_pascal,
        singular_snake,
        fields,
        user_scoped,
    ):
        """앱 디렉토리와 소스 파일들을 생성합니다."""
        os.makedirs(apps_dir, exist_ok=True)
        os.makedirs(os.path.join(apps_dir, "migrations"), exist_ok=True)
        self._write_file(os.path.join(apps_dir, "migrations", "__init__.py"), "")
        self._write_file(os.path.join(apps_dir, "__init__.py"), "")
        self._write_file(os.path.join(apps_dir, "apps.py"), _gen_apps_py(resource_name, plural_pascal))
        self._write_file(
            os.path.join(apps_dir, "models.py"),
            _gen_models_py(resource_name, singular_pascal, fields, user_scoped),
        )
        self._write_file(
            os.path.join(apps_dir, "views.py"),
            _gen_views_py(
                resource_name,
                singular_pascal,
                plural_pascal,
                singular_snake,
                fields,
                user_scoped,
            ),
        )
        self._write_file(
            os.path.join(apps_dir, "serializers.py"),
            _gen_serializers_py(singular_pascal, fields, user_scoped),
        )
        self._write_file(os.path.join(apps_dir, "urls.py"), _gen_urls_py(resource_name, singular_snake, plural_pascal))

    def _generate_test_files(self, tests_dir, resource_name, singular_pascal, singular_snake, fields, user_scoped):
        """테스트 디렉토리와 테스트 파일들을 생성합니다."""
        os.makedirs(tests_dir, exist_ok=True)
        self._write_file(os.path.join(tests_dir, "__init__.py"), "")
        self._write_file(
            os.path.join(tests_dir, "test_models.py"),
            _gen_test_models_py(
                resource_name,
                singular_pascal,
                singular_snake,
                fields,
                user_scoped,
            ),
        )
        self._write_file(
            os.path.join(tests_dir, "test_api.py"),
            _gen_test_api_py(resource_name, singular_pascal, fields, user_scoped),
        )

    def _auto_register_and_report(self, base_dir, resource_name, plural_pascal):
        """settings와 urls에 자동 등록하고 결과를 출력합니다."""
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

    def _write_file(self, path: str, content: str):
        """파일을 생성하고 결과를 출력합니다."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        # 프로젝트 루트 기준 상대 경로 출력
        rel = os.path.relpath(path, os.getcwd())
        self.stdout.write(f"  생성: {rel}")
