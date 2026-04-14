from django.contrib.auth.models import AbstractUser
from django.db import models


class BaseModel(models.Model):
    """
    抽象基类：为所有业务模型提供统一的审计字段
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')

    class Meta:
        abstract = True


class Department(BaseModel):
    """
    部门表：支持树形结构
    """
    name = models.CharField(max_length=64, verbose_name='部门名称')
    code = models.CharField(max_length=64, unique=True, verbose_name='部门编码')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
        verbose_name='上级部门'
    )
    sort_order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        db_table = 'system_department'
        verbose_name = '部门'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Menu(BaseModel):
    """
    菜单表：用于前端动态路由及按钮权限控制
    """
    MENU_TYPE_CHOICES = (
        ('DIR', '目录'),
        ('MENU', '菜单'),
        ('BUTTON', '按钮'),
    )

    name = models.CharField(max_length=64, verbose_name='菜单名称')
    title = models.CharField(max_length=64, verbose_name='显示标题')
    path = models.CharField(max_length=128, blank=True, null=True, verbose_name='路由路径')
    component = models.CharField(max_length=128, blank=True, null=True, verbose_name='组件路径')
    icon = models.CharField(max_length=64, blank=True, null=True, verbose_name='图标')
    permission = models.CharField(max_length=128, blank=True, null=True, verbose_name='权限标识')
    menu_type = models.CharField(max_length=16, choices=MENU_TYPE_CHOICES, default='MENU', verbose_name='菜单类型')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
        verbose_name='上级菜单'
    )
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_hidden = models.BooleanField(default=False, verbose_name='是否隐藏')
    keep_alive = models.BooleanField(default=True, verbose_name='是否缓存')

    class Meta:
        db_table = 'system_menu'
        verbose_name = '菜单'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title


class Role(BaseModel):
    """
    角色表：RBAC核心
    """
    name = models.CharField(max_length=64, verbose_name='角色名称')
    code = models.CharField(max_length=64, unique=True, verbose_name='角色编码')
    menus = models.ManyToManyField(Menu, blank=True, verbose_name='权限菜单')
    sort_order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        db_table = 'system_role'
        verbose_name = '角色'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    自定义用户模型：扩展手机号、头像、部门、角色等字段
    """
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatar/%Y/%m', blank=True, null=True, verbose_name='头像')
    dept = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='所属部门'
    )
    roles = models.ManyToManyField(Role, blank=True, verbose_name='角色')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'system_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.username
