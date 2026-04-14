from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from apps.system.permissions import RBACPermission
from utils.response import success_response

from apps.inventory.models import Warehouse, Inventory, StockTransfer, InventoryCheck
from apps.inventory.serializers import (
    WarehouseSerializer, InventorySerializer,
    StockTransferSerializer, InventoryCheckSerializer
)


class WarehouseListCreateView(generics.ListCreateAPIView):
    queryset = Warehouse.objects.filter(is_active=True).order_by('-id')
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:warehouse:view'
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'inventory:warehouse:add'
        return super().get_permissions()


class WarehouseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'inventory:warehouse:edit'
        elif method == 'DELETE':
            self.required_permission = 'inventory:warehouse:delete'
        else:
            self.required_permission = 'inventory:warehouse:view'
        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class WarehouseOptionsView(views.APIView):
    """
    仓库下拉选项
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:warehouse:view'

    def get(self, request):
        queryset = Warehouse.objects.filter(is_active=True).order_by('id')
        data = [{'id': w.id, 'name': w.name, 'code': w.code} for w in queryset]
        return success_response(data=data)


class InventoryListView(generics.ListAPIView):
    """
    库存查询：只读列表
    """
    queryset = Inventory.objects.all().order_by('-id')
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:stock:view'
    search_fields = ['material_name', 'spec']
    filterset_fields = ['warehouse']


class StockTransferListCreateView(generics.ListCreateAPIView):
    queryset = StockTransfer.objects.all().order_by('-id')
    serializer_class = StockTransferSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:transfer:view'
    search_fields = ['transfer_no']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'inventory:transfer:add'
        return super().get_permissions()


class StockTransferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'inventory:transfer:edit'
        elif method == 'DELETE':
            self.required_permission = 'inventory:transfer:delete'
        else:
            self.required_permission = 'inventory:transfer:view'
        return super().get_permissions()


class InventoryCheckListCreateView(generics.ListCreateAPIView):
    queryset = InventoryCheck.objects.all().order_by('-id')
    serializer_class = InventoryCheckSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:check:view'
    search_fields = ['check_no']
    filterset_fields = ['status']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'inventory:check:add'
        return super().get_permissions()


class InventoryCheckRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InventoryCheck.objects.all()
    serializer_class = InventoryCheckSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'inventory:check:edit'
        elif method == 'DELETE':
            self.required_permission = 'inventory:check:delete'
        else:
            self.required_permission = 'inventory:check:view'
        return super().get_permissions()
