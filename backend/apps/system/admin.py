from django.contrib import admin
from apps.system.models import User, Role, Menu, Department


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'phone', 'dept', 'is_active', 'created_at']
    list_filter = ['is_active', 'dept']
    search_fields = ['username', 'email', 'phone']
    filter_horizontal = ['roles', 'groups', 'user_permissions']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'sort_order', 'is_active']
    search_fields = ['name', 'code']
    filter_horizontal = ['menus']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'name', 'menu_type', 'path', 'permission', 'sort_order']
    list_filter = ['menu_type', 'is_active']
    search_fields = ['title', 'name', 'path']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'parent', 'sort_order']
    search_fields = ['name', 'code']
