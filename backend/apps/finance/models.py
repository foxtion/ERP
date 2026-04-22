from django.db import models
from django.conf import settings


class AccountSubject(models.Model):
    """
    会计科目
    """
    CATEGORY_CHOICES = (
        ('asset', '资产'),
        ('liability', '负债'),
        ('equity', '所有者权益'),
        ('income', '收入'),
        ('expense', '费用'),
    )

    code = models.CharField(max_length=32, unique=True, verbose_name='科目编码')
    name = models.CharField(max_length=64, verbose_name='科目名称')
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES, verbose_name='科目类别')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
        verbose_name='上级科目'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'finance_account_subject'
        verbose_name = '会计科目'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self):
        return f"{self.code} {self.name}"


class Voucher(models.Model):
    """
    记账凭证
    """
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('audited', '已审核'),
        ('cancelled', '已作废'),
    )

    voucher_no = models.CharField(max_length=64, unique=True, verbose_name='凭证号')
    voucher_date = models.DateField(verbose_name='凭证日期')
    total_debit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='借方合计')
    total_credit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='贷方合计')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    preparer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='制单人',
        related_name='prepared_vouchers'
    )
    auditor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='审核人',
        related_name='audited_vouchers'
    )
    audit_date = models.DateTimeField(blank=True, null=True, verbose_name='审核日期')
    attachment = models.CharField(max_length=255, blank=True, null=True, verbose_name='附件URL')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_voucher'
        verbose_name = '记账凭证'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.voucher_no


class VoucherItem(models.Model):
    """
    凭证明细
    """
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='items', verbose_name='凭证')
    line_no = models.PositiveIntegerField(default=1, verbose_name='行号')
    subject = models.ForeignKey(AccountSubject, on_delete=models.PROTECT, verbose_name='会计科目')
    summary = models.CharField(max_length=255, verbose_name='摘要')
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='借方金额')
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='贷方金额')

    class Meta:
        db_table = 'finance_voucher_item'
        verbose_name = '凭证明细'
        verbose_name_plural = verbose_name
        ordering = ['line_no']


# ==================== 对账往来模块 ====================

class Counterparty(models.Model):
    """
    往来单位：客户/供应商等往来方
    """
    TYPE_CHOICES = (
        ('customer', '客户'),
        ('supplier', '供应商'),
        ('both', '客户+供应商'),
        ('other', '其他'),
    )

    name = models.CharField(max_length=128, unique=True, verbose_name='单位名称')
    type = models.CharField(max_length=16, choices=TYPE_CHOICES, default='customer', verbose_name='单位类型')
    contact = models.CharField(max_length=64, blank=True, null=True, verbose_name='联系人')
    phone = models.CharField(max_length=32, blank=True, null=True, verbose_name='联系电话')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='地址')
    bank_name = models.CharField(max_length=128, blank=True, null=True, verbose_name='开户银行')
    bank_account = models.CharField(max_length=64, blank=True, null=True, verbose_name='银行账号')
    tax_no = models.CharField(max_length=64, blank=True, null=True, verbose_name='税号')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_counterparty'
        verbose_name = '往来单位'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name

    @property
    def receivable_total(self):
        """应收总额"""
        from decimal import Decimal
        from django.db.models import Sum
        return self.receivables.filter(doc_type='receivable').aggregate(t=Sum('amount'))['t'] or Decimal('0')

    @property
    def receivable_unpaid(self):
        """应收未结金额"""
        from decimal import Decimal
        from django.db.models import Sum, F
        return self.receivables.filter(doc_type='receivable').exclude(status='paid').aggregate(
            t=Sum(F('amount') - F('paid_amount'))
        )['t'] or Decimal('0')

    @property
    def payable_total(self):
        """应付总额"""
        from decimal import Decimal
        from django.db.models import Sum
        return self.receivables.filter(doc_type='payable').aggregate(t=Sum('amount'))['t'] or Decimal('0')

    @property
    def payable_unpaid(self):
        """应付未结金额"""
        from decimal import Decimal
        from django.db.models import Sum, F
        return self.receivables.filter(doc_type='payable').exclude(status='paid').aggregate(
            t=Sum(F('amount') - F('paid_amount'))
        )['t'] or Decimal('0')


class ReceivablePayable(models.Model):
    """
    应收应付：记录企业与客户/供应商之间的应收应付款项
    """
    TYPE_CHOICES = (
        ('receivable', '应收'),
        ('payable', '应付'),
    )
    STATUS_CHOICES = (
        ('unpaid', '未结清'),
        ('partial', '部分结清'),
        ('paid', '已结清'),
    )
    SOURCE_CHOICES = (
        ('sales_order', '销售订单'),
        ('purchase_order', '采购订单'),
        ('manual', '手工录入'),
    )

    doc_no = models.CharField(max_length=64, unique=True, verbose_name='单据编号')
    doc_type = models.CharField(max_length=16, choices=TYPE_CHOICES, verbose_name='类型')
    counterparty = models.CharField(max_length=128, verbose_name='往来单位')
    counterparty_obj = models.ForeignKey(
        Counterparty,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='receivables',
        verbose_name='往来单位关联'
    )
    doc_date = models.DateField(verbose_name='单据日期')
    due_date = models.DateField(blank=True, null=True, verbose_name='到期日')
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='金额')
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='已结金额')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='unpaid', verbose_name='状态')
    source_type = models.CharField(max_length=16, choices=SOURCE_CHOICES, default='manual', verbose_name='来源类型')
    source_no = models.CharField(max_length=64, blank=True, null=True, verbose_name='来源单号')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_receivable_payable'
        verbose_name = '应收应付'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.doc_no

    @property
    def remaining_amount(self):
        from decimal import Decimal
        return (self.amount or Decimal('0')) - (self.paid_amount or Decimal('0'))

    @property
    def overdue_days(self):
        if not self.due_date or self.status == 'paid':
            return 0
        from datetime import date
        today = date.today()
        if self.due_date < today:
            return (today - self.due_date).days
        return 0

    @property
    def is_overdue(self):
        return self.overdue_days > 0


class PaymentReceipt(models.Model):
    """
    收款付款单：记录实际的收付款流水
    """
    TYPE_CHOICES = (
        ('receipt', '收款'),
        ('payment', '付款'),
    )
    METHOD_CHOICES = (
        ('cash', '现金'),
        ('bank_transfer', '银行转账'),
        ('check', '支票'),
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
    )

    doc_no = models.CharField(max_length=64, unique=True, verbose_name='单据编号')
    doc_type = models.CharField(max_length=16, choices=TYPE_CHOICES, verbose_name='类型')
    counterparty = models.CharField(max_length=128, verbose_name='往来单位')
    counterparty_obj = models.ForeignKey(
        Counterparty,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='payments',
        verbose_name='往来单位关联'
    )
    doc_date = models.DateField(verbose_name='日期')
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='金额')
    payment_method = models.CharField(max_length=16, choices=METHOD_CHOICES, default='bank_transfer', verbose_name='付款方式')
    bank_account = models.CharField(max_length=128, blank=True, null=True, verbose_name='银行账户')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='经办人'
    )
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_payment_receipt'
        verbose_name = '收付款'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.doc_no

    @property
    def settled_amount(self):
        from decimal import Decimal
        return self.settlements.aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    @property
    def unsettled_amount(self):
        from decimal import Decimal
        return (self.amount or Decimal('0')) - self.settled_amount


class Settlement(models.Model):
    """
    收付款核销明细：记录收付款单与应收应付单的核销关系
    """
    payment_receipt = models.ForeignKey(
        PaymentReceipt,
        on_delete=models.CASCADE,
        related_name='settlements',
        verbose_name='收付款单'
    )
    receivable_payable = models.ForeignKey(
        ReceivablePayable,
        on_delete=models.CASCADE,
        related_name='settlements',
        verbose_name='应收应付单'
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='核销金额')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='核销时间')

    class Meta:
        db_table = 'finance_settlement'
        verbose_name = '核销明细'
        verbose_name_plural = verbose_name
        ordering = ['-id']
        unique_together = [['payment_receipt', 'receivable_payable']]

    def __str__(self):
        return f"{self.payment_receipt.doc_no} -> {self.receivable_payable.doc_no}: {self.amount}"
