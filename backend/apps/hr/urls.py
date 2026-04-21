from django.urls import path
from apps.hr import views

urlpatterns = [
    path('employees/', views.EmployeeListCreateView.as_view(), name='employee_list'),
    path('employees/<int:pk>/', views.EmployeeRetrieveUpdateDestroyView.as_view(), name='employee_detail'),
    path('employees/<int:pk>/confirm/', views.EmployeeConfirmView.as_view(), name='employee_confirm'),
    path('employees/<int:pk>/resign/', views.EmployeeResignView.as_view(), name='employee_resign'),
    path('employees/generate_no/', views.EmployeeGenerateNoView.as_view(), name='employee_generate_no'),
    path('employees/stats/', views.EmployeeStatsView.as_view(), name='employee_stats'),
    path('employees/options/', views.EmployeeOptionsView.as_view(), name='employee_options'),

    path('attendances/', views.AttendanceListCreateView.as_view(), name='attendance_list'),
    path('attendances/<int:pk>/', views.AttendanceRetrieveUpdateDestroyView.as_view(), name='attendance_detail'),
    path('attendances/stats/', views.AttendanceStatsView.as_view(), name='attendance_stats'),
    path('attendances/bulk/', views.AttendanceBulkCreateView.as_view(), name='attendance_bulk'),

    path('salaries/', views.SalaryListCreateView.as_view(), name='salary_list'),
    path('salaries/<int:pk>/', views.SalaryRetrieveUpdateDestroyView.as_view(), name='salary_detail'),

    path('recruitments/', views.RecruitmentListCreateView.as_view(), name='recruitment_list'),
    path('recruitments/<int:pk>/', views.RecruitmentRetrieveUpdateDestroyView.as_view(), name='recruitment_detail'),

    path('dingtalk/config/', views.DingTalkConfigView.as_view(), name='dingtalk_config'),
    path('dingtalk/test/', views.DingTalkTestConnectionView.as_view(), name='dingtalk_test'),
    path('dingtalk/sync/', views.DingTalkSyncView.as_view(), name='dingtalk_sync'),
]
