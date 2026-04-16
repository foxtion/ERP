from django.contrib.auth import get_user_model
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.system.models import Role, Menu, Department
from apps.system.serializers import (
    UserSerializer, RoleSerializer, MenuSerializer, DepartmentSerializer
)
from apps.system.permissions import RBACPermission
from apps.system.filters import UserFilter
from utils.response import success_response, error_response

User = get_user_model()


class LoginView(TokenObtainPairView):
    """
    JWT登录接口：用户输入用户名/密码，返回 access_token 和 refresh_token
    同时返回用户基本信息和权限菜单，供前端初始化使用
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            return error_response(message='用户名或密码错误', code=401)

        data = serializer.validated_data
        user = serializer.user
        user_data = UserSerializer(user).data
        menus = self._get_user_menus(user)
        permissions = self._get_user_permissions(user)

        return success_response(data={
            'access': data['access'],
            'refresh': data['refresh'],
            'user': user_data,
            'menus': menus,
            'permissions': permissions,
        }, message='登录成功')

    def _get_user_menus(self, user):
        if user.is_superuser:
            queryset = Menu.objects.filter(is_active=True).exclude(menu_type='BUTTON')
        else:
            menu_ids = set()
            for role in user.roles.all():
                for menu in role.menus.filter(is_active=True).exclude(menu_type='BUTTON'):
                    menu_ids.add(menu.id)
                    parent = menu.parent
                    while parent:
                        menu_ids.add(parent.id)
                        parent = parent.parent
            queryset = Menu.objects.filter(id__in=menu_ids).exclude(menu_type='BUTTON')
        top_menus = queryset.filter(parent__isnull=True).order_by('sort_order', 'id')
        return MenuSerializer(top_menus, many=True).data

    def _get_user_permissions(self, user):
        if user.is_superuser:
            return list(Menu.objects.filter(
                is_active=True, menu_type='BUTTON', permission__isnull=False
            ).values_list('permission', flat=True))
        perms = set()
        for role in user.roles.all():
            for menu in role.menus.filter(
                is_active=True, menu_type='BUTTON', permission__isnull=False
            ):
                perms.add(menu.permission)
        return list(perms)


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return success_response(message='登出成功')


class UserInfoView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return success_response(data=serializer.data)


# ==================== 统一包装响应格式的 Mixin ====================

class CreateResponseMixin:
    """
    为 ListCreateAPIView 统一包装 create 响应格式
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return success_response(data=serializer.data, message='创建成功', code=200)


class RUDResponseMixin:
    """
    为 RetrieveUpdateDestroyAPIView 统一包装 {code, message, data} 响应格式
    """
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data, message='更新成功')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message='删除成功')


# ==================== CRUD 视图类 ====================

class UserListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'system:user:view'
    search_fields = ['username', 'phone', 'email']
    ordering_fields = ['id', 'created_at']
    filterset_class = UserFilter

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'system:user:add'
        return super().get_permissions()


class UserRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'system:user:edit'
        elif method == 'DELETE':
            self.required_permission = 'system:user:delete'
        else:
            self.required_permission = 'system:user:view'
        return super().get_permissions()


class RoleListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = Role.objects.all().order_by('-id')
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'system:role:view'
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'system:role:add'
        return super().get_permissions()


class RoleRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'system:role:edit'
        elif method == 'DELETE':
            self.required_permission = 'system:role:delete'
        else:
            self.required_permission = 'system:role:view'
        return super().get_permissions()


class RoleMenuView(views.APIView):
    """
    角色菜单权限：GET 获取角色的菜单ID列表；PUT 更新角色菜单
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'system:role:edit'

    def get(self, request, pk):
        try:
            role = Role.objects.get(pk=pk)
            menu_ids = list(role.menus.values_list('id', flat=True))
            return success_response(data={'role_id': pk, 'menu_ids': menu_ids})
        except Role.DoesNotExist:
            return error_response(message='角色不存在', code=404)

    def put(self, request, pk):
        try:
            role = Role.objects.get(pk=pk)
            menu_ids = request.data.get('menu_ids', [])
            role.menus.set(menu_ids)
            return success_response(message='角色菜单权限更新成功')
        except Role.DoesNotExist:
            return error_response(message='角色不存在', code=404)


class MenuListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = Menu.objects.filter(is_active=True)
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'system:menu:view'

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'system:menu:add'
        return super().get_permissions()

    def get_queryset(self):
        return Menu.objects.filter(is_active=True, parent__isnull=True).order_by('sort_order', 'id')


class MenuAllTreeView(views.APIView):
    """
    获取完整菜单树（用于菜单管理页面的父级选择）
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'system:menu:view'

    def get(self, request):
        queryset = Menu.objects.filter(is_active=True, parent__isnull=True).order_by('sort_order', 'id')
        data = MenuSerializer(queryset, many=True).data
        return success_response(data=data)


class MenuAllFlatView(views.APIView):
    """
    获取完整菜单平铺列表（用于角色分配菜单时的树形选择）
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'system:role:view'

    def get(self, request):
        queryset = Menu.objects.filter(is_active=True).order_by('sort_order', 'id')
        data = MenuSerializer(queryset, many=True).data
        return success_response(data=data)


class MenuRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'system:menu:edit'
        elif method == 'DELETE':
            self.required_permission = 'system:menu:delete'
        else:
            self.required_permission = 'system:menu:view'
        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class DepartmentListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'system:dept:view'
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'system:dept:add'
        return super().get_permissions()

    def get_queryset(self):
        return Department.objects.filter(is_active=True, parent__isnull=True).order_by('sort_order', 'id')


class DepartmentAllTreeView(views.APIView):
    """
    获取完整部门树（用于用户管理等部门选择）
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'system:dept:view'

    def get(self, request):
        queryset = Department.objects.filter(is_active=True, parent__isnull=True).order_by('sort_order', 'id')
        data = DepartmentSerializer(queryset, many=True).data
        return success_response(data=data)


class DepartmentRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'system:dept:edit'
        elif method == 'DELETE':
            self.required_permission = 'system:dept:delete'
        else:
            self.required_permission = 'system:dept:view'
        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
