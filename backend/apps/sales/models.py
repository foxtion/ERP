from django.db import models
from django.conf import settings


class Customer(models.Model):
    """
    客户档案
    """
    LEVEL_CHOICES = (
        ('A', 'A级-VIP'),
        ('B', 'B级-重要'),
        ('C', 'C级-普通'),
        ('D', 'D级-潜在'),
    )

    name = models.CharField(max_length=128, verbose_name='客户名称')
    code = models.CharField(max_length=64, unique=True, verbose_name='客户编码')
    contact = models.CharField(max_length=64, blank=True, null=True, verbose_name='联系人')
    phone = models.CharField(max_length=32, blank=True, null=True, verbose_name='联系电话')
    email = models.EmailField(max_length=128, blank=True, null=True, verbose_name='邮箱')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='地址')
    industry = models.CharField(max_length=64, blank=True, null=True, verbose_name='所属行业')
    level = models.CharField(max_length=8, choices=LEVEL_CHOICES, default='C', verbose_name='客户等级')
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='信用额度')
    tax_no = models.CharField(max_length=64, blank=True, null=True, verbose_name='统一社会信用代码')
    bank_info = models.CharField(max_length=255, blank=True, null=True, verbose_name='银行信息')
    allow_partial_shipment = models.BooleanField(default=False, verbose_name='允许部分出货')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_customer'
        verbose_name = '客户'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name


class SalesOrder(models.Model):
    """
    销售订单
    """
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('partial', '部分出库'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )

    order_no = models.CharField(max_length=64, unique=True, blank=True, verbose_name='订单编号')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name='客户')
    order_date = models.DateField(verbose_name='订单日期')
    delivery_date = models.DateField(blank=True, null=True, verbose_name='交货日期')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='总金额')
    salesman = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='销售员'
    )
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_order'
        verbose_name = '销售订单'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.order_no


class SalesOrderItem(models.Model):
    """
    销售订单明细
    """
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items', verbose_name='销售订单')
    material_code = models.CharField(max_length=64, blank=True, null=True, verbose_name='物料编码')
    material_name = models.CharField(max_length=128, verbose_name='物料名称')
    spec = models.CharField(max_length=128, blank=True, null=True, verbose_name='规格型号')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='销售数量')
    unit = models.CharField(max_length=32, default='件', verbose_name='单位')
    price = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='单价')
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='金额')
    delivered_qty = models.DecimalField(max_digits=14, decimal_places=4, default=0, verbose_name='已出库数量')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'sales_order_item'
        verbose_name = '销售订单明细'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.amount = (self.quantity or 0) * (self.price or 0)
        super().save(*args, **kwargs)


class SalesOutStock(models.Model):
    """
    销售出库单
    """
    stock_no = models.CharField(max_length=64, unique=True, verbose_name='出库单号')
    order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT, verbose_name='关联销售订单')
    stock_date = models.DateField(verbose_name='出库日期')
    warehouse = models.CharField(max_length=64, default='默认仓库', verbose_name='出库仓库')
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
        db_table = 'sales_out_stock'
        verbose_name = '销售出库'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.stock_no


class SalesOutStockItem(models.Model):
    """
    销售出库明细
    """
    stock = models.ForeignKey(SalesOutStock, on_delete=models.CASCADE, related_name='items', verbose_name='出库单')
    material_name = models.CharField(max_length=128, verbose_name='物料名称')
    spec = models.CharField(max_length=128, blank=True, null=True, verbose_name='规格型号')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='出库数量')
    unit = models.CharField(max_length=32, default='件', verbose_name='单位')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'sales_out_stock_item'
        verbose_name = '销售出库明细'
        verbose_name_plural = verbose_name


class SalesReturn(models.Model):
    """
    销售退货单
    """
    return_no = models.CharField(max_length=64, unique=True, verbose_name='退货单号')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name='客户')
    return_date = models.DateField(verbose_name='退货日期')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='退货总金额')
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
        db_table = 'sales_return'
        verbose_name = '销售退货'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.return_no


class SalesReturnItem(models.Model):
    """
    销售退货明细
    """
    return_order = models.ForeignKey(SalesReturn, on_delete=models.CASCADE, related_name='items', verbose_name='退货单')
    material_name = models.CharField(max_length=128, verbose_name='物料名称')
    spec = models.CharField(max_length=128, blank=True, null=True, verbose_name='规格型号')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='退货数量')
    unit = models.CharField(max_length=32, default='件', verbose_name='单位')
    price = models.DecimalField(max_digits=14, decimal_places=4, default=0, verbose_name='单价')
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='金额')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'sales_return_item'
        verbose_name = '销售退货明细'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.amount = (self.quantity or 0) * (self.price or 0)
        super().save(*args, **kwargs)
