from rest_framework import serializers
from django.db import transaction
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
        extra_kwargs = {
            'request': {'read_only': True},
        }


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
        extra_kwargs = {
            'order': {'read_only': True},
        }


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, required=False)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    purchaser_name = serializers.CharField(source='purchaser.username', read_only=True)
    request_no = serializers.CharField(source='request.request_no', read_only=True)

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
        extra_kwargs = {
            'stock': {'read_only': True},
        }


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
        self._update_order_receipt(stock)
        self._update_inventory(stock)
        return stock

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseInStockItem.objects.create(stock=instance, **item_data)
        self._update_order_receipt(instance)
        self._update_inventory(instance)
        return instance

    def _update_order_receipt(self, stock):
        """
        入库后联动更新采购订单的已入库数量和状态
        """
        order = stock.order
        if not order:
            return
        from django.db.models import Sum
        stock_items = {}
        for s in order.purchaseinstock_set.all():
            for item in s.items.all():
                key = (item.material_name or '').strip()
                if key:
                    stock_items[key] = stock_items.get(key, 0) + (item.quantity or 0)
        all_completed = True
        any_received = False
        for oi in order.items.all():
            received = stock_items.get((oi.material_name or '').strip(), 0)
            oi.received_qty = received
            oi.save()
            if received > 0:
                any_received = True
            if (oi.quantity or 0) > received:
                all_completed = False
        if all_completed and any_received:
            order.status = 'completed'
        elif any_received:
            order.status = 'partial'
        else:
            order.status = 'confirmed'
        order.save()

    def _update_inventory(self, stock):
        """
        入库后增加库存台账
        """
        from apps.inventory.models import Warehouse, Inventory
        from decimal import Decimal
        warehouse_name = stock.warehouse
        if not warehouse_name:
            return
        warehouse = Warehouse.objects.filter(name=warehouse_name).first()
        if not warehouse:
            return
        for item in stock.items.all():
            qty = item.quantity or Decimal('0')
            if qty <= 0:
                continue
            spec = item.spec or ''
            inv, created = Inventory.objects.get_or_create(
                warehouse=warehouse,
                material_name=item.material_name,
                spec=spec,
                defaults={'unit': item.unit or '件', 'qty': 0}
            )
            inv.qty += qty
            inv.save()
