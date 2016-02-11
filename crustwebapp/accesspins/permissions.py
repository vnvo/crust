from rest_framework import permissions

class IsAdminOrPINOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, pin_obj):
        if request.user.is_admin:
            return True
        if pin_obj.supervisor == request.user:
            return True
        return False
