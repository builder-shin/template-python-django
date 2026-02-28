from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthUser:
    """
    Non-DB-backed user model representing authenticated user from external auth service.
    Equivalent to Rails AuthUser (ActiveModel::API).
    """

    id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    workspace_id: Optional[str] = None
    workspace_kind: Optional[str] = None
    workspace_role: Optional[str] = None
    member_status: Optional[str] = None

    @property
    def is_authenticated(self):
        return self.id is not None

    @property
    def is_anonymous(self):
        return self.id is None

    def is_personal(self):
        return self.workspace_kind == "personal"

    def is_enterprise(self):
        return self.workspace_kind == "enterprise"

    def is_active(self):
        return self.member_status == "active"
