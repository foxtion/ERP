from django.contrib import admin
from apps.production.models import (
    BOM, BOMItem, ProductionPlan, ProductionOrder,
    MaterialRequisition, MaterialRequisitionItem, ProductionInStock
)


class BOMItemInline(admin.TabularInline):
    model = BOMItem
    extra = 1


class MaterialRequisitionItemInline(admin.TabularInline):
    model = MaterialRequisitionItem
    extra = 1


@admin.register(BOM)
class BOMAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'product_name', 'version', 'is_active']
    inlines = [BOMItemInline]
    search_fields = ['product_code', 'product_name']


@admin.register(ProductionPlan)
class ProductionPlanAdmin(admin.ModelAdmin):
    list_display = ['plan_no', 'product_name', 'quantity', 'plan_date', 'status']
    search_fields = ['plan_no']


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'product_name', 'quantity', 'order_date', 'status']
    search_fields = ['order_no']


@admin.register(MaterialRequisition)
class MaterialRequisitionAdmin(admin.ModelAdmin):
    list_display = ['requisition_no', 'production_order', 'requisition_date', 'warehouse']
    inlines = [MaterialRequisitionItemInline]
    search_fields = ['requisition_no']


@admin.register(ProductionInStock)
class ProductionInStockAdmin(admin.ModelAdmin):
    list_display = ['stock_no', 'production_order', 'product_name', 'quantity', 'stock_date']
    search_fields = ['stock_no']
