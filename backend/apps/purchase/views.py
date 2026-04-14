from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from apps.system.permissions import RBACPermission
from utils.response import success_response, error_response
from utils.pagination import StandardPagination

from apps.purchase.models import (
    Supplier, PurchaseRequest, PurchaseOrder, PurchaseInStock
)
from apps.purchase.serializers import (
    SupplierSerializer, PurchaseRequestSerializer,
    PurchaseOrderSerializer, PurchaseInStockSerializer
)


class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.filter(is_active=True).order_by('-id')
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:supplier:view'
    search_fields = ['name', 'code', 'contact', 'phone']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'purchase:supplier:add'
        return super().get_permissions()


class SupplierRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'purchase:supplier:edit'
        elif method == 'DELETE':
            self.required_permission = 'purchase:supplier:delete'
        else:
            self.required_permission = 'purchase:supplier:view'
        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class PurchaseRequestListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseRequest.objects.all().order_by('-id')
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:request:view'
    search_fields = ['request_no']
    filterset_fields = ['status']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'purchase:request:add'
        return super().get_permissions()


class PurchaseRequestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'purchase:request:edit'
        elif method == 'DELETE':
            self.required_permission = 'purchase:request:delete'
        else:
            self.required_permission = 'purchase:request:view'
        return super().get_permissions()


class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all().order_by('-id')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:order:view'
    search_fields = ['order_no', 'supplier__name']
    filterset_fields = ['status']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'purchase:order:add'
        return super().get_permissions()


class PurchaseOrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'purchase:order:edit'
        elif method == 'DELETE':
            self.required_permission = 'purchase:order:delete'
        else:
            self.required_permission = 'purchase:order:view'
        return super().get_permissions()


class PurchaseInStockListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseInStock.objects.all().order_by('-id')
    serializer_class = PurchaseInStockSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:instock:view'
    search_fields = ['stock_no', 'order__order_no']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'purchase:instock:add'
        return super().get_permissions()


class PurchaseInStockRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseInStock.objects.all()
    serializer_class = PurchaseInStockSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'purchase:instock:edit'
        elif method == 'DELETE':
            self.required_permission = 'purchase:instock:delete'
        else:
            self.required_permission = 'purchase:instock:view'
        return super().get_permissions()


class PurchaseOrderOptionsView(views.APIView):
    """
    获取可用于下拉选择的采购订单列表
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:order:view'

    def get(self, request):
        queryset = PurchaseOrder.objects.filter(status__in=['draft', 'confirmed', 'partial']).order_by('-id')
        data = [{'id': o.id, 'order_no': o.order_no, 'supplier_name': o.supplier.name} for o in queryset]
        return success_response(data=data)
