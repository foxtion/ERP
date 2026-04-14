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
    voucher_no = models.CharField(max_length=64, unique=True, verbose_name='凭证号')
    voucher_date = models.DateField(verbose_name='凭证日期')
    total_debit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='借方合计')
    total_credit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='贷方合计')
    preparer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='制单人'
    )
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
    subject = models.ForeignKey(AccountSubject, on_delete=models.PROTECT, verbose_name='会计科目')
    summary = models.CharField(max_length=255, verbose_name='摘要')
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='借方金额')
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='贷方金额')

    class Meta:
        db_table = 'finance_voucher_item'
        verbose_name = '凭证明细'
        verbose_name_plural = verbose_name


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

    doc_no = models.CharField(max_length=64, unique=True, verbose_name='单据编号')
    doc_type = models.CharField(max_length=16, choices=TYPE_CHOICES, verbose_name='类型')
    counterparty = models.CharField(max_length=128, verbose_name='往来单位')
    doc_date = models.DateField(verbose_name='单据日期')
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='金额')
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='已结金额')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='unpaid', verbose_name='状态')
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


class PaymentReceipt(models.Model):
    """
    收款付款单：记录实际的收付款流水
    """
    TYPE_CHOICES = (
        ('receipt', '收款'),
        ('payment', '付款'),
    )

    doc_no = models.CharField(max_length=64, unique=True, verbose_name='单据编号')
    doc_type = models.CharField(max_length=16, choices=TYPE_CHOICES, verbose_name='类型')
    counterparty = models.CharField(max_length=128, verbose_name='往来单位')
    doc_date = models.DateField(verbose_name='日期')
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='金额')
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
