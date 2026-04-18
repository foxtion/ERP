from django.db import models
from django.conf import settings


class Supplier(models.Model):
    """
    供应商：采购业务的基础档案
    """
    name = models.CharField(max_length=128, verbose_name='供应商名称')
    code = models.CharField(max_length=64, unique=True, verbose_name='供应商编码')
    contact = models.CharField(max_length=64, blank=True, null=True, verbose_name='联系人')
    phone = models.CharField(max_length=32, blank=True, null=True, verbose_name='联系电话')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='地址')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_supplier'
        verbose_name = '供应商'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name


class PurchaseRequest(models.Model):
    """
    采购申请单：由需求部门发起，审批后下推采购订单
    """
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已驳回'),
        ('ordered', '已转单'),
    )

    request_no = models.CharField(max_length=64, unique=True, verbose_name='申请单号')
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='申请人'
    )
    request_date = models.DateField(verbose_name='申请日期')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='总金额')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_request'
        verbose_name = '采购申请'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.request_no


class PurchaseRequestItem(models.Model):
    """
    采购申请明细
    """
    request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='items', verbose_name='申请单')
    material_name = models.CharField(max_length=128, verbose_name='物料名称')
    spec = models.CharField(max_length=128, blank=True, null=True, verbose_name='规格型号')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='数量')
    unit = models.CharField(max_length=32, default='件', verbose_name='单位')
    estimated_price = models.DecimalField(max_digits=14, decimal_places=4, default=0, verbose_name='预估单价')
    estimated_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='预估金额')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'purchase_request_item'
        verbose_name = '采购申请明细'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.estimated_amount = (self.quantity or 0) * (self.estimated_price or 0)
        super().save(*args, **kwargs)


class PurchaseOrder(models.Model):
    """
    采购订单：向供应商下达的正式采购单据
    """
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('partial', '部分入库'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )

    order_no = models.CharField(max_length=64, unique=True, verbose_name='订单编号')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    request = models.ForeignKey(
        'PurchaseRequest',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='来源申请单',
        related_name='orders'
    )
    order_date = models.DateField(verbose_name='订单日期')
    delivery_date = models.DateField(blank=True, null=True, verbose_name='交货日期')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='总金额')
    purchaser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='采购员'
    )
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_order'
        verbose_name = '采购订单'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.order_no


class PurchaseOrderItem(models.Model):
    """
    采购订单明细
    """
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items', verbose_name='采购订单')
    material_name = models.CharField(max_length=128, verbose_name='物料名称')
    spec = models.CharField(max_length=128, blank=True, null=True, verbose_name='规格型号')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='采购数量')
    unit = models.CharField(max_length=32, default='件', verbose_name='单位')
    price = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='单价')
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='金额')
    received_qty = models.DecimalField(max_digits=14, decimal_places=4, default=0, verbose_name='已入库数量')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'purchase_order_item'
        verbose_name = '采购订单明细'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.amount = (self.quantity or 0) * (self.price or 0)
        super().save(*args, **kwargs)


class PurchaseInStock(models.Model):
    """
    采购入库单：记录采购货物的实际入库情况
    """
    stock_no = models.CharField(max_length=64, unique=True, verbose_name='入库单号')
    order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, verbose_name='关联采购订单')
    stock_date = models.DateField(verbose_name='入库日期')
    warehouse = models.CharField(max_length=64, default='默认仓库', verbose_name='入库仓库')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='操作人'
    )
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_in_stock'
        verbose_name = '采购入库'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.stock_no


class PurchaseInStockItem(models.Model):
    """
    采购入库明细
    """
    stock = models.ForeignKey(PurchaseInStock, on_delete=models.CASCADE, related_name='items', verbose_name='入库单')
    material_name = models.CharField(max_length=128, verbose_name='物料名称')
    spec = models.CharField(max_length=128, blank=True, null=True, verbose_name='规格型号')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='入库数量')
    unit = models.CharField(max_length=32, default='件', verbose_name='单位')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'purchase_in_stock_item'
        verbose_name = '采购入库明细'
        verbose_name_plural = verbose_name
