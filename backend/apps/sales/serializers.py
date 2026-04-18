import datetime
from rest_framework import serializers
from django.db.models import Sum
from apps.sales.models import (
    Customer, SalesOrder, SalesOrderItem,
    SalesOutStock, SalesOutStockItem, SalesReturn, SalesReturnItem
)


def generate_order_no(prefix='SO'):
    """自动生成订单编号：SO + 年月日 + 4位流水号"""
    today = datetime.date.today()
    date_str = today.strftime('%Y%m%d')
    like_str = f'{prefix}{date_str}'
    # 获取当天最大序号
    latest = SalesOrder.objects.filter(order_no__startswith=like_str).order_by('-order_no').first()
    if latest:
        try:
            seq = int(latest.order_no[len(like_str):]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f'{like_str}{seq:04d}'


class CustomerSerializer(serializers.ModelSerializer):
    order_count = serializers.SerializerMethodField(read_only=True)
    order_total_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'

    def get_order_count(self, obj):
        return obj.salesorder_set.count()

    def get_order_total_amount(self, obj):
        total = obj.salesorder_set.aggregate(total=Sum('total_amount'))['total']
        return total or 0


class CustomerListSerializer(serializers.ModelSerializer):
    """客户列表专用序列化器（轻量）"""
    order_count = serializers.SerializerMethodField(read_only=True)
    order_total_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'code', 'name', 'contact', 'phone', 'email',
            'address', 'industry', 'level', 'credit_limit',
            'is_active', 'remark', 'created_at', 'updated_at',
            'order_count', 'order_total_amount',
        ]

    def get_order_count(self, obj):
        return obj.salesorder_set.count()

    def get_order_total_amount(self, obj):
        total = obj.salesorder_set.aggregate(total=Sum('total_amount'))['total']
        return total or 0


class SalesOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderItem
        fields = '__all__'
        extra_kwargs = {
            'order': {'read_only': True},
        }


class SalesOrderSerializer(serializers.ModelSerializer):
    items = SalesOrderItemSerializer(many=True, required=False)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    salesman_name = serializers.CharField(source='salesman.username', read_only=True)

    class Meta:
        model = SalesOrder
        fields = '__all__'
        extra_kwargs = {
            'order_no': {'required': False},
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        if not validated_data.get('order_no'):
            validated_data['order_no'] = generate_order_no()
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
