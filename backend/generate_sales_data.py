#!/usr/bin/env python
"""
销售管理模块测试数据生成脚本
生成：客户、销售订单、销售订单明细、销售出库单、销售出库明细、销售退货单、销售退货明细
"""
import os
import sys
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import transaction
from apps.sales.models import (
    Customer, SalesOrder, SalesOrderItem,
    SalesOutStock, SalesOutStockItem,
    SalesReturn, SalesReturnItem
)
from apps.system.models import User


# ========== 配置 ==========
NUM_CUSTOMERS = 15          # 客户数量
NUM_ORDERS = 50             # 销售订单数量
NUM_RETURNS = 8             # 退货单数量

random.seed(42)

# 基础数据
COMPANY_PREFIXES = ['华东', '华南', '华北', '西南', '华中', '东北', '西北', '东南']
COMPANY_SUFFIXES = ['科技', '贸易', '实业', '电子', '机械', '纺织', '化工', '食品', '建材', '物流']
INDUSTRIES = ['电子科技', '机械制造', '纺织服装', '化工材料', '食品饮料', '建筑材料', '物流运输', '医疗器械']
MATERIALS = [
    ('智能控制器', 'KC-2024A', '套'),
    ('伺服电机', 'SM-750W', '台'),
    ('PLC模块', 'S7-1200', '个'),
    ('触摸屏', 'TPC7062Ti', '台'),
    ('变频器', 'VFD-M', '台'),
    ('传感器', 'E3F-DS30C4', '支'),
    ('气缸', 'SC50×100', '只'),
    ('电磁阀', '4V210-08', '个'),
    ('轴承', '6205-2RS', '套'),
    ('减速机', 'NMRV050', '台'),
    ('链条', '08B-1', '米'),
    ('皮带轮', 'SPB160', '个'),
    ('润滑油', 'L-HM46', '桶'),
    ('密封圈', 'Φ50×3.55', '个'),
    ('继电器', 'MY2NJ', '个'),
]
WAREHOUSES = ['默认仓库', '华东仓', '华南仓', '华北仓', '西南仓']
SALESMEN = list(User.objects.filter(is_active=True))
if not SALESMEN:
    raise RuntimeError('系统中没有可用用户，请先创建用户')


def random_date(start_days_ago=90, end_days_ago=0):
    """生成随机日期"""
    base = datetime.now().date()
    delta = random.randint(end_days_ago, start_days_ago)
    return base - timedelta(days=delta)


def generate_order_no(prefix, seq):
    """生成编号"""
    return f"{prefix}{datetime.now().strftime('%Y%m')}{seq:04d}"


def create_customers():
    """生成客户数据"""
    print('>>> 生成客户数据...')
    customers = []
    existing_codes = set(Customer.objects.values_list('code', flat=True))
    for i in range(NUM_CUSTOMERS):
        prefix = random.choice(COMPANY_PREFIXES)
        suffix = random.choice(COMPANY_SUFFIXES)
        name = f"{prefix}{suffix}有限公司"
        code = f"CUST{random.randint(10000, 99999)}"
        while code in existing_codes:
            code = f"CUST{random.randint(10000, 99999)}"
        existing_codes.add(code)

        customer = Customer(
            name=name,
            code=code,
            contact=f"联系人{random.randint(1, 99)}",
            phone=f"13{random.randint(100000000, 999999999)}",
            email=f"contact@{code.lower()}.com",
            address=f"{random.choice(COMPANY_PREFIXES)}市{random.choice(['高新', '经济', '产业'])}区{random.randint(1, 999)}号",
            industry=random.choice(INDUSTRIES),
            level=random.choice(['A', 'B', 'C', 'D']),
            credit_limit=Decimal(random.randint(10, 500)) * 10000,
            tax_no=f"91{random.randint(100000000000, 999999999999)}",
            bank_info=f"中国工商银行 {random.randint(100000000000, 999999999999)}"
        )
        customers.append(customer)
    Customer.objects.bulk_create(customers)
    created = list(Customer.objects.all())
    print(f'    已创建 {len(created)} 个客户')
    return created


def create_sales_orders(customers):
    """生成销售订单及明细"""
    print('>>> 生成销售订单及明细...')
    orders = []
    items = []
    order_seq = 1

    for i in range(NUM_ORDERS):
        status = random.choices(
            ['draft', 'confirmed', 'partial', 'completed', 'cancelled'],
            weights=[15, 25, 20, 30, 10]
        )[0]
        customer = random.choice(customers)
        order_date = random_date(60, 0)
        delivery_date = order_date + timedelta(days=random.randint(3, 30)) if random.random() > 0.1 else None

        order = SalesOrder(
            order_no=generate_order_no('SO', order_seq),
            customer=customer,
            order_date=order_date,
            delivery_date=delivery_date,
            status=status,
            total_amount=Decimal('0'),
            salesman=random.choice(SALESMEN) if random.random() > 0.2 else None,
            remark=random.choice(['', '急单，请优先处理', '客户要求分批交货', '账期30天', '含运费', ''])
        )
        orders.append(order)
        order_seq += 1

    SalesOrder.objects.bulk_create(orders)
    orders = list(SalesOrder.objects.all().order_by('id'))

    # 生成明细
    for order in orders:
        num_items = random.randint(1, 5)
        order_total = Decimal('0')
        order_delivered = Decimal('0')
        for j in range(num_items):
            mat = random.choice(MATERIALS)
            qty = Decimal(random.randint(10, 5000))
            price = Decimal(random.randint(10, 50000)) / Decimal('100')
            amount = (qty * price).quantize(Decimal('0.01'))
            order_total += amount

            # 根据状态设置已出库数量
            if order.status == 'draft':
                delivered = Decimal('0')
            elif order.status == 'confirmed':
                delivered = Decimal('0')
            elif order.status == 'cancelled':
                delivered = Decimal('0')
            elif order.status == 'completed':
                delivered = qty
                order_delivered += qty
            else:  # partial
                delivered = (qty * Decimal(random.randint(10, 80)) / Decimal('100')).quantize(Decimal('0.0001'))
                order_delivered += delivered

            items.append(SalesOrderItem(
                order=order,
                material_name=mat[0],
                spec=mat[1],
                quantity=qty,
                unit=mat[2],
                price=price,
                amount=amount,
                delivered_qty=delivered,
                remark=''
            ))

        order.total_amount = order_total

    SalesOrderItem.objects.bulk_create(items)
    # 批量更新订单总金额
    from django.db.models import F, Sum
    # 由于 bulk_update 对 total_amount 支持有限，这里逐个更新
    for order in orders:
        order.save(update_fields=['total_amount'])

    print(f'    已创建 {len(orders)} 个销售订单，{len(items)} 条明细')
    return orders


def create_sales_outstock(orders):
    """生成销售出库单及明细"""
    print('>>> 生成销售出库单及明细...')
    stock_orders = [o for o in orders if o.status in ('partial', 'completed')]
    stocks = []
    stock_items = []
    stock_seq = 1

    for order in stock_orders:
        items = list(order.items.all())
        # 已完成：一次性全部出库；部分出库：可能分多次
        if order.status == 'completed':
            stock = SalesOutStock(
                stock_no=generate_order_no('CK', stock_seq),
                order=order,
                stock_date=order.order_date + timedelta(days=random.randint(1, 10)),
                warehouse=random.choice(WAREHOUSES),
                operator=random.choice(SALESMEN),
                remark=''
            )
            stocks.append(stock)
            stock_seq += 1

            for it in items:
                stock_items.append(SalesOutStockItem(
                    stock=stock,
                    material_name=it.material_name,
                    spec=it.spec,
                    quantity=it.quantity,
                    unit=it.unit,
                    remark=''
                ))
        else:
            # 部分出库：分 1-2 次出库
            num_batches = random.randint(1, 2)
            for b in range(num_batches):
                stock = SalesOutStock(
                    stock_no=generate_order_no('CK', stock_seq),
                    order=order,
                    stock_date=order.order_date + timedelta(days=random.randint(1, 15)),
                    warehouse=random.choice(WAREHOUSES),
                    operator=random.choice(SALESMEN),
                    remark='分批出库' if b > 0 else ''
                )
                stocks.append(stock)
                stock_seq += 1

                for it in items:
                    if b == 0:
                        out_qty = (it.quantity * Decimal(random.randint(30, 70)) / Decimal('100')).quantize(Decimal('0.0001'))
                    else:
                        out_qty = (it.quantity - it.delivered_qty).quantize(Decimal('0.0001')) if it.delivered_qty else Decimal('0')
                        out_qty = max(Decimal('0'), out_qty)

                    if out_qty > 0:
                        stock_items.append(SalesOutStockItem(
                            stock=stock,
                            material_name=it.material_name,
                            spec=it.spec,
                            quantity=out_qty,
                            unit=it.unit,
                            remark=''
                        ))

    SalesOutStock.objects.bulk_create(stocks)
    # 重新获取 stocks 以关联 items
    stocks = list(SalesOutStock.objects.all().order_by('id'))
    # 关联 stock_items 到正确的 stock 对象
    # 由于 bulk_create 后 items 的 stock 引用还是旧对象，需要重新映射
    # 简单做法：逐个创建
    print(f'    已创建 {len(stocks)} 个出库单')

    # 逐个创建出库明细，确保外键正确
    for stock in stocks:
        # 找到匹配这个 stock 的 items（根据 stock_no 不太可能）
        pass

    # 更简单的做法：重新用循环创建
    SalesOutStockItem.objects.all().delete()
    SalesOutStock.objects.all().delete()
    stocks = []
    stock_seq = 1

    for order in stock_orders:
        items = list(order.items.all())
        if order.status == 'completed':
            stock = SalesOutStock.objects.create(
                stock_no=generate_order_no('CK', stock_seq),
                order=order,
                stock_date=order.order_date + timedelta(days=random.randint(1, 10)),
                warehouse=random.choice(WAREHOUSES),
                operator=random.choice(SALESMEN),
                remark=''
            )
            stock_seq += 1
            for it in items:
                SalesOutStockItem.objects.create(
                    stock=stock,
                    material_name=it.material_name,
                    spec=it.spec,
                    quantity=it.quantity,
                    unit=it.unit,
                    remark=''
                )
        else:
            num_batches = random.randint(1, 2)
            for b in range(num_batches):
                stock = SalesOutStock.objects.create(
                    stock_no=generate_order_no('CK', stock_seq),
                    order=order,
                    stock_date=order.order_date + timedelta(days=random.randint(1, 15)),
                    warehouse=random.choice(WAREHOUSES),
                    operator=random.choice(SALESMEN),
                    remark='分批出库' if b > 0 else ''
                )
                stock_seq += 1
                for it in items:
                    if b == 0:
                        out_qty = (it.quantity * Decimal(random.randint(30, 70)) / Decimal('100')).quantize(Decimal('0.0001'))
                    else:
                        remaining = it.quantity - it.delivered_qty
                        out_qty = (remaining * Decimal(random.randint(0, 50)) / Decimal('100')).quantize(Decimal('0.0001'))
                        out_qty = max(Decimal('0'), out_qty)
                    if out_qty > 0:
                        SalesOutStockItem.objects.create(
                            stock=stock,
                            material_name=it.material_name,
                            spec=it.spec,
                            quantity=out_qty,
                            unit=it.unit,
                            remark=''
                        )

    print(f'    出库单创建完成，共 {SalesOutStock.objects.count()} 单')


def create_sales_returns(customers):
    """生成销售退货单及明细"""
    print('>>> 生成销售退货单及明细...')
    returns = []
    return_items_list = []
    return_seq = 1

    completed_orders = list(SalesOrder.objects.filter(status='completed'))
    if not completed_orders:
        print('    没有已完成的订单，跳过退货单生成')
        return

    for i in range(min(NUM_RETURNS, len(completed_orders))):
        order = random.choice(completed_orders)
        completed_orders.remove(order)
        customer = order.customer

        ret = SalesReturn.objects.create(
            return_no=generate_order_no('TH', return_seq),
            customer=customer,
            return_date=order.order_date + timedelta(days=random.randint(15, 45)),
            total_amount=Decimal('0'),
            operator=random.choice(SALESMEN),
            remark=random.choice(['', '质量问题', '数量多发', '客户取消订单', ''])
        )
        return_seq += 1

        # 从订单中随机选几个物料退货
        order_items = list(order.items.all())
        selected = random.sample(order_items, min(random.randint(1, 3), len(order_items)))
        total = Decimal('0')
        for it in selected:
            qty = (it.quantity * Decimal(random.randint(5, 30)) / Decimal('100')).quantize(Decimal('0.0001'))
            qty = max(Decimal('1'), qty)
            price = it.price
            amount = (qty * price).quantize(Decimal('0.01'))
            total += amount
            SalesReturnItem.objects.create(
                return_order=ret,
                material_name=it.material_name,
                spec=it.spec,
                quantity=qty,
                unit=it.unit,
                price=price,
                amount=amount,
                remark=''
            )
        ret.total_amount = total
        ret.save()

    print(f'    已创建 {SalesReturn.objects.count()} 个退货单')


def print_summary():
    print('\n' + '='*50)
    print('数据生成完成！统计如下：')
    print('='*50)
    print(f"  客户数量:        {Customer.objects.count()}")
    print(f"  销售订单:        {SalesOrder.objects.count()}")
    print(f"  销售订单明细:    {SalesOrderItem.objects.count()}")
    print(f"  销售出库单:      {SalesOutStock.objects.count()}")
    print(f"  销售出库明细:    {SalesOutStockItem.objects.count()}")
    print(f"  销售退货单:      {SalesReturn.objects.count()}")
    print(f"  销售退货明细:    {SalesReturnItem.objects.count()}")
    print('='*50)
    print('\n各状态订单分布:')
    for status, label in SalesOrder.STATUS_CHOICES:
        cnt = SalesOrder.objects.filter(status=status).count()
        print(f"  {label}: {cnt}")


def main():
    print('开始生成销售管理模块测试数据...\n')
    # 清理已有数据（可选）
    # SalesReturnItem.objects.all().delete()
    # SalesReturn.objects.all().delete()
    # SalesOutStockItem.objects.all().delete()
    # SalesOutStock.objects.all().delete()
    # SalesOrderItem.objects.all().delete()
    # SalesOrder.objects.all().delete()
    # Customer.objects.all().delete()

    customers = create_customers()
    orders = create_sales_orders(customers)
    create_sales_outstock(orders)
    create_sales_returns(customers)
    print_summary()
    print('\n[OK] 全部完成！')


if __name__ == '__main__':
    main()
