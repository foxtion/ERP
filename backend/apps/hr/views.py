from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from apps.system.permissions import RBACPermission
from utils.response import success_response

from apps.hr.models import Employee, Attendance, Salary, Recruitment
from apps.hr.serializers import (
    EmployeeSerializer, EmployeeOptionSerializer,
    AttendanceSerializer, SalarySerializer, RecruitmentSerializer
)


class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all().order_by('-id')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:employee:view'
    search_fields = ['employee_no', 'name', 'phone']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'hr:employee:add'
        return super().get_permissions()


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


class EmployeeOptionsView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:employee:view'

    def get(self, request):
        queryset = Employee.objects.filter(status__in=['active', 'probation']).order_by('id')
        data = EmployeeOptionSerializer(queryset, many=True).data
        return success_response(data=data)


class AttendanceListCreateView(generics.ListCreateAPIView):
    queryset = Attendance.objects.all().order_by('-id')
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'hr:attendance:view'
    search_fields = ['employee__name', 'date']
    filterset_fields = ['status']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'hr:attendance:add'
        return super().get_permissions()


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
