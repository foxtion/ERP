from rest_framework.permissions import BasePermission


class RBACPermission(BasePermission):
    """
    基于RBAC的接口权限控制
    通过判断用户所属角色的菜单权限标识(permission)来判定是否有权访问
    权限标识格式建议：module:action，如 system:user:view、system:user:add
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True

        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            # 默认拒绝（安全策略）
            return False

        user_permissions = set()
        for role in request.user.roles.all():
            for menu in role.menus.filter(is_active=True, menu_type='BUTTON'):
                if menu.permission:
                    user_permissions.add(menu.permission)

        if isinstance(required_permission, str):
            required_permission = [required_permission]

        return any(perm in user_permissions for perm in required_permission)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
