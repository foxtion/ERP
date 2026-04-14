from django.db import models
from django.conf import settings


class Employee(models.Model):
    """
    员工档案
    """
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )
    STATUS_CHOICES = (
        ('active', '在职'),
        ('resigned', '离职'),
        ('probation', '试用期'),
    )

    employee_no = models.CharField(max_length=64, unique=True, verbose_name='工号')
    name = models.CharField(max_length=64, verbose_name='姓名')
    gender = models.CharField(max_length=16, choices=GENDER_CHOICES, default='male', verbose_name='性别')
    phone = models.CharField(max_length=32, blank=True, null=True, verbose_name='手机号')
    email = models.EmailField(blank=True, null=True, verbose_name='邮箱')
    id_card = models.CharField(max_length=18, blank=True, null=True, verbose_name='身份证号')
    department = models.CharField(max_length=64, blank=True, null=True, verbose_name='部门')
    position = models.CharField(max_length=64, blank=True, null=True, verbose_name='职位')
    entry_date = models.DateField(blank=True, null=True, verbose_name='入职日期')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='地址')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hr_employee'
        verbose_name = '员工档案'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name


class Attendance(models.Model):
    """
    考勤记录
    """
    STATUS_CHOICES = (
        ('normal', '正常'),
        ('late', '迟到'),
        ('early', '早退'),
        ('absent', '旷工'),
        ('leave', '请假'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='员工')
    date = models.DateField(verbose_name='考勤日期')
    check_in = models.TimeField(blank=True, null=True, verbose_name='上班时间')
    check_out = models.TimeField(blank=True, null=True, verbose_name='下班时间')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='normal', verbose_name='考勤状态')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hr_attendance'
        verbose_name = '考勤记录'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return f"{self.employee.name} - {self.date}"


class Salary(models.Model):
    """
    薪资记录
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='员工')
    year_month = models.CharField(max_length=7, verbose_name='薪资月份')
    base_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='基本工资')
    bonus = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='奖金')
    deduction = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='扣款')
    total_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='实发工资')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hr_salary'
        verbose_name = '薪资管理'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def save(self, *args, **kwargs):
        self.total_salary = (self.base_salary or 0) + (self.bonus or 0) - (self.deduction or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.year_month}"


class Recruitment(models.Model):
    """
    招聘管理
    """
    STATUS_CHOICES = (
        ('open', '招聘中'),
        ('closed', '已关闭'),
        ('filled', '已招满'),
    )

    job_no = models.CharField(max_length=64, unique=True, verbose_name='招聘编号')
    position = models.CharField(max_length=128, verbose_name='招聘岗位')
    department = models.CharField(max_length=64, blank=True, null=True, verbose_name='招聘部门')
    headcount = models.IntegerField(default=1, verbose_name='招聘人数')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='open', verbose_name='状态')
    requirements = models.TextField(blank=True, null=True, verbose_name='岗位要求')
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='招聘负责人'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hr_recruitment'
        verbose_name = '招聘管理'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.position
