from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from apps.system.permissions import RBACPermission
from utils.response import success_response, error_response
from django.db import transaction
from django.utils import timezone
from datetime import date

from apps.hr.models import Employee, Attendance, Salary, Recruitment, DingTalkConfig
from apps.hr.serializers import (
    EmployeeSerializer, EmployeeOptionSerializer,
    AttendanceSerializer, SalarySerializer, RecruitmentSerializer,
    DingTalkConfigSerializer
)


class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all().order_by('-id')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:employee:view'
    search_fields = ['employee_no', 'name', 'phone', 'department', 'position']
    filterset_fields = ['status', 'gender', 'department']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'hr:employee:add'
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(entry_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(entry_date__lte=date_to)
        # 合同即将到期筛选
        contract_expiry = self.request.query_params.get('contract_expiry')
        from datetime import date, timedelta
        if contract_expiry == '1':
            queryset = queryset.filter(
                contract_end_date__isnull=False,
                contract_end_date__lte=date.today() + timedelta(days=30),
                status__in=['active', 'probation']
            )
        return queryset


class EmployeeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'hr:employee:edit'
        elif method == 'DELETE':
            self.required_permission = 'hr:employee:delete'
        else:
            self.required_permission = 'hr:employee:view'
        return super().get_permissions()


class EmployeeGenerateNoView(views.APIView):
    """
    自动生成工号
    GET /employees/generate_no/
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:employee:add'

    def get(self, request):
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m')
        prefix = f'EMP{date_str}'
        existing = Employee.objects.filter(employee_no__startswith=prefix).order_by('-employee_no').first()
        if existing:
            try:
                seq = int(existing.employee_no.split('-')[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        return success_response(data={'employee_no': f'{prefix}-{seq:03d}'})


class EmployeeConfirmView(views.APIView):
    """
    员工转正：试用期 -> 在职
    POST /employees/<id>/confirm/
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:employee:edit'

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        employee = get_object_or_404(Employee, pk=pk)
        if employee.status != 'probation':
            return error_response(message='只有试用期员工才能转正', code=400)
        employee.status = 'active'
        employee.probation_end_date = date.today()
        employee.save()
        return success_response(data=EmployeeSerializer(employee).data, message='转正成功')


class EmployeeResignView(views.APIView):
    """
    员工离职：在职/试用期 -> 离职
    POST /employees/<id>/resign/
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:employee:edit'

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        employee = get_object_or_404(Employee, pk=pk)
        if employee.status == 'resigned':
            return error_response(message='该员工已离职', code=400)
        employee.status = 'resigned'
        employee.resignation_date = date.today()
        employee.save()
        return success_response(data=EmployeeSerializer(employee).data, message='离职操作成功')


class EmployeeStatsView(views.APIView):
    """
    员工统计
    GET /employees/stats/
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:employee:view'

    def get(self, request):
        from django.db.models import Count
        total = Employee.objects.count()
        active = Employee.objects.filter(status='active').count()
        probation = Employee.objects.filter(status='probation').count()
        resigned = Employee.objects.filter(status='resigned').count()
        # 合同即将到期（30天内）
        from datetime import date, timedelta
        contract_expiry = Employee.objects.filter(
            contract_end_date__isnull=False,
            contract_end_date__lte=date.today() + timedelta(days=30),
            status__in=['active', 'probation']
        ).count()
        # 按部门统计
        dept_stats = []
        for d in Employee.objects.exclude(department='').exclude(department__isnull=True).values('department').annotate(count=Count('id')).order_by('-count'):
            dept_stats.append({'department': d['department'], 'count': d['count']})
        return success_response(data={
            'total': total,
            'active': active,
            'probation': probation,
            'resigned': resigned,
            'contract_expiry': contract_expiry,
            'dept_stats': dept_stats,
        })


class EmployeeOptionsView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:employee:view'

    def get(self, request):
        queryset = Employee.objects.filter(status__in=['active', 'probation']).order_by('id')
        data = EmployeeOptionSerializer(queryset, many=True).data
        return success_response(data=data)


class AttendanceListCreateView(generics.ListCreateAPIView):
    queryset = Attendance.objects.all().order_by('-date', '-id')
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:attendance:view'
    search_fields = ['employee__name', 'employee__employee_no', 'date']
    filterset_fields = ['status', 'employee']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'hr:attendance:add'
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return queryset


class AttendanceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'hr:attendance:edit'
        elif method == 'DELETE':
            self.required_permission = 'hr:attendance:delete'
        else:
            self.required_permission = 'hr:attendance:view'
        return super().get_permissions()


class AttendanceStatsView(views.APIView):
    """
    考勤统计
    GET /attendances/stats/?date_from=2024-01-01&date_to=2024-01-31
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:attendance:view'

    def get(self, request):
        from django.db.models import Count, Sum
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        queryset = Attendance.objects.all()
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        total = queryset.count()
        normal = queryset.filter(status='normal').count()
        late = queryset.filter(status='late').count()
        early = queryset.filter(status='early').count()
        absent = queryset.filter(status='absent').count()
        leave = queryset.filter(status='leave').count()
        total_work_hours = queryset.aggregate(total=Sum('work_hours'))['total'] or 0
        total_overtime = queryset.aggregate(total=Sum('overtime_hours'))['total'] or 0

        # 按员工统计
        employee_stats = []
        for emp in queryset.values('employee__name', 'employee__employee_no').annotate(
            count=Count('id'),
            work_hours=Sum('work_hours'),
            overtime=Sum('overtime_hours')
        ).order_by('-count')[:10]:
            employee_stats.append({
                'name': emp['employee__name'],
                'employee_no': emp['employee__employee_no'],
                'count': emp['count'],
                'work_hours': float(emp['work_hours'] or 0),
                'overtime': float(emp['overtime'] or 0),
            })

        return success_response(data={
            'total': total,
            'normal': normal,
            'late': late,
            'early': early,
            'absent': absent,
            'leave': leave,
            'total_work_hours': float(total_work_hours),
            'total_overtime': float(total_overtime),
            'employee_stats': employee_stats,
        })


class AttendanceBulkCreateView(views.APIView):
    """
    批量打卡：为多个员工同一天打卡
    POST /attendances/bulk/
    {
        "date": "2024-01-15",
        "employee_ids": [1, 2, 3],
        "check_in": "09:00:00",
        "check_out": "18:00:00",
        "status": "normal"
    }
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:attendance:add'

    @transaction.atomic
    def post(self, request):
        date_str = request.data.get('date')
        employee_ids = request.data.get('employee_ids', [])
        check_in = request.data.get('check_in')
        check_out = request.data.get('check_out')
        status = request.data.get('status', 'normal')

        if not date_str or not employee_ids:
            return error_response(message='请指定日期和员工', code=400)

        created_count = 0
        updated_count = 0
        for emp_id in employee_ids:
            obj, created = Attendance.objects.update_or_create(
                employee_id=emp_id,
                date=date_str,
                defaults={
                    'check_in': check_in,
                    'check_out': check_out,
                    'status': status,
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        return success_response(
            data={'created': created_count, 'updated': updated_count},
            message=f'批量打卡完成：新增{created_count}条，更新{updated_count}条'
        )


class SalaryListCreateView(generics.ListCreateAPIView):
    queryset = Salary.objects.all().order_by('-id')
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:salary:view'
    search_fields = ['employee__name', 'year_month']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'hr:salary:add'
        return super().get_permissions()


class SalaryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'hr:salary:edit'
        elif method == 'DELETE':
            self.required_permission = 'hr:salary:delete'
        else:
            self.required_permission = 'hr:salary:view'
        return super().get_permissions()


class RecruitmentListCreateView(generics.ListCreateAPIView):
    queryset = Recruitment.objects.all().order_by('-id')
    serializer_class = RecruitmentSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:recruitment:view'
    search_fields = ['job_no', 'position', 'department']
    filterset_fields = ['status']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'hr:recruitment:add'
        return super().get_permissions()


class RecruitmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recruitment.objects.all()
    serializer_class = RecruitmentSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'hr:recruitment:edit'
        elif method == 'DELETE':
            self.required_permission = 'hr:recruitment:delete'
        else:
            self.required_permission = 'hr:recruitment:view'
        return super().get_permissions()


# ==================== 钉钉集成 ====================

class DingTalkConfigView(views.APIView):
    """
    钉钉配置管理
    GET /dingtalk/config/  -> 获取配置（脱敏）
    POST /dingtalk/config/ -> 保存/更新配置
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:attendance:edit'

    def get(self, request):
        config = DingTalkConfig.objects.first()
        if not config:
            return success_response(data=None)
        # 脱敏显示
        data = {
            'id': config.id,
            'app_key': config.app_key,
            'app_secret_masked': f"{config.app_secret[:4]}****{config.app_secret[-4:]}" if config.app_secret and len(config.app_secret) > 8 else "****",
            'has_token': bool(config.access_token and config.token_expires_at and timezone.now() < config.token_expires_at),
            'updated_at': config.updated_at,
        }
        return success_response(data=data)

    def post(self, request):
        app_key = request.data.get('app_key')
        app_secret = request.data.get('app_secret')
        if not app_key or not app_secret:
            return error_response(message='AppKey 和 AppSecret 不能为空', code=400)

        config, created = DingTalkConfig.objects.update_or_create(
            id=1,  # 单条记录
            defaults={
                'app_key': app_key,
                'app_secret': app_secret,
                'access_token': None,
                'token_expires_at': None,
            }
        )
        return success_response(message='配置保存成功')


class DingTalkTestConnectionView(views.APIView):
    """
    测试钉钉连接
    GET /dingtalk/test/
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:attendance:edit'

    def get(self, request):
        from utils.dingtalk import test_connection
        config = DingTalkConfig.objects.first()
        if not config:
            return error_response(message='未配置钉钉应用', code=400)
        ok, err = test_connection(config.app_key, config.app_secret)
        if ok:
            return success_response(message='钉钉连接成功')
        return error_response(message=err, code=400)


class DingTalkSyncView(views.APIView):
    """
    手动触发钉钉考勤同步
    POST /dingtalk/sync/
    {
        "date_from": "2024-01-01",
        "date_to": "2024-01-07"
    }
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:attendance:edit'

    def post(self, request):
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to')

        if not date_from or not date_to:
            return error_response(message='请指定同步日期范围', code=400)

        from utils.dingtalk import sync_attendance_to_system
        sync_count, err = sync_attendance_to_system(date_from, date_to)
        if err:
            return error_response(message=err, code=400)
        return success_response(
            data={'sync_count': sync_count},
            message=f'同步完成，共导入 {sync_count} 条考勤记录'
        )
