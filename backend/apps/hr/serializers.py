from rest_framework import serializers
from apps.hr.models import Employee, Attendance, Salary, Recruitment


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class EmployeeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'employee_no', 'name']


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_no = serializers.CharField(source='employee.employee_no', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'


class SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_no = serializers.CharField(source='employee.employee_no', read_only=True)

    class Meta:
        model = Salary
        fields = '__all__'


class RecruitmentSerializer(serializers.ModelSerializer):
    recruiter_name = serializers.CharField(source='recruiter.username', read_only=True)

    class Meta:
        model = Recruitment
        fields = '__all__'
