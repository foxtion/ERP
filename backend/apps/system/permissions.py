from rest_framework.permissions import BasePermission


class RBACPermission(BasePermission):
    """
    基于RBAC的接口权限控制
    通过判断用户所属角色的菜单权限标识(permission)来判定是否有权访问
    权限标识格式建议：module:action，如 system:user:view、system:user:add
    """
    def has_permission(self, request, view):
        # 超级管理员直接放行
        if request.user and request.user.is_superuser:
            return True

        # 尝试从视图类中获取 required_permission 属性
        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            # 如果没有配置 required_permission，默认放行
            return True

        # 收集当前用户所有角色的权限标识
        user_permissions = set()
        for role in request.user.roles.all():
            for menu in role.menus.filter(is_active=True, menu_type='BUTTON'):
                if menu.permission:
                    user_permissions.add(menu.permission)

        # 支持 required_permission 为字符串或列表
        if isinstance(required_permission, str):
            required_permission = [required_permission]

        # 只要满足其中任意一个权限即可
        return any(perm in user_permissions for perm in required_permission)
