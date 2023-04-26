from rest_framework import permissions


class IsAuthorOrAdminPermissoin(permissions.BasePermission):
    message = (
        'Только администратор или автор может менять контент.')

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or obj.author == request.user)
