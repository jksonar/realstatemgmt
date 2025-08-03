from rest_framework import permissions

def IsGroupMember(group_name):
    class IsInGroup(permissions.BasePermission):
        def has_permission(self, request, view):
            return request.user.groups.filter(name=group_name).exists()
    return IsInGroup
