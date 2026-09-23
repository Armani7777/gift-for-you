from rest_framework.permissions import BasePermission

from .exceptions import InvitationError
from .services import get_managed_invitation, get_public_invitation


class HasPublicInvitation(BasePermission):
    def has_permission(self, request, view) -> bool:
        token = view.kwargs.get("public_token")
        if not token:
            return False
        try:
            view.invitation = get_public_invitation(token)
        except InvitationError as exc:
            raise exc
        return True


class HasManagementAccess(BasePermission):
    def has_permission(self, request, view) -> bool:
        public_token = view.kwargs.get("public_token")
        management_token = view.kwargs.get("management_token")
        if not public_token or not management_token:
            return False
        view.invitation = get_managed_invitation(public_token, management_token)
        return True
