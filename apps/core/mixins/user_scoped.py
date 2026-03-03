from apps.core.exceptions import JsonApiError


class UserScopedMixin:
    """사용자 소유권 검증을 위한 Mixin.

    user FK 기반 리소스 소유권 검증과 공통 lifecycle hook을 제공한다.
    resource_label을 오버라이드하여 에러 메시지를 커스터마이즈할 수 있다.
    """

    resource_label = "리소스"

    def _check_ownership(self, instance, action_label: str) -> None:
        if instance.user_id != self.request.user.id:
            raise JsonApiError(
                "Forbidden",
                f"본인의 {self.resource_label}만 {action_label}할 수 있습니다.",
                403,
            )

    def create_after_init(self, instance) -> None:
        instance.user = self.request.user

    def update_after_init(self, instance) -> None:
        self._check_ownership(instance, "수정")

    def destroy_after_init(self, instance) -> None:
        self._check_ownership(instance, "삭제")
