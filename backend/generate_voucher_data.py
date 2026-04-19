"""
初始化财务管理-记账凭证测试数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from apps.finance.models import AccountSubject, Voucher, VoucherItem

User = get_user_model()


def ensure_subjects():
    """确保有基础的会计科目"""
    subjects_data = [
        # 资产类
        ('1001', '库存现金', 'asset'),
        ('1002', '银行存款', 'asset'),
        ('1122', '应收账款', 'asset'),
        ('1403', '原材料', 'asset'),
        ('1601', '固定资产', 'asset'),
        # 负债类
        ('2202', '应付账款', 'liability'),
        ('2211', '应付职工薪酬', 'liability'),
        # 所有者权益
        ('4001', '实收资本', 'equity'),
        ('4103', '本年利润', 'equity'),
        # 收入
        ('6001', '主营业务收入', 'income'),
        ('6051', '其他业务收入', 'income'),
        # 费用
        ('6401', '主营业务成本', 'expense'),
        ('6602', '管理费用', 'expense'),
        ('6603', '财务费用', 'expense'),
    ]
    created = []
    for code, name, category in subjects_data:
        obj, _ = AccountSubject.objects.get_or_create(
            code=code,
            defaults={'name': name, 'category': category, 'is_active': True}
        )
        created.append(obj)
    return created


def run():
    print("开始生成记账凭证测试数据...")

    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("未找到管理员用户，跳过数据生成")
        return

    subjects = ensure_subjects()
    if not subjects:
        print("无法创建会计科目")
        return

    subject_map = {s.code: s for s in subjects}

    # 凭证1: 销售商品（已审核）
    v1 = Voucher.objects.create(
        voucher_no='PZ20260419-001',
        voucher_date=date.today(),
        status='audited',
        preparer=admin,
        auditor=admin,
        remark='销售商品收入确认'
    )
    VoucherItem.objects.create(voucher=v1, line_no=1, subject=subject_map['1122'], summary='确认应收账款', debit=Decimal('117000.00'), credit=Decimal('0'))
    VoucherItem.objects.create(voucher=v1, line_no=2, subject=subject_map['6001'], summary='确认主营业务收入', debit=Decimal('0'), credit=Decimal('100000.00'))
    v1.total_debit = Decimal('117000.00')
    v1.total_credit = Decimal('100000.00')
    v1.save()
    print(f"  创建凭证: {v1.voucher_no} - 销售商品")

    # 凭证2: 采购原材料（草稿）
    v2 = Voucher.objects.create(
        voucher_no='PZ20260419-002',
        voucher_date=date.today() - timedelta(days=1),
        status='draft',
        preparer=admin,
        remark='采购原材料入库'
    )
    VoucherItem.objects.create(voucher=v2, line_no=1, subject=subject_map['1403'], summary='原材料入库', debit=Decimal('50000.00'), credit=Decimal('0'))
    VoucherItem.objects.create(voucher=v2, line_no=2, subject=subject_map['2202'], summary='应付账款', debit=Decimal('0'), credit=Decimal('50000.00'))
    v2.total_debit = Decimal('50000.00')
    v2.total_credit = Decimal('50000.00')
    v2.save()
    print(f"  创建凭证: {v2.voucher_no} - 采购原材料")

    # 凭证3: 支付工资（已审核）
    v3 = Voucher.objects.create(
        voucher_no='PZ20260419-003',
        voucher_date=date.today() - timedelta(days=2),
        status='audited',
        preparer=admin,
        auditor=admin,
        remark='支付上月工资'
    )
    VoucherItem.objects.create(voucher=v3, line_no=1, subject=subject_map['2211'], summary='发放工资', debit=Decimal('80000.00'), credit=Decimal('0'))
    VoucherItem.objects.create(voucher=v3, line_no=2, subject=subject_map['1002'], summary='银行存款支付', debit=Decimal('0'), credit=Decimal('80000.00'))
    v3.total_debit = Decimal('80000.00')
    v3.total_credit = Decimal('80000.00')
    v3.save()
    print(f"  创建凭证: {v3.voucher_no} - 支付工资")

    # 凭证4: 提现（草稿）
    v4 = Voucher.objects.create(
        voucher_no='PZ20260419-004',
        voucher_date=date.today() - timedelta(days=3),
        status='draft',
        preparer=admin,
        remark='从银行提取现金'
    )
    VoucherItem.objects.create(voucher=v4, line_no=1, subject=subject_map['1001'], summary='现金增加', debit=Decimal('20000.00'), credit=Decimal('0'))
    VoucherItem.objects.create(voucher=v4, line_no=2, subject=subject_map['1002'], summary='银行存款减少', debit=Decimal('0'), credit=Decimal('20000.00'))
    v4.total_debit = Decimal('20000.00')
    v4.total_credit = Decimal('20000.00')
    v4.save()
    print(f"  创建凭证: {v4.voucher_no} - 提现")

    # 凭证5: 费用报销（已作废）
    v5 = Voucher.objects.create(
        voucher_no='PZ20260419-005',
        voucher_date=date.today() - timedelta(days=5),
        status='draft',
        preparer=admin,
        remark='管理费用报销（已作废演示）'
    )
    VoucherItem.objects.create(voucher=v5, line_no=1, subject=subject_map['6602'], summary='办公费用', debit=Decimal('3000.00'), credit=Decimal('0'))
    VoucherItem.objects.create(voucher=v5, line_no=2, subject=subject_map['1001'], summary='现金支付', debit=Decimal('0'), credit=Decimal('3000.00'))
    v5.total_debit = Decimal('3000.00')
    v5.total_credit = Decimal('3000.00')
    v5.save()
    print(f"  创建凭证: {v5.voucher_no} - 费用报销")

    print(f"\n记账凭证测试数据生成完成！共 {Voucher.objects.count()} 条凭证，{VoucherItem.objects.count()} 条明细。")


if __name__ == '__main__':
    run()
