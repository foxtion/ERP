from django.urls import path
from apps.hr import views

urlpatterns = [
    path('employees/', views.EmployeeListCreateView.as_view(), name='employee_list'),
    path('employees/<int:pk>/', views.EmployeeRetrieveUpdateDestroyView.as_view(), name='employee_detail'),
    path('employees/options/', views.EmployeeOptionsView.as_view(), name='employee_options'),

    path('attendances/', views.AttendanceListCreateView.as_view(), name='attendance_list'),
    path('attendances/<int:pk>/', views.AttendanceRetrieveUpdateDestroyView.as_view(), name='attendance_detail'),

    path('salaries/', views.SalaryListCreateView.as_view(), name='salary_list'),
    path('salaries/<int:pk>/', views.SalaryRetrieveUpdateDestroyView.as_view(), name='salary_detail'),

    path('recruitments/', views.RecruitmentListCreateView.as_view(), name='recruitment_list'),
    path('recruitments/<int:pk>/', views.RecruitmentRetrieveUpdateDestroyView.as_view(), name='recruitment_detail'),
]
