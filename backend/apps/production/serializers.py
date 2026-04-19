from rest_framework import serializers
from apps.production.models import (
    BOM, BOMItem, ProductionPlan, ProductionOrder,
    MaterialRequisition, MaterialRequisitionItem, ProductionInStock
)


class BOMItemSerializer(serializers.ModelSerializer):
    material_code = serializers.CharField(source='material.code', read_only=True, default='')
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=4, read_only=True)

    class Meta:
        model = BOMItem
        fields = '__all__'


class BOMSerializer(serializers.ModelSerializer):
    items = BOMItemSerializer(many=True, required=False)
    total_cost = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BOM
        fields = '__all__'

    def get_total_cost(self, obj):
        return sum(item.subtotal for item in obj.items.all())

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bom = BOM.objects.create(**validated_data)
        for item_data in items_data:
            # 兼容前端传 material 为对象或 id 的情况
            if 'material' in item_data and isinstance(item_data['material'], dict):
                item_data['material_id'] = item_data.pop('material', {}).get('id')
            BOMItem.objects.create(bom=bom, **item_data)
        return bom

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                if 'material' in item_data and isinstance(item_data['material'], dict):
                    item_data['material_id'] = item_data.pop('material', {}).get('id')
                BOMItem.objects.create(bom=instance, **item_data)
        return instance


class ProductionPlanSerializer(serializers.ModelSerializer):
    planner_name = serializers.CharField(source='planner.username', read_only=True)
    bom_product_name = serializers.CharField(source='bom.product_name', read_only=True)
    order_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductionPlan
        fields = '__all__'
        extra_kwargs = {
            'plan_no': {'required': False},
        }

    def create(self, validated_data):
        if not validated_data.get('plan_no'):
            validated_data['plan_no'] = self._generate_plan_no()
        return super().create(validated_data)

    def _generate_plan_no(self):
        from datetime import datetime
        prefix = 'JH' + datetime.now().strftime('%Y%m%d')
        count = ProductionPlan.objects.filter(plan_no__startswith=prefix).count()
        return f'{prefix}-{count + 1:03d}'


class ProductionOrderSerializer(serializers.ModelSerializer):
    plan_no = serializers.CharField(source='plan.plan_no', read_only=True)
    bom_product_name = serializers.CharField(source='bom.product_name', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    progress = serializers.SerializerMethodField(read_only=True)
    priority_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductionOrder
        fields = '__all__'
        extra_kwargs = {
            'order_no': {'required': False},
        }

    def get_progress(self, obj):
        if not obj.quantity or obj.quantity == 0:
            return 0
        from decimal import Decimal
        progress = (obj.completed_qty or Decimal('0')) / obj.quantity * 100
        return min(100, round(float(progress), 1))

    def get_priority_display(self, obj):
        return dict(ProductionOrder.PRIORITY_CHOICES).get(obj.priority, obj.priority)

    def create(self, validated_data):
        if not validated_data.get('order_no'):
            validated_data['order_no'] = self._generate_order_no()
        return super().create(validated_data)

    def _generate_order_no(self):
        from datetime import datetime
        prefix = 'GD' + datetime.now().strftime('%Y%m%d')
        count = ProductionOrder.objects.filter(order_no__startswith=prefix).count()
        return f'{prefix}-{count + 1:03d}'


class MaterialRequisitionItemSerializer(serializers.ModelSerializer):
    material_code = serializers.CharField(source='material.code', read_only=True, default='')
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=4, read_only=True)

    class Meta:
        model = MaterialRequisitionItem
        fields = '__all__'
        extra_kwargs = {
            'requisition': {'required': False},
        }


class MaterialRequisitionSerializer(serializers.ModelSerializer):
    items = MaterialRequisitionItemSerializer(many=True, required=False)
    production_order_no = serializers.CharField(source='production_order.order_no', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    auditor_name = serializers.CharField(source='auditor.username', read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    total_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MaterialRequisition
        fields = '__all__'
        extra_kwargs = {
            'requisition_no': {'required': False},
        }

    def get_status_display(self, obj):
        return dict(MaterialRequisition.STATUS_CHOICES).get(obj.status, obj.status)

    def get_total_amount(self, obj):
        return sum(item.subtotal for item in obj.items.all())

    def create(self, validated_data):
        if not validated_data.get('requisition_no'):
            validated_data['requisition_no'] = self._generate_requisition_no()
        items_data = validated_data.pop('items', [])
        req = MaterialRequisition.objects.create(**validated_data)
        for item_data in items_data:
            if 'material' in item_data and isinstance(item_data['material'], dict):
                item_data['material_id'] = item_data.pop('material', {}).get('id')
            MaterialRequisitionItem.objects.create(requisition=req, **item_data)
        return req

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                if 'material' in item_data and isinstance(item_data['material'], dict):
                    item_data['material_id'] = item_data.pop('material', {}).get('id')
                MaterialRequisitionItem.objects.create(requisition=instance, **item_data)
        return instance

    def _generate_requisition_no(self):
        from datetime import datetime
        prefix = 'LL' + datetime.now().strftime('%Y%m%d')
        count = MaterialRequisition.objects.filter(requisition_no__startswith=prefix).count()
        return f'{prefix}-{count + 1:03d}'


class ProductionInStockSerializer(serializers.ModelSerializer):
    production_order_no = serializers.CharField(source='production_order.order_no', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    auditor_name = serializers.CharField(source='auditor.username', read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductionInStock
        fields = '__all__'
        extra_kwargs = {
            'stock_no': {'required': False},
        }

    def get_status_display(self, obj):
        return dict(ProductionInStock.STATUS_CHOICES).get(obj.status, obj.status)

    def create(self, validated_data):
        if not validated_data.get('stock_no'):
            validated_data['stock_no'] = self._generate_stock_no()
        return super().create(validated_data)

    def _generate_stock_no(self):
        from datetime import datetime
        prefix = 'RK' + datetime.now().strftime('%Y%m%d')
        count = ProductionInStock.objects.filter(stock_no__startswith=prefix).count()
        return f'{prefix}-{count + 1:03d}'
