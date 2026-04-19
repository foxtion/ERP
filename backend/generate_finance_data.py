"""
初始化财务管理-应收应付测试数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from apps.finance.models import ReceivablePayable, PaymentReceipt, Settlement

User = get_user_model()


def generate_doc_no(prefix, seq):
    date_str = date.today().strftime('%Y%m%d')
    return f"{prefix}{date_str}-{seq:03d}"


def run():
    print("开始生成财务应收应付测试数据...")

    # 获取管理员用户
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("未找到管理员用户，跳过数据生成")
        return

    # 往来单位
    customers = ['华为技术有限公司', '深圳市腾讯计算机系统有限公司', '阿里巴巴（中国）有限公司', '北京京东世纪贸易有限公司']
    suppliers = ['上海宝钢集团有限公司', '中国石油化工股份有限公司', '联想（北京）有限公司', '美的集团股份有限公司']

    # 1. 创建应收单据
    receivables = []
    for i, customer in enumerate(customers):
        rp = ReceivablePayable.objects.create(
            doc_no=generate_doc_no('YS', i + 1),
            doc_type='receivable',
            counterparty=customer,
            doc_date=date.today() - timedelta(days=i * 5),
            due_date=date.today() + timedelta(days=30 - i * 10),
            amount=Decimal('50000.00') + Decimal(str(i * 10000)),
            paid_amount=Decimal('0'),
            status='unpaid',
            source_type='sales_order',
            source_no=f'SO2025010{i + 1:02d}',
            remark=f'销售订单应收款 {i + 1}'
        )
        receivables.append(rp)
        print(f"  创建应收单: {rp.doc_no} - {customer} - {rp.amount}")

    # 2. 创建应付单据
    payables = []
    for i, supplier in enumerate(suppliers):
        rp = ReceivablePayable.objects.create(
            doc_no=generate_doc_no('YF', i + 1),
            doc_type='payable',
            counterparty=supplier,
            doc_date=date.today() - timedelta(days=i * 3),
            due_date=date.today() + timedelta(days=15 - i * 5),
            amount=Decimal('30000.00') + Decimal(str(i * 5000)),
            paid_amount=Decimal('0'),
            status='unpaid',
            source_type='purchase_order',
            source_no=f'PO2025010{i + 1:02d}',
            remark=f'采购订单应付款 {i + 1}'
        )
        payables.append(rp)
        print(f"  创建应付单: {rp.doc_no} - {supplier} - {rp.amount}")

    # 3. 创建已部分结清的应收（模拟历史数据）
    partial_receivable = ReceivablePayable.objects.create(
        doc_no=generate_doc_no('YS', 10),
        doc_type='receivable',
        counterparty='华为技术有限公司',
        doc_date=date.today() - timedelta(days=20),
        due_date=date.today() - timedelta(days=5),  # 已逾期
        amount=Decimal('100000.00'),
        paid_amount=Decimal('30000.00'),
        status='partial',
        source_type='sales_order',
        source_no='SO202501010',
        remark='部分结清应收款'
    )
    print(f"  创建部分结清应收单: {partial_receivable.doc_no}")

    # 4. 创建收款单
    receipts = []
    for i, customer in enumerate(customers[:2]):
        pm = PaymentReceipt.objects.create(
            doc_no=generate_doc_no('SK', i + 1),
            doc_type='receipt',
            counterparty=customer,
            doc_date=date.today() - timedelta(days=i * 2),
            amount=Decimal('20000.00') + Decimal(str(i * 5000)),
            payment_method='bank_transfer',
            bank_account='6222021234567890123',
            operator=admin,
            remark=f'银行转账收款 {i + 1}'
        )
        receipts.append(pm)
        print(f"  创建收款单: {pm.doc_no} - {customer} - {pm.amount}")

    # 5. 创建付款单
    payments = []
    for i, supplier in enumerate(suppliers[:2]):
        pm = PaymentReceipt.objects.create(
            doc_no=generate_doc_no('FK', i + 1),
            doc_type='payment',
            counterparty=supplier,
            doc_date=date.today() - timedelta(days=i * 2),
            amount=Decimal('15000.00') + Decimal(str(i * 3000)),
            payment_method='bank_transfer',
            bank_account='6222029876543210987',
            operator=admin,
            remark=f'银行转账付款 {i + 1}'
        )
        payments.append(pm)
        print(f"  创建付款单: {pm.doc_no} - {supplier} - {pm.amount}")

    # 6. 创建核销记录（收款核销应收）
    if receipts and receivables:
        settlement = Settlement.objects.create(
            payment_receipt=receipts[0],
            receivable_payable=partial_receivable,
            amount=Decimal('20000.00')
        )
        partial_receivable.paid_amount = Decimal('50000.00')
        if partial_receivable.paid_amount >= partial_receivable.amount:
            partial_receivable.status = 'paid'
        else:
            partial_receivable.status = 'partial'
        partial_receivable.save()
        print(f"  创建核销记录: {settlement}")

    # 7. 创建另一个核销记录
    if len(receipts) > 1 and receivables:
        settlement2 = Settlement.objects.create(
            payment_receipt=receipts[1],
            receivable_payable=receivables[0],
            amount=Decimal('15000.00')
        )
        receivables[0].paid_amount = Decimal('15000.00')
        receivables[0].status = 'partial'
        receivables[0].save()
        print(f"  创建核销记录: {settlement2}")

    # 8. 创建付款核销应付
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

    print("\n财务应收应付测试数据生成完成！")
    print(f"  应收单据: {ReceivablePayable.objects.filter(doc_type='receivable').count()} 条")
    print(f"  应付单据: {ReceivablePayable.objects.filter(doc_type='payable').count()} 条")
    print(f"  收款单: {PaymentReceipt.objects.filter(doc_type='receipt').count()} 条")
    print(f"  付款单: {PaymentReceipt.objects.filter(doc_type='payment').count()} 条")
    print(f"  核销记录: {Settlement.objects.count()} 条")


if __name__ == '__main__':
    run()
