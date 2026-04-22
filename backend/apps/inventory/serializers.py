from rest_framework import serializers
from apps.inventory.models import (
    Warehouse, Inventory, StockTransfer, StockTransferItem,
    InventoryCheck, InventoryCheckItem, WarehouseLocation, Material, StockWarning
)


class MaterialSerializer(serializers.ModelSerializer):
    warning_status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Material
        fields = '__all__'

    def get_warning_status_display(self, obj):
        return '预警' if obj.qty <= obj.warning_threshold else '正常'


class StockWarningSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    handler_name = serializers.CharField(source='handler.username', read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    material_code = serializers.CharField(source='material.code', read_only=True, default='')

    class Meta:
        model = StockWarning
        fields = '__all__'

    def get_status_display(self, obj):
        return dict(StockWarning.STATUS_CHOICES).get(obj.status, obj.status)


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'


class WarehouseLocationSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    warehouse_code = serializers.CharField(source='warehouse.code', read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WarehouseLocation
        fields = '__all__'

    def get_status_display(self, obj):
        return '空位' if obj.is_empty else '有货'


class InventorySerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    warning_status_display = serializers.SerializerMethodField(read_only=True)
    material_code = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'

    def get_warning_status_display(self, obj):
        threshold = obj.material.warning_threshold if hasattr(obj, 'material') and obj.material else 50
        return '预警' if obj.qty <= threshold else '正常'

    def get_material_code(self, obj):
        if hasattr(obj, 'material') and obj.material:
            return obj.material.code
        return ''


class StockTransferItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransferItem
        fields = '__all__'


class StockTransferSerializer(serializers.ModelSerializer):
    items = StockTransferItemSerializer(many=True, required=False)
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = StockTransfer
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        transfer = StockTransfer.objects.create(**validated_data)
        for item_data in items_data:
            StockTransferItem.objects.create(transfer=transfer, **item_data)
        return transfer

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                StockTransferItem.objects.create(transfer=instance, **item_data)
        return instance


class InventoryCheckItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCheckItem
        fields = '__all__'


class InventoryCheckSerializer(serializers.ModelSerializer):
    items = InventoryCheckItemSerializer(many=True, required=False)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = InventoryCheck
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        check = InventoryCheck.objects.create(**validated_data)
        for item_data in items_data:
            InventoryCheckItem.objects.create(check_order=check, **item_data)
        return check

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                InventoryCheckItem.objects.create(check_order=instance, **item_data)
        return instance
