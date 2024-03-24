from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """Вносить изменения может только администратор или автор контента."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.is_admin
                or request.user == obj.author
            )
        )


class SelfORAdminOrReadOnly(BasePermission):
    """Вносить изменения может только администаратор или
    владалец учетной записи.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            request.user == obj
            or request.user.is_admin
            or request.user.is_superuser
        )
