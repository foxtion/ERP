from django.contrib import admin
from apps.sales.models import (
    Customer, SalesOrder, SalesOrderItem,
    SalesOutStock, SalesOutStockItem, SalesReturn, SalesReturnItem
)


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1


class SalesOutStockItemInline(admin.TabularInline):
    model = SalesOutStockItem
    extra = 1


class SalesReturnItemInline(admin.TabularInline):
    model = SalesReturnItem
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact', 'phone', 'is_active']
    search_fields = ['code', 'name', 'contact']


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'customer', 'order_date', 'status', 'total_amount']
    inlines = [SalesOrderItemInline]
    search_fields = ['order_no']


@admin.register(SalesOutStock)
class SalesOutStockAdmin(admin.ModelAdmin):
    list_display = ['stock_no', 'order', 'stock_date', 'warehouse', 'operator']
    inlines = [SalesOutStockItemInline]
    search_fields = ['stock_no']


@admin.register(SalesReturn)
class SalesReturnAdmin(admin.ModelAdmin):
    list_display = ['return_no', 'customer', 'return_date', 'total_amount', 'operator']
    inlines = [SalesReturnItemInline]
    search_fields = ['return_no']
