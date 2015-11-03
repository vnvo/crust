from rest_framework import permissions

class IsAdminOrGroupOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, group_obj):
        if request.user.is_admin:
            return True

        if group_obj.supervisor == request.user:
            return True

        return False

class IsAdminOrServerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, server_obj):
        if request.user.is_admin:
            return True
        if server_obj.server_group.supervisor == request.user:
            return True

        return False

class IsAdminOrServerAccountOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, serveraccount_obj):
        if request.user.is_admin:
            return True
        if serveraccount_obj.server.server_group.supervisor == request.user:
            return True

        return False
