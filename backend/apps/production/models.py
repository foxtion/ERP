from django.db import models
from django.conf import settings


class BOM(models.Model):
    """
    物料清单（BOM）：定义一个产品由哪些原材料组成
    """
    product_name = models.CharField(max_length=128, verbose_name='产品名称')
    product_code = models.CharField(max_length=64, unique=True, verbose_name='产品编码')
    version = models.CharField(max_length=32, default='V1.0', verbose_name='版本')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'production_bom'
        verbose_name = 'BOM'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.product_name


class BOMItem(models.Model):
    """
    BOM明细：组成产品的子物料
    """
    bom = models.ForeignKey(BOM, on_delete=models.CASCADE, related_name='items', verbose_name='BOM')
    material_name = models.CharField(max_length=128, verbose_name='物料名称')
    spec = models.CharField(max_length=128, blank=True, null=True, verbose_name='规格型号')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='用量')
    unit = models.CharField(max_length=32, default='件', verbose_name='单位')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'production_bom_item'
        verbose_name = 'BOM明细'
        verbose_name_plural = verbose_name


class ProductionPlan(models.Model):
    """
    生产计划：计划生产哪些产品、数量、日期
    """
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )

    plan_no = models.CharField(max_length=64, unique=True, verbose_name='计划编号')
    plan_date = models.DateField(verbose_name='计划日期')
    product_name = models.CharField(max_length=128, verbose_name='产品名称')
    product_code = models.CharField(max_length=64, verbose_name='产品编码')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='计划数量')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    planner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='计划员'
    )
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'production_plan'
        verbose_name = '生产计划'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.plan_no


class ProductionOrder(models.Model):
    """
    生产工单：下达给车间的具体生产任务
    """
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('released', '已下达'),
        ('processing', '生产中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )

    order_no = models.CharField(max_length=64, unique=True, verbose_name='工单编号')
    plan = models.ForeignKey(
        ProductionPlan,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='关联计划'
    )
    bom = models.ForeignKey(
        BOM,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='关联BOM'
    )
    order_date = models.DateField(verbose_name='开工日期')
    product_name = models.CharField(max_length=128, verbose_name='产品名称')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='生产数量')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='负责人'
    )
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'production_order'
        verbose_name = '生产工单'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.order_no


class MaterialRequisition(models.Model):
    """
    领料单：根据工单从仓库领取原材料
    """
    requisition_no = models.CharField(max_length=64, unique=True, verbose_name='领料单号')
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.PROTECT, verbose_name='关联工单')
    requisition_date = models.DateField(verbose_name='领料日期')
    warehouse = models.CharField(max_length=64, default='默认仓库', verbose_name='领料仓库')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='领料人'
    )
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'production_requisition'
        verbose_name = '领料单'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.requisition_no


class MaterialRequisitionItem(models.Model):
    """
    领料明细
    """
    requisition = models.ForeignKey(MaterialRequisition, on_delete=models.CASCADE, related_name='items', verbose_name='领料单')
    material_name = models.CharField(max_length=128, verbose_name='物料名称')
    spec = models.CharField(max_length=128, blank=True, null=True, verbose_name='规格型号')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='领料数量')
    unit = models.CharField(max_length=32, default='件', verbose_name='单位')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'production_requisition_item'
        verbose_name = '领料明细'
        verbose_name_plural = verbose_name


class ProductionInStock(models.Model):
    """
    生产入库单：记录完工产品入库
    """
    stock_no = models.CharField(max_length=64, unique=True, verbose_name='入库单号')
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.PROTECT, verbose_name='关联工单')
    stock_date = models.DateField(verbose_name='入库日期')
    warehouse = models.CharField(max_length=64, default='默认仓库', verbose_name='入库仓库')
    product_name = models.CharField(max_length=128, verbose_name='产品名称')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, verbose_name='入库数量')
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
        db_table = 'production_in_stock'
        verbose_name = '生产入库'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.stock_no
