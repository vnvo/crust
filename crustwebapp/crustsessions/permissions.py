from rest_framework import permissions

class CanSeeSession(permissions.BasePermission):
    def has_object_permission(self, request, view, session_obj):
        if request.user.is_admin:
            return True



        return False
