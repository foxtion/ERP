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
        extra_kwargs = {
            'code': {'validators': []},
        }

    def get_warning_status_display(self, obj):
        return '预警' if obj.qty <= obj.warning_threshold else '正常'

    def create(self, validated_data):
        code = validated_data.get('code')
        existing = Material.objects.filter(code=code).first()
        if existing:
            # 已存在则累加数量，同时更新其他字段（如果有传）
            add_qty = validated_data.get('qty', 0) or 0
            existing.qty = (existing.qty or 0) + add_qty
            if validated_data.get('name'):
                existing.name = validated_data['name']
            if validated_data.get('category'):
                existing.category = validated_data['category']
            if validated_data.get('unit'):
                existing.unit = validated_data['unit']
            if validated_data.get('spec') is not None:
                existing.spec = validated_data['spec']
            if validated_data.get('barcode') is not None:
                existing.barcode = validated_data['barcode']
            existing.save()
            return existing
        return super().create(validated_data)


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
        from apps.inventory.models import Material
        mat = Material.objects.filter(name=obj.material_name).first()
        threshold = mat.warning_threshold if mat else 50
        return '预警' if obj.qty <= threshold else '正常'

    def get_material_code(self, obj):
        from apps.inventory.models import Material
        if not obj.material_name:
            return ''
        mat = Material.objects.filter(name=obj.material_name).first()
        return mat.code if mat else ''


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
