from rest_framework.permissions import BasePermission


# 部门 → 权限前缀映射（用于无角色员工的部门兜底）
# 格式: 部门名称 -> [权限前缀列表，优先匹配长的]
DEPT_PERM_PREFIXES = {
    '采购部': ['purchase', 'supplier', 'porder', 'request', 'instock', 'in_stock'],
    '销售部': ['sales', 'customer', 'sorder', 'outstock', 'return', 'out_stock'],
    '仓库部': ['inventory', 'warehouse', 'stock', 'material', 'location', 'warning', 'transfer', 'check', 'sales:picking', 'sales:outstock'],
    '生产部': ['production', 'bom', 'workorder', 'plan', 'requisition', 'production_instock'],
    '财务部': ['finance', 'receivable', 'voucher', 'payment', 'statement', 'subject', 'counterparty'],
    '人力资源部': ['hr', 'employee', 'attendance', 'salary'],
}


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
            # 视图未声明权限要求，放行（由视图自身的其他权限类控制）
            return True

        user_permissions = set()
        for role in request.user.roles.all():
            for menu in role.menus.filter(is_active=True, menu_type='BUTTON'):
                if menu.permission:
                    user_permissions.add(menu.permission)

        if isinstance(required_permission, str):
            required_permission = [required_permission]

        if any(perm in user_permissions for perm in required_permission):
            return True

        # 部门员工兜底：有部门的用户，可以访问本部门的 view / job 类权限
        user_dept = None
        if hasattr(request.user, 'employee_profile') and request.user.employee_profile:
            user_dept = request.user.employee_profile.department
        elif request.user.dept:
            user_dept = request.user.dept.name

        if user_dept:
            prefixes = DEPT_PERM_PREFIXES.get(user_dept, [])
            for perm in required_permission:
                for prefix in prefixes:
                    if perm.startswith(prefix + ':'):
                        # 只允许 view / job / operate 类操作权限
                        if any(perm.endswith(suffix) for suffix in (':view', ':job', ':operate', ':execute')):
                            return True
                        break

        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
