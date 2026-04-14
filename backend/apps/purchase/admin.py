from django.contrib import admin
from apps.purchase.models import (
    Supplier, PurchaseRequest, PurchaseRequestItem,
    PurchaseOrder, PurchaseOrderItem, PurchaseInStock, PurchaseInStockItem
)


class PurchaseRequestItemInline(admin.TabularInline):
    model = PurchaseRequestItem
    extra = 1


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


class PurchaseInStockItemInline(admin.TabularInline):
    model = PurchaseInStockItem
    extra = 1


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact', 'phone', 'is_active']
    search_fields = ['code', 'name', 'contact']


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['request_no', 'applicant', 'request_date', 'status', 'total_amount']
    inlines = [PurchaseRequestItemInline]
    search_fields = ['request_no']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'supplier', 'order_date', 'status', 'total_amount']
    inlines = [PurchaseOrderItemInline]
    search_fields = ['order_no']


@admin.register(PurchaseInStock)
class PurchaseInStockAdmin(admin.ModelAdmin):
    list_display = ['stock_no', 'order', 'stock_date', 'warehouse', 'operator']
    inlines = [PurchaseInStockItemInline]
    search_fields = ['stock_no']
