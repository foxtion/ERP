from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from apps.system.permissions import RBACPermission
from utils.response import success_response

from apps.sales.models import Customer, SalesOrder, SalesOutStock, SalesReturn
from apps.sales.serializers import (
    CustomerSerializer, SalesOrderSerializer,
    SalesOutStockSerializer, SalesReturnSerializer
)


class CustomerListCreateView(generics.ListCreateAPIView):
    """
    客户列表 / 新增
    GET  -> 列表（支持搜索 name、code、contact、phone；支持筛选 is_active）
    POST -> 新增客户
    """
    queryset = Customer.objects.filter(is_active=True).order_by('-id')
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:customer:view'
    search_fields = ['name', 'code', 'contact', 'phone']
    filterset_fields = ['is_active']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'sales:customer:add'
        return super().get_permissions()


class CustomerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    客户详情 / 修改 / 删除（逻辑删除）
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'sales:customer:edit'
        elif method == 'DELETE':
            self.required_permission = 'sales:customer:delete'
        else:
            self.required_permission = 'sales:customer:view'
        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class CustomerOptionsView(views.APIView):
    """
    获取可用于下拉选择的客户列表（仅启用状态）
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:customer:view'

    def get(self, request):
        queryset = Customer.objects.filter(is_active=True).order_by('-id')
        data = [{'id': c.id, 'code': c.code, 'name': c.name, 'contact': c.contact, 'phone': c.phone} for c in queryset]
        return success_response(data=data)


class SalesOrderListCreateView(generics.ListCreateAPIView):
    queryset = SalesOrder.objects.all().order_by('-id')
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:order:view'
    search_fields = ['order_no', 'customer__name']
    filterset_fields = ['status']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'sales:order:add'
        return super().get_permissions()


class SalesOrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'sales:order:edit'
        elif method == 'DELETE':
            self.required_permission = 'sales:order:delete'
        else:
            self.required_permission = 'sales:order:view'
        return super().get_permissions()


class SalesOrderOptionsView(views.APIView):
    """
    可用于下拉的销售订单列表
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:order:view'

    def get(self, request):
        queryset = SalesOrder.objects.filter(status__in=['draft', 'confirmed', 'partial']).order_by('-id')
        data = [{'id': o.id, 'order_no': o.order_no, 'customer_name': o.customer.name} for o in queryset]
        return success_response(data=data)


class SalesOutStockListCreateView(generics.ListCreateAPIView):
    queryset = SalesOutStock.objects.all().order_by('-id')
    serializer_class = SalesOutStockSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:outstock:view'
    search_fields = ['stock_no', 'order__order_no']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'sales:outstock:add'
        return super().get_permissions()


class SalesOutStockRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SalesOutStock.objects.all()
    serializer_class = SalesOutStockSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'sales:outstock:edit'
        elif method == 'DELETE':
            self.required_permission = 'sales:outstock:delete'
        else:
            self.required_permission = 'sales:outstock:view'
        return super().get_permissions()


class SalesReturnListCreateView(generics.ListCreateAPIView):
    queryset = SalesReturn.objects.all().order_by('-id')
    serializer_class = SalesReturnSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:return:view'
    search_fields = ['return_no', 'customer__name']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'sales:return:add'
        return super().get_permissions()


class SalesReturnRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SalesReturn.objects.all()
    serializer_class = SalesReturnSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'sales:return:edit'
        elif method == 'DELETE':
            self.required_permission = 'sales:return:delete'
        else:
            self.required_permission = 'sales:return:view'
        return super().get_permissions()
