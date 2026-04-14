from django.db import models
from django.conf import settings


class Warehouse(models.Model):
    """
    仓库档案
    """
    name = models.CharField(max_length=64, verbose_name='仓库名称')
    code = models.CharField(max_length=64, unique=True, verbose_name='仓库编码')
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name='所在位置')
    manager = models.CharField(max_length=64, blank=True, null=True, verbose_name='负责人')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'inventory_warehouse'
        verbose_name = '仓库'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name


class Inventory(models.Model):
    """
    库存台账：记录每个仓库中各物料的实时库存数量
    """
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='仓库')
    material_name = models.CharField(max_length=128, verbose_name='物料名称')
    spec = models.CharField(max_length=128, blank=True, null=True, verbose_name='规格型号')
    unit = models.CharField(max_length=32, default='件', verbose_name='单位')
    qty = models.DecimalField(max_digits=14, decimal_places=4, default=0, verbose_name='库存数量')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'inventory_stock'
        verbose_name = '库存'
        verbose_name_plural = verbose_name
        ordering = ['-id']
        unique_together = [['warehouse', 'material_name', 'spec']]

    def __str__(self):
        return f"{self.material_name}@{self.warehouse.name}"


class StockTransfer(models.Model):
    """
    库存调拨单
    """
    transfer_no = models.CharField(max_length=64, unique=True, verbose_name='调拨单号')
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='out_transfers', verbose_name='调出仓库')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='in_transfers', verbose_name='调入仓库')
    transfer_date = models.DateField(verbose_name='调拨日期')
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
        db_table = 'inventory_stock_transfer'
        verbose_name = '库存调拨'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.transfer_no


class StockTransferItem(models.Model):
    """
    调拨明细
    """
    transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name='items', verbose_name='调拨单')
    material_name = models.CharField(max_length=128, verbose_name='物料名称')
    spec = models.CharField(max_length=128, blank=True, null=True, verbose_name='规格型号')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='调拨数量')
    unit = models.CharField(max_length=32, default='件', verbose_name='单位')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'inventory_stock_transfer_item'
        verbose_name = '调拨明细'
        verbose_name_plural = verbose_name


class InventoryCheck(models.Model):
    """
    库存盘点单
    """
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('completed', '已完成'),
    )

    check_no = models.CharField(max_length=64, unique=True, verbose_name='盘点单号')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='盘点仓库')
    check_date = models.DateField(verbose_name='盘点日期')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
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
        db_table = 'inventory_check'
        verbose_name = '库存盘点'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.check_no


class InventoryCheckItem(models.Model):
    """
    盘点明细
    """
    check_order = models.ForeignKey(InventoryCheck, on_delete=models.CASCADE, related_name='items', verbose_name='盘点单')
    material_name = models.CharField(max_length=128, verbose_name='物料名称')
    spec = models.CharField(max_length=128, blank=True, null=True, verbose_name='规格型号')
    unit = models.CharField(max_length=32, default='件', verbose_name='单位')
    book_qty = models.DecimalField(max_digits=14, decimal_places=4, default=0, verbose_name='账面数量')
    actual_qty = models.DecimalField(max_digits=14, decimal_places=4, default=0, verbose_name='实盘数量')
    diff_qty = models.DecimalField(max_digits=14, decimal_places=4, default=0, verbose_name='差异数量')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'inventory_check_item'
        verbose_name = '盘点明细'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.diff_qty = (self.actual_qty or 0) - (self.book_qty or 0)
        super().save(*args, **kwargs)
