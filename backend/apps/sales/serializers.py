from rest_framework import serializers
from apps.sales.models import (
    Customer, SalesOrder, SalesOrderItem,
    SalesOutStock, SalesOutStockItem, SalesReturn, SalesReturnItem
)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class SalesOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderItem
        fields = '__all__'


class SalesOrderSerializer(serializers.ModelSerializer):
    items = SalesOrderItemSerializer(many=True, required=False)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    salesman_name = serializers.CharField(source='salesman.username', read_only=True)

    class Meta:
        model = SalesOrder
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = SalesOrder.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            item = SalesOrderItem.objects.create(order=order, **item_data)
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
                item = SalesOrderItem.objects.create(order=instance, **item_data)
                total += item.amount
            instance.total_amount = total
            instance.save()
        return instance


class SalesOutStockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOutStockItem
        fields = '__all__'


class SalesOutStockSerializer(serializers.ModelSerializer):
    items = SalesOutStockItemSerializer(many=True, required=False)
    order_no = serializers.CharField(source='order.order_no', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = SalesOutStock
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        stock = SalesOutStock.objects.create(**validated_data)
        for item_data in items_data:
            SalesOutStockItem.objects.create(stock=stock, **item_data)
        return stock

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                SalesOutStockItem.objects.create(stock=instance, **item_data)
        return instance


class SalesReturnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReturnItem
        fields = '__all__'


class SalesReturnSerializer(serializers.ModelSerializer):
    items = SalesReturnItemSerializer(many=True, required=False)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = SalesReturn
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        return_obj = SalesReturn.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            item = SalesReturnItem.objects.create(return_order=return_obj, **item_data)
            total += item.amount
        return_obj.total_amount = total
        return_obj.save()
        return return_obj

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            total = 0
            for item_data in items_data:
                item = SalesReturnItem.objects.create(return_order=instance, **item_data)
                total += item.amount
            instance.total_amount = total
            instance.save()
        return instance
