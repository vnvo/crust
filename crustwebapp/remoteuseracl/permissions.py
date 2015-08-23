from rest_framework import permissions

class IsAdminOrRuleOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, rule_obj):
        if request.user.is_admin:
            return True

        if rule_obj.server_group and rule_obj.server_group.supervisor == request.user:
            return True

        if rule_obj.server and rule_obj.server.server_group.supervisor == request.user:
            return True

        if rule_obj.server_account:
            supervisor = rule_obj.server_account.server.server_group.supervisor
            if supervisor == request.user:
                return True

        return False
