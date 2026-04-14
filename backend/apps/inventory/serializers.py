from rest_framework import serializers
from apps.inventory.models import (
    Warehouse, Inventory, StockTransfer, StockTransferItem,
    InventoryCheck, InventoryCheckItem
)


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'


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
            InventoryCheckItem.objects.create(check=check, **item_data)
        return check

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                InventoryCheckItem.objects.create(check=instance, **item_data)
        return instance
