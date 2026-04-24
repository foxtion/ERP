from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.system.models import Department as SysDepartment
from datetime import datetime, time, timedelta


class Position(models.Model):
    """
    职位表：隶属于部门
    """
    name = models.CharField(max_length=64, verbose_name='职位名称')
    department = models.ForeignKey(
        'system.Department',
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='所属部门'
    )
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hr_position'
        verbose_name = '职位'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.department.name} - {self.name}'


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
    EDUCATION_CHOICES = (
        ('high_school', '高中'),
        ('college', '大专'),
        ('bachelor', '本科'),
        ('master', '硕士'),
        ('doctor', '博士'),
    )

    employee_no = models.CharField(max_length=64, unique=True, verbose_name='工号')
    name = models.CharField(max_length=64, verbose_name='姓名')
    gender = models.CharField(max_length=16, choices=GENDER_CHOICES, default='male', verbose_name='性别')
    phone = models.CharField(max_length=32, blank=True, null=True, verbose_name='手机号')
    email = models.EmailField(blank=True, null=True, verbose_name='邮箱')
    id_card = models.CharField(max_length=18, blank=True, null=True, verbose_name='身份证号')
    birth_date = models.DateField(blank=True, null=True, verbose_name='出生日期')
    department_old = models.CharField(max_length=64, blank=True, null=True, verbose_name='部门(旧)')
    position_old = models.CharField(max_length=64, blank=True, null=True, verbose_name='职位(旧)')
    department = models.ForeignKey(
        'system.Department',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employees',
        verbose_name='部门'
    )
    position = models.ForeignKey(
        'hr.Position',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employees',
        verbose_name='职位'
    )
    education = models.CharField(max_length=16, choices=EDUCATION_CHOICES, blank=True, null=True, verbose_name='学历')
    graduate_school = models.CharField(max_length=128, blank=True, null=True, verbose_name='毕业院校')
    entry_date = models.DateField(blank=True, null=True, verbose_name='入职日期')
    probation_end_date = models.DateField(blank=True, null=True, verbose_name='试用期结束日')
    contract_end_date = models.DateField(blank=True, null=True, verbose_name='合同到期日')
    resignation_date = models.DateField(blank=True, null=True, verbose_name='离职日期')
    bank_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='开户行')
    bank_account = models.CharField(max_length=32, blank=True, null=True, verbose_name='工资卡号')
    emergency_contact = models.CharField(max_length=64, blank=True, null=True, verbose_name='紧急联系人')
    emergency_phone = models.CharField(max_length=32, blank=True, null=True, verbose_name='紧急联系电话')
    dingtalk_user_id = models.CharField(max_length=64, blank=True, null=True, verbose_name='钉钉用户ID')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='地址')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employee_profile',
        verbose_name='系统用户'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hr_employee'
        verbose_name = '员工档案'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name

    @property
    def age(self):
        if not self.birth_date:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def _generate_username(self, base_name):
        """基于员工姓名生成唯一用户名，重名时自动加序号后缀"""
        User = get_user_model()
        if not User.objects.filter(username=base_name).exists():
            return base_name
        seq = 1
        while True:
            candidate = f'{base_name}{seq}'
            if not User.objects.filter(username=candidate).exists():
                return candidate
            seq += 1

    def sync_user(self):
        """
        将员工档案信息同步到关联的系统用户。
        - 不存在则自动创建
        - 用户名跟随员工姓名（重名自动加后缀）
        - 密码重置为员工编号（仅在创建时）
        - 在职状态同步到 is_active
        """
        User = get_user_model()
        if self.user:
            user = self.user
            # 同步用户名（如果姓名发生变化且当前用户名不是由其他规则定制的，也同步）
            if user.username != self.name and not User.objects.filter(username=self.name).exists():
                # 优先尝试直接使用姓名，若冲突则生成唯一名
                user.username = self._generate_username(self.name)
            elif user.username != self.name:
                user.username = self._generate_username(self.name)
            user.email = self.email or user.email
            user.phone = self.phone or user.phone
            user.is_active = self.status != 'resigned'
            # 同步部门（department 现在是外键对象）
            if self.department:
                if user.dept_id != self.department.id:
                    user.dept = self.department
                    user.save(update_fields=['username', 'email', 'phone', 'is_active', 'dept'])
                else:
                    user.save(update_fields=['username', 'email', 'phone', 'is_active'])
            else:
                user.save(update_fields=['username', 'email', 'phone', 'is_active'])
        else:
            # 创建新用户
            username = self._generate_username(self.name)
            user = User(
                username=username,
                email=self.email or '',
                phone=self.phone or '',
                is_active=self.status != 'resigned',
            )
            user.set_password(self.employee_no)
            # 同步部门
            if self.department:
                user.dept = self.department
            user.save()
            self.user = user

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        need_update_fk = self.user is None
        self.sync_user()
        # sync_user 创建了新用户时，需要把外键写回数据库（避免递归 save）
        if need_update_fk and self.user:
            Employee.objects.filter(pk=self.pk).update(user=self.user)

    def delete(self, *args, **kwargs):
        if self.user:
            self.user.delete()
        super().delete(*args, **kwargs)


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
    # 排班基准时间（钉钉同步时填充）
    base_check_in = models.TimeField(blank=True, null=True, verbose_name='应上班时间')
    base_check_out = models.TimeField(blank=True, null=True, verbose_name='应下班时间')
    work_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='工作时长(小时)')
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='加班时长(小时)')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='normal', verbose_name='考勤状态')
    late_minutes = models.IntegerField(default=0, verbose_name='迟到分钟数')
    early_minutes = models.IntegerField(default=0, verbose_name='早退分钟数')
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注')
    # 钉钉同步原始数据快照
    dingtalk_detail = models.JSONField(blank=True, null=True, verbose_name='钉钉打卡详情')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hr_attendance'
        verbose_name = '考勤记录'
        verbose_name_plural = verbose_name
        ordering = ['-date', '-id']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.name} - {self.date}"

    def save(self, *args, **kwargs):
        from datetime import datetime, time
        # 处理字符串类型的 time（update_or_create 传入时可能还是字符串）
        check_in = self.check_in
        check_out = self.check_out
        if isinstance(check_in, str):
            try:
                parts = check_in.split(':')
                if len(parts) == 2:
                    h, m = map(int, parts)
                    check_in = time(h, m, 0)
                elif len(parts) == 3:
                    h, m, s = map(int, parts)
                    check_in = time(h, m, s)
                else:
                    check_in = None
            except (ValueError, TypeError):
                check_in = None
        if isinstance(check_out, str):
            try:
                parts = check_out.split(':')
                if len(parts) == 2:
                    h, m = map(int, parts)
                    check_out = time(h, m, 0)
                elif len(parts) == 3:
                    h, m, s = map(int, parts)
                    check_out = time(h, m, s)
                else:
                    check_out = None
            except (ValueError, TypeError):
                check_out = None

        # 将转换后的值写回模型字段
        self.check_in = check_in
        self.check_out = check_out

        # 自动计算工作时长
        if check_in and check_out:
            try:
                in_dt = datetime.combine(datetime.today(), check_in)
                out_dt = datetime.combine(datetime.today(), check_out)
                if out_dt < in_dt:
                    out_dt += timedelta(days=1)
                diff_hours = (out_dt - in_dt).total_seconds() / 3600
                # 扣除午休1小时（如果工作时长大于5小时）
                if diff_hours > 5:
                    diff_hours -= 1
                self.work_hours = round(max(0, diff_hours), 2)
                # 加班时长：超过8小时算加班
                if self.work_hours > 8:
                    self.overtime_hours = round(self.work_hours - 8, 2)
                    self.work_hours = 8
                else:
                    self.overtime_hours = 0
            except Exception:
                pass
        # 自动判断迟到/早退
        if self.status == 'normal' and check_in and check_out:
            if check_in > time(9, 0):
                self.status = 'late'
            elif check_out < time(17, 30):
                self.status = 'early'
        super().save(*args, **kwargs)


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
        unique_together = [['employee', 'year_month']]

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


class DingTalkConfig(models.Model):
    """
    钉钉配置：存储钉钉开放平台凭证和缓存的 access_token
    """
    app_key = models.CharField(max_length=64, verbose_name='AppKey')
    app_secret = models.CharField(max_length=255, verbose_name='AppSecret')
    access_token = models.CharField(max_length=512, blank=True, null=True, verbose_name='AccessToken')
    token_expires_at = models.DateTimeField(blank=True, null=True, verbose_name='Token过期时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hr_dingtalk_config'
        verbose_name = '钉钉配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'钉钉配置: {self.app_key}'
