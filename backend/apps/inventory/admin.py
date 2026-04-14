from django.contrib import admin
from apps.inventory.models import (
    Warehouse, Inventory, StockTransfer, StockTransferItem,
    InventoryCheck, InventoryCheckItem
)


class StockTransferItemInline(admin.TabularInline):
    model = StockTransferItem
    extra = 1


class InventoryCheckItemInline(admin.TabularInline):
    model = InventoryCheckItem
    extra = 1


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'location', 'manager', 'is_active']
    search_fields = ['code', 'name']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['warehouse', 'material_name', 'spec', 'unit', 'qty', 'updated_at']
    search_fields = ['material_name', 'spec']
    list_filter = ['warehouse']


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ['transfer_no', 'from_warehouse', 'to_warehouse', 'transfer_date', 'operator']
    inlines = [StockTransferItemInline]
    search_fields = ['transfer_no']


@admin.register(InventoryCheck)
class InventoryCheckAdmin(admin.ModelAdmin):
    list_display = ['check_no', 'warehouse', 'check_date', 'status', 'operator']
    inlines = [InventoryCheckItemInline]
    search_fields = ['check_no']
