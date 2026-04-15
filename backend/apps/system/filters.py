import django_filters
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFilter(django_filters.FilterSet):
    """
    用户列表筛选器：支持按部门、状态、创建时间范围筛选
    """
    dept = django_filters.NumberFilter(field_name='dept_id', label='所属部门')
    is_active = django_filters.BooleanFilter(field_name='is_active', label='是否启用')
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte', label='创建时间起')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte', label='创建时间止')

    class Meta:
        model = User
        fields = ['dept', 'is_active']
