from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class IsAuthorOrAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    """Вносить изменения может только администратор или автор контента."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_superuser or request.user == obj.author)
        )
