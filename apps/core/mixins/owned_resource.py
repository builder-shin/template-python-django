from apps.core.exceptions import JsonApiError


class OwnedResourceMixin:
    """
    user_id 기반 소유권 검증을 제공하는 Mixin.
    resource_name을 오버라이드하여 에러 메시지를 커스터마이즈.
    """

    owner_field: str = "user_id"
    resource_label: str = "리소스"

    def _check_ownership(self, instance, action_label: str) -> None:
        """소유권을 검증하고, 실패 시 403 JsonApiError를 raise한다."""
        owner_id = getattr(instance, self.owner_field, None)
        if str(owner_id) != str(self.request.user.id):
            raise JsonApiError(
                "Forbidden",
                f"본인의 {self.resource_label}만 {action_label}할 수 있습니다.",
                403,
            )

    def create_after_init(self, instance) -> None:
        setattr(instance, self.owner_field, str(self.request.user.id))

    def update_after_init(self, instance) -> None:
        self._check_ownership(instance, "수정")

    def destroy_after_init(self, instance) -> None:
        self._check_ownership(instance, "삭제")
