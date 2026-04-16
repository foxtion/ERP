import django_filters
from apps.purchase.models import Supplier


class SupplierFilter(django_filters.FilterSet):
    """
    供应商筛选器：支持关键字搜索、状态筛选
    """
    is_active = django_filters.BooleanFilter(field_name='is_active', label='是否启用')
    keyword = django_filters.CharFilter(method='filter_keyword', label='关键字')

    class Meta:
        model = Supplier
        fields = ['is_active']

    def filter_keyword(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            code__icontains=value
        ) | queryset.filter(
            name__icontains=value
        ) | queryset.filter(
            contact__icontains=value
        ) | queryset.filter(
            phone__icontains=value
        )
