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

    def _validate_location(self, value, size_label, size_code):
        if value == '' or value is None:
            return None
        value = value.strip()
        if not value:
            return None
        loc = WarehouseLocation.objects.filter(location_code=value, size=size_code).first()
        if not loc:
            raise serializers.ValidationError(f'{size_label} {value} 不存在于库位管理中')
        return value

    def validate_large_location(self, value):
        return self._validate_location(value, '大库位', '大')

    def validate_small_location(self, value):
        value = self._validate_location(value, '小库位', '小')
        if value is None:
            return None
        # 检查是否已被其他物料占用
        instance = getattr(self, 'instance', None)
        queryset = Material.objects.filter(small_location=value)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(f'小库位 {value} 已被物料 {queryset.first().code} 占用')
        return value


class StockWarningSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    handler_name = serializers.CharField(source='handler.username', read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    material_code = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StockWarning
        fields = '__all__'

    def get_status_display(self, obj):
        return dict(StockWarning.STATUS_CHOICES).get(obj.status, obj.status)

    def get_material_code(self, obj):
        # 优先从模型字段读取
        if getattr(obj, 'material_code', None):
            return obj.material_code
        # 其次从关联物料读取
        if obj.material:
            return obj.material.code
        # 最后从备注中解析
        import re
        match = re.search(r'（([^）]+)）', obj.remark or '')
        if match:
            return match.group(1)
        return ''


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
        # Inventory 无 material 外键，通过名称查询 Material 表获取真实阈值
        from apps.inventory.models import Material
        material = Material.objects.filter(name=obj.material_name).first()
        threshold = material.warning_threshold if material else 50
        return '预警' if obj.qty <= threshold else '正常'

    def get_material_code(self, obj):
        if getattr(obj, 'material_code', None):
            return obj.material_code
        from apps.inventory.models import Material
        material = Material.objects.filter(name=obj.material_name).first()
        return material.code if material else ''


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
