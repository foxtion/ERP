"""
初始化财务管理-往来单位及对账往来测试数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from apps.finance.models import Counterparty, ReceivablePayable, PaymentReceipt, Settlement

User = get_user_model()


def generate_doc_no(prefix, seq):
    date_str = date.today().strftime('%Y%m%d')
    return f"{prefix}{date_str}-{seq:03d}"


def run():
    print("开始生成往来单位及对账往来测试数据...")

    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("未找到管理员用户，跳过数据生成")
        return

    # 1. 创建往来单位
    counterparties_data = [
        {'name': '华为技术有限公司', 'type': 'customer', 'contact': '张经理', 'phone': '0755-88888888'},
        {'name': '深圳市腾讯计算机系统有限公司', 'type': 'customer', 'contact': '李总监', 'phone': '0755-86013388'},
        {'name': '阿里巴巴（中国）有限公司', 'type': 'both', 'contact': '王主管', 'phone': '0571-85022088'},
        {'name': '北京京东世纪贸易有限公司', 'type': 'customer', 'contact': '刘经理', 'phone': '010-89127000'},
        {'name': '上海宝钢集团有限公司', 'type': 'supplier', 'contact': '陈主任', 'phone': '021-26647000'},
        {'name': '中国石油化工股份有限公司', 'type': 'supplier', 'contact': '赵部长', 'phone': '010-59960000'},
        {'name': '联想（北京）有限公司', 'type': 'both', 'contact': '孙经理', 'phone': '010-58868888'},
        {'name': '美的集团股份有限公司', 'type': 'supplier', 'contact': '周总监', 'phone': '0757-26606888'},
    ]

    cp_map = {}
    for i, data in enumerate(counterparties_data):
        cp, created = Counterparty.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        cp_map[data['name']] = cp
        action = '创建' if created else '已存在'
        print(f"  {action}往来单位: {cp.name} ({cp.get_type_display()})")

    # 2. 创建应收单据
    receivable_data = [
        ('华为技术有限公司', Decimal('50000.00'), 'receivable', 30),
        ('深圳市腾讯计算机系统有限公司', Decimal('80000.00'), 'receivable', 45),
        ('阿里巴巴（中国）有限公司', Decimal('120000.00'), 'receivable', 60),
        ('北京京东世纪贸易有限公司', Decimal('35000.00'), 'receivable', 15),
        ('联想（北京）有限公司', Decimal('60000.00'), 'receivable', 30),
    ]

    receivables = []
    for i, (name, amount, doc_type, due_days) in enumerate(receivable_data):
        cp = cp_map[name]
        rp = ReceivablePayable.objects.create(
            doc_no=generate_doc_no('YS', i + 1),
            doc_type=doc_type,
            counterparty=name,
            counterparty_obj=cp,
            doc_date=date.today() - timedelta(days=i * 5 + 10),
            due_date=date.today() + timedelta(days=due_days - i * 5),
            amount=amount,
            paid_amount=Decimal('0'),
            status='unpaid',
            source_type='sales_order',
            source_no=f'SO202501{i+1:02d}',
            remark=f'销售订单应收款 {i + 1}'
        )
        receivables.append(rp)
        print(f"  创建应收单: {rp.doc_no} - {name} - {rp.amount}")

    # 3. 创建应付单据
    payable_data = [
        ('上海宝钢集团有限公司', Decimal('45000.00'), 'payable', 20),
        ('中国石油化工股份有限公司', Decimal('72000.00'), 'payable', 30),
        ('阿里巴巴（中国）有限公司', Decimal('55000.00'), 'payable', 25),
        ('美的集团股份有限公司', Decimal('38000.00'), 'payable', 15),
        ('联想（北京）有限公司', Decimal('48000.00'), 'payable', 20),
    ]

    payables = []
    for i, (name, amount, doc_type, due_days) in enumerate(payable_data):
        cp = cp_map[name]
        rp = ReceivablePayable.objects.create(
            doc_no=generate_doc_no('YF', i + 1),
            doc_type=doc_type,
            counterparty=name,
            counterparty_obj=cp,
            doc_date=date.today() - timedelta(days=i * 3 + 5),
            due_date=date.today() + timedelta(days=due_days - i * 3),
            amount=amount,
            paid_amount=Decimal('0'),
            status='unpaid',
            source_type='purchase_order',
            source_no=f'PO202501{i+1:02d}',
            remark=f'采购订单应付款 {i + 1}'
        )
        payables.append(rp)
        print(f"  创建应付单: {rp.doc_no} - {name} - {rp.amount}")

    # 4. 部分结清的应收（华为）
    partial_rp = ReceivablePayable.objects.create(
        doc_no=generate_doc_no('YS', 10),
        doc_type='receivable',
        counterparty='华为技术有限公司',
        counterparty_obj=cp_map['华为技术有限公司'],
        doc_date=date.today() - timedelta(days=30),
        due_date=date.today() - timedelta(days=5),
        amount=Decimal('100000.00'),
        paid_amount=Decimal('30000.00'),
        status='partial',
        source_type='sales_order',
        source_no='SO202501010',
        remark='部分结清应收款'
    )
    print(f"  创建部分结清应收单: {partial_rp.doc_no}")

    # 5. 已结清的应收
    paid_rp = ReceivablePayable.objects.create(
        doc_no=generate_doc_no('YS', 11),
        doc_type='receivable',
        counterparty='北京京东世纪贸易有限公司',
        counterparty_obj=cp_map['北京京东世纪贸易有限公司'],
        doc_date=date.today() - timedelta(days=60),
        due_date=date.today() - timedelta(days=30),
        amount=Decimal('25000.00'),
        paid_amount=Decimal('25000.00'),
        status='paid',
        source_type='sales_order',
        source_no='SO202501011',
        remark='已结清应收款'
    )
    print(f"  创建已结清应收单: {paid_rp.doc_no}")

    # 6. 创建收款单
    receipts = []
    receipt_data = [
        ('华为技术有限公司', Decimal('30000.00')),
        ('深圳市腾讯计算机系统有限公司', Decimal('25000.00')),
        ('阿里巴巴（中国）有限公司', Decimal('40000.00')),
    ]
    for i, (name, amount) in enumerate(receipt_data):
        cp = cp_map[name]
        pm = PaymentReceipt.objects.create(
            doc_no=generate_doc_no('SK', i + 1),
            doc_type='receipt',
            counterparty=name,
            counterparty_obj=cp,
            doc_date=date.today() - timedelta(days=i * 2 + 1),
            amount=amount,
            payment_method='bank_transfer',
            bank_account='6222021234567890123',
            operator=admin,
            remark=f'银行转账收款 {i + 1}'
        )
        receipts.append(pm)
        print(f"  创建收款单: {pm.doc_no} - {name} - {pm.amount}")

    # 7. 创建付款单
    payments = []
    payment_data = [
        ('上海宝钢集团有限公司', Decimal('20000.00')),
        ('中国石油化工股份有限公司', Decimal('35000.00')),
        ('美的集团股份有限公司', Decimal('15000.00')),
    ]
    for i, (name, amount) in enumerate(payment_data):
        cp = cp_map[name]
        pm = PaymentReceipt.objects.create(
            doc_no=generate_doc_no('FK', i + 1),
            doc_type='payment',
            counterparty=name,
            counterparty_obj=cp,
            doc_date=date.today() - timedelta(days=i * 2 + 1),
            amount=amount,
            payment_method='bank_transfer',
            bank_account='6222029876543210987',
            operator=admin,
            remark=f'银行转账付款 {i + 1}'
        )
        payments.append(pm)
        print(f"  创建付款单: {pm.doc_no} - {name} - {pm.amount}")

    # 8. 核销记录：收款核销应收
    if receipts and receivables:
        # 收款1 核销 华为部分结清
        settlement1 = Settlement.objects.create(
            payment_receipt=receipts[0],
            receivable_payable=partial_rp,
            amount=Decimal('20000.00')
        )
        partial_rp.paid_amount = Decimal('50000.00')
        partial_rp.status = 'partial'
        partial_rp.save()
        print(f"  创建核销记录: {settlement1}")

        # 收款2 核销 腾讯应收
        settlement2 = Settlement.objects.create(
            payment_receipt=receipts[1],
            receivable_payable=receivables[1],
            amount=Decimal('15000.00')
        )
        receivables[1].paid_amount = Decimal('15000.00')
        receivables[1].status = 'partial'
        receivables[1].save()
        print(f"  创建核销记录: {settlement2}")

    # 9. 付款核销应付
    if payments and payables:
        settlement3 = Settlement.objects.create(
            payment_receipt=payments[0],
            receivable_payable=payables[0],
            amount=Decimal('10000.00')
        )
        payables[0].paid_amount = Decimal('10000.00')
        payables[0].status = 'partial'
        payables[0].save()
        print(f"  创建核销记录: {settlement3}")

        settlement4 = Settlement.objects.create(
            payment_receipt=payments[2],
            receivable_payable=payables[3],
            amount=Decimal('8000.00')
        )
        payables[3].paid_amount = Decimal('8000.00')
        payables[3].status = 'partial'
        payables[3].save()
        print(f"  创建核销记录: {settlement4}")

    print("\n往来单位及对账往来测试数据生成完成！")
    print(f"  往来单位: {Counterparty.objects.count()} 条")
    print(f"  应收单据: {ReceivablePayable.objects.filter(doc_type='receivable').count()} 条")
    print(f"  应付单据: {ReceivablePayable.objects.filter(doc_type='payable').count()} 条")
    print(f"  收款单: {PaymentReceipt.objects.filter(doc_type='receipt').count()} 条")
    print(f"  付款单: {PaymentReceipt.objects.filter(doc_type='payment').count()} 条")
    print(f"  核销记录: {Settlement.objects.count()} 条")


if __name__ == '__main__':
    run()
