from rest_framework import serializers
from apps.purchase.models import (
    Supplier, PurchaseRequest, PurchaseRequestItem,
    PurchaseOrder, PurchaseOrderItem, PurchaseInStock, PurchaseInStockItem
)


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

    def validate_code(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('供应商编码不能为空')
        queryset = Supplier.objects.filter(code=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('供应商编码已存在')
        return value

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('供应商名称不能为空')
        return value


class PurchaseRequestItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequestItem
        fields = '__all__'


class PurchaseRequestSerializer(serializers.ModelSerializer):
    items = PurchaseRequestItemSerializer(many=True, required=False)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request_obj = PurchaseRequest.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            item = PurchaseRequestItem.objects.create(request=request_obj, **item_data)
            total += item.estimated_amount
        request_obj.total_amount = total
        request_obj.save()
        return request_obj

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            total = 0
            for item_data in items_data:
                item = PurchaseRequestItem.objects.create(request=instance, **item_data)
                total += item.estimated_amount
            instance.total_amount = total
            instance.save()
        return instance


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, required=False)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    purchaser_name = serializers.CharField(source='purchaser.username', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = PurchaseOrder.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            item = PurchaseOrderItem.objects.create(order=order, **item_data)
            total += item.amount
        order.total_amount = total
        order.save()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            total = 0
            for item_data in items_data:
                item = PurchaseOrderItem.objects.create(order=instance, **item_data)
                total += item.amount
            instance.total_amount = total
            instance.save()
        return instance


class PurchaseInStockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInStockItem
        fields = '__all__'


class PurchaseInStockSerializer(serializers.ModelSerializer):
    items = PurchaseInStockItemSerializer(many=True, required=False)
    order_no = serializers.CharField(source='order.order_no', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = PurchaseInStock
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        stock = PurchaseInStock.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseInStockItem.objects.create(stock=stock, **item_data)
        return stock

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseInStockItem.objects.create(stock=instance, **item_data)
        return instance
