from rest_framework import serializers
from apps.production.models import (
    BOM, BOMItem, ProductionPlan, ProductionOrder,
    MaterialRequisition, MaterialRequisitionItem, ProductionInStock
)


class BOMItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BOMItem
        fields = '__all__'


class BOMSerializer(serializers.ModelSerializer):
    items = BOMItemSerializer(many=True, required=False)

    class Meta:
        model = BOM
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bom = BOM.objects.create(**validated_data)
        for item_data in items_data:
            BOMItem.objects.create(bom=bom, **item_data)
        return bom

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                BOMItem.objects.create(bom=instance, **item_data)
        return instance


class ProductionPlanSerializer(serializers.ModelSerializer):
    planner_name = serializers.CharField(source='planner.username', read_only=True)

    class Meta:
        model = ProductionPlan
        fields = '__all__'


class ProductionOrderSerializer(serializers.ModelSerializer):
    plan_no = serializers.CharField(source='plan.plan_no', read_only=True)
    bom_product_name = serializers.CharField(source='bom.product_name', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = ProductionOrder
        fields = '__all__'


class MaterialRequisitionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialRequisitionItem
        fields = '__all__'


class MaterialRequisitionSerializer(serializers.ModelSerializer):
    items = MaterialRequisitionItemSerializer(many=True, required=False)
    production_order_no = serializers.CharField(source='production_order.order_no', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = MaterialRequisition
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        req = MaterialRequisition.objects.create(**validated_data)
        for item_data in items_data:
            MaterialRequisitionItem.objects.create(requisition=req, **item_data)
        return req

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                MaterialRequisitionItem.objects.create(requisition=instance, **item_data)
        return instance


class ProductionInStockSerializer(serializers.ModelSerializer):
    production_order_no = serializers.CharField(source='production_order.order_no', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = ProductionInStock
        fields = '__all__'
