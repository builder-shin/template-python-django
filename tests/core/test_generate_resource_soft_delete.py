"""generate_resource --soft-delete 옵션 테스트 — Phase 6 TDD Red."""

from apps.core.management.commands.generate_resource import _gen_models_py


class TestGenerateResourceSoftDelete:
    def test_soft_delete_flag_generates_mixin_import(self):
        code = _gen_models_py("items", "Item", [("name", "CharField")], user_scoped=False, soft_delete=True)
        assert "SoftDeleteMixin" in code
        assert "SoftDeleteManager" in code
        assert "SoftDeleteAllManager" in code

    def test_soft_delete_flag_adds_mixin_to_model(self):
        code = _gen_models_py("items", "Item", [("name", "CharField")], user_scoped=False, soft_delete=True)
        assert "class Item(SoftDeleteMixin, BaseModel):" in code

    def test_soft_delete_flag_adds_soft_delete_cascade(self):
        code = _gen_models_py("items", "Item", [("name", "CharField")], user_scoped=False, soft_delete=True)
        assert "soft_delete_cascade = {}" in code

    def test_soft_delete_flag_adds_all_objects_manager(self):
        code = _gen_models_py("items", "Item", [("name", "CharField")], user_scoped=False, soft_delete=True)
        assert "all_objects" in code

    def test_without_soft_delete_flag_no_mixin(self):
        code = _gen_models_py("items", "Item", [("name", "CharField")], user_scoped=False, soft_delete=False)
        assert "SoftDeleteMixin" not in code
        assert "soft_delete_cascade" not in code

    def test_existing_behavior_unchanged(self):
        """기존 호출 (soft_delete 미지정)은 동작이 변경되지 않아야 함."""
        code = _gen_models_py("items", "Item", [("name", "CharField")], user_scoped=False)
        assert "class Item(BaseModel):" in code
        assert "SoftDeleteMixin" not in code
