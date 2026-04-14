from django.contrib import admin
from apps.hr.models import Employee, Attendance, Salary, Recruitment


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_no', 'name', 'gender', 'department', 'position', 'entry_date', 'status']
    list_filter = ['status', 'gender']
    search_fields = ['employee_no', 'name', 'phone']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'status']
    list_filter = ['status']
    search_fields = ['employee__name']


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'year_month', 'base_salary', 'bonus', 'deduction', 'total_salary']
    search_fields = ['employee__name', 'year_month']


@admin.register(Recruitment)
class RecruitmentAdmin(admin.ModelAdmin):
    list_display = ['job_no', 'position', 'department', 'headcount', 'status', 'recruiter']
    list_filter = ['status']
    search_fields = ['job_no', 'position', 'department']
