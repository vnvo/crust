from rest_framework import permissions

class IsAdminOrCGOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, cg_obj):
        if request.user.is_admin:
            return True
        if request.user == cg_obj.supervisor:
            return True

        return False

class IsAdminOrCommandPatternOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, cp_obj):
        if request.user.is_admin:
            return True
        elif request.user == cp_obj.commandgroup.supervisor:
            return True

        return False
