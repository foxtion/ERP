from rest_framework import serializers
from apps.hr.models import Employee, Attendance, Salary, Recruitment, DingTalkConfig, Position


class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Position
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True, allow_null=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)

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
    department = serializers.CharField(source='employee.department.name', read_only=True)

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


class DingTalkConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DingTalkConfig
        fields = ['id', 'app_key', 'app_secret', 'access_token', 'token_expires_at', 'created_at', 'updated_at']
        extra_kwargs = {
            'app_secret': {'write_only': True},
            'access_token': {'read_only': True},
        }
