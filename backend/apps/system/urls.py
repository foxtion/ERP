from django.urls import path

from apps.system import views

urlpatterns = [
    # JWT认证
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/info/', views.UserInfoView.as_view(), name='user_info'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change_password'),

    # 用户管理
    path('users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', views.UserRetrieveUpdateDestroyView.as_view(), name='user_detail'),

    # 角色管理
    path('roles/', views.RoleListCreateView.as_view(), name='role_list_create'),
    path('roles/<int:pk>/', views.RoleRetrieveUpdateDestroyView.as_view(), name='role_detail'),
    path('roles/<int:pk>/menus/', views.RoleMenuView.as_view(), name='role_menus'),

    # 菜单管理
    path('menus/', views.MenuListCreateView.as_view(), name='menu_list_create'),
    path('menus/tree/', views.MenuAllTreeView.as_view(), name='menu_tree'),
    path('menus/flat/', views.MenuAllFlatView.as_view(), name='menu_flat'),
    path('menus/<int:pk>/', views.MenuRetrieveUpdateDestroyView.as_view(), name='menu_detail'),

    # 部门管理
    path('departments/', views.DepartmentListCreateView.as_view(), name='dept_list_create'),
    path('departments/tree/', views.DepartmentAllTreeView.as_view(), name='dept_tree'),
    path('departments/<int:pk>/', views.DepartmentRetrieveUpdateDestroyView.as_view(), name='dept_detail'),
]
