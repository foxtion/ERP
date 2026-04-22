import datetime
from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from django.db.models import Sum
from apps.sales.models import (
    Customer, SalesOrder, SalesOrderItem,
    SalesOutStock, SalesOutStockItem, SalesReturn, SalesReturnItem,
    SalesPickingList, SalesPickingListItem
)


def generate_order_no(prefix='SO', model=SalesOrder, field='order_no'):
    """自动生成编号：prefix + 年月日 + 4位流水号"""
    today = datetime.date.today()
    date_str = today.strftime('%Y%m%d')
    like_str = f'{prefix}{date_str}'
    latest = model.objects.filter(**{f'{field}__startswith': like_str}).order_by('-id').first()
    if latest:
        try:
            no = getattr(latest, field)
            seq = int(no[len(like_str):]) + 1
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


class SalesOrderItemCreateSerializer(serializers.ModelSerializer):
    """
    销售订单明细创建专用序列化器
    """
    class Meta:
        model = SalesOrderItem
        fields = ['material_code', 'material_name', 'spec', 'quantity', 'unit', 'price', 'remark']


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
        extra_kwargs = {
            'stock': {'read_only': True},
        }


class SalesOutStockSerializer(serializers.ModelSerializer):
    items = SalesOutStockItemSerializer(many=True, required=False)
    order_no = serializers.CharField(source='order.order_no', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = SalesOutStock
        fields = '__all__'
        extra_kwargs = {
            'stock_no': {'required': False},
        }

    def create(self, validated_data):
        from apps.inventory.models import Inventory, Warehouse

        items_data = validated_data.pop('items', [])
        order = validated_data.get('order')
        customer = order.customer if order else None

        # 校验订单状态
        if order and order.status not in ('confirmed', 'partial'):
            raise serializers.ValidationError('只能对已确认或部分出库的订单进行出库')

        # 自动生成出库单号
        if not validated_data.get('stock_no'):
            validated_data['stock_no'] = generate_order_no('CK', model=SalesOutStock, field='stock_no')

        # 解析仓库
        warehouse_name = validated_data.get('warehouse', '默认仓库')
        warehouse = Warehouse.objects.filter(name=warehouse_name).first()

        stock = SalesOutStock.objects.create(**validated_data)

        for item_data in items_data:
            SalesOutStockItem.objects.create(stock=stock, **item_data)

            # 扣减库存台账（必须按仓库扣减）
            material_name = item_data.get('material_name')
            spec = item_data.get('spec') or ''
            out_qty = item_data.get('quantity') or Decimal('0')

            if material_name and out_qty > 0:
                inv_query = Inventory.objects.filter(
                    material_name=material_name,
                    spec=spec
                )
                if warehouse:
                    inv_query = inv_query.filter(warehouse=warehouse)
                inv = inv_query.first()
                if inv:
                    if inv.qty < out_qty:
                        raise serializers.ValidationError(f'物料 "{material_name}" 库存不足，当前库存 {inv.qty}')
                    inv.qty -= out_qty
                    inv.save()

            # 更新销售订单明细的已出库数量（通过order_item_id精确匹配）
            if order and material_name:
                order_item = SalesOrderItem.objects.filter(
                    order=order,
                    material_name=material_name,
                    spec=spec or ''
                ).first()
                if order_item:
                    order_item.delivered_qty = (order_item.delivered_qty or Decimal('0')) + out_qty
                    order_item.save()

        # 更新销售订单状态 + 拆单处理
        if order:
            self._update_order_status(order, customer)

        return stock

    def _update_order_status(self, order, customer=None):
        items = SalesOrderItem.objects.filter(order=order)
        total_qty = Decimal('0')
        total_delivered = Decimal('0')
        has_remaining = False

        for item in items:
            qty = item.quantity or Decimal('0')
            delivered = item.delivered_qty or Decimal('0')
            total_qty += qty
            total_delivered += delivered
            if delivered < qty:
                has_remaining = True

        if total_delivered >= total_qty and total_qty > 0:
            order.status = 'completed'
            order.save()
        elif total_delivered > 0:
            if customer and customer.allow_partial_shipment:
                order.status = 'completed'
                order.save()
                self._split_order(order, items)
            else:
                order.status = 'partial'
                order.save()

    def _split_order(self, order, items):
        """
        拆单：为未出库完成的物料生成新订单
        """
        remaining_items = []
        for item in items:
            remaining = (item.quantity or Decimal('0')) - (item.delivered_qty or Decimal('0'))
            if remaining > 0:
                remaining_items.append({
                    'material_code': item.material_code,
                    'material_name': item.material_name,
                    'spec': item.spec,
                    'quantity': remaining,
                    'unit': item.unit,
                    'price': item.price,
                    'remark': item.remark,
                })

        if not remaining_items:
            return

        new_order = SalesOrder.objects.create(
            order_no=generate_order_no(),
            customer=order.customer,
            order_date=order.order_date,
            delivery_date=order.delivery_date,
            status='confirmed',
            total_amount=0,
            salesman=order.salesman,
            remark=f'由订单 {order.order_no} 部分出库后自动拆单生成',
        )

        total = 0
        for item_data in remaining_items:
            item = SalesOrderItem.objects.create(order=new_order, **item_data)
            total += item.amount

        new_order.total_amount = total
        new_order.save()

    def update(self, instance, validated_data):
        from apps.inventory.models import Inventory, Warehouse
        items_data = validated_data.pop('items', None)

        if items_data is not None:
            # 先回滚旧库存和旧订单数量
            order = instance.order
            warehouse_name = instance.warehouse
            warehouse = Warehouse.objects.filter(name=warehouse_name).first()
            for old_item in instance.items.all():
                material_name = old_item.material_name
                spec = old_item.spec or ''
                out_qty = old_item.quantity or Decimal('0')
                if warehouse:
                    inv = Inventory.objects.filter(warehouse=warehouse, material_name=material_name, spec=spec).first()
                    if inv:
                        inv.qty += out_qty
                        inv.save()
                if order:
                    order_item = SalesOrderItem.objects.filter(
                        order=order, material_name=material_name, spec=spec
                    ).first()
                    if order_item:
                        order_item.delivered_qty = max(Decimal('0'), (order_item.delivered_qty or Decimal('0')) - out_qty)
                        order_item.save()

            instance.items.all().delete()
            for item_data in items_data:
                SalesOutStockItem.objects.create(stock=instance, **item_data)
                # 重新扣减库存
                material_name = item_data.get('material_name')
                spec = item_data.get('spec') or ''
                out_qty = item_data.get('quantity') or Decimal('0')
                if warehouse and material_name and out_qty > 0:
                    inv, created = Inventory.objects.get_or_create(
                        warehouse=warehouse,
                        material_name=material_name,
                        spec=spec,
                        defaults={'unit': item_data.get('unit', '件'), 'qty': 0}
                    )
                    if inv.qty < out_qty:
                        raise serializers.ValidationError(f'物料 "{material_name}" 库存不足，当前库存 {inv.qty}')
                    inv.qty -= out_qty
                    inv.save()
                if order and material_name and out_qty > 0:
                    order_item = SalesOrderItem.objects.filter(
                        order=order, material_name=material_name, spec=spec
                    ).first()
                    if order_item:
                        order_item.delivered_qty = (order_item.delivered_qty or Decimal('0')) + out_qty
                        order_item.save()

            # 重新计算订单状态
            if order:
                self._update_order_status(order, order.customer)

        instance = super().update(instance, validated_data)
        return instance


class SalesReturnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReturnItem
        fields = '__all__'
        extra_kwargs = {
            'return_order': {'read_only': True},
        }


class SalesReturnSerializer(serializers.ModelSerializer):
    items = SalesReturnItemSerializer(many=True, required=False)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = SalesReturn
        fields = '__all__'

    def create(self, validated_data):
        from apps.inventory.models import Inventory, Warehouse
        items_data = validated_data.pop('items', [])
        return_obj = SalesReturn.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            item = SalesReturnItem.objects.create(return_order=return_obj, **item_data)
            total += item.amount
            # 退货增加库存
            material_name = item_data.get('material_name')
            spec = item_data.get('spec') or ''
            qty = item_data.get('quantity') or Decimal('0')
            if material_name and qty > 0:
                # 默认入到第一个仓库，或保持与出库相同的仓库逻辑
                warehouse = Warehouse.objects.filter(is_active=True).first()
                if warehouse:
                    inv, created = Inventory.objects.get_or_create(
                        warehouse=warehouse,
                        material_name=material_name,
                        spec=spec,
                        defaults={'unit': item_data.get('unit', '件'), 'qty': 0}
                    )
                    inv.qty += qty
                    inv.save()
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


class SalesPickingListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesPickingListItem
        fields = '__all__'
        extra_kwargs = {
            'picking_list': {'read_only': True},
        }


class SalesPickingListSerializer(serializers.ModelSerializer):
    items = SalesPickingListItemSerializer(many=True, required=False)
    order_no = serializers.CharField(source='order.order_no', read_only=True)
    customer_name = serializers.CharField(source='order.customer.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    picker_name = serializers.CharField(source='picker.username', read_only=True)

    class Meta:
        model = SalesPickingList
        fields = '__all__'
        extra_kwargs = {
            'picking_no': {'required': False},
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        if not validated_data.get('picking_no'):
            validated_data['picking_no'] = generate_order_no('JH', model=SalesPickingList, field='picking_no')
        picking = SalesPickingList.objects.create(**validated_data)
        for item_data in items_data:
            SalesPickingListItem.objects.create(picking_list=picking, **item_data)
        return picking

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                SalesPickingListItem.objects.create(picking_list=instance, **item_data)
        return instance
