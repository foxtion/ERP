from django.db import models
from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from apps.system.permissions import RBACPermission
from utils.response import success_response

from apps.inventory.models import Warehouse, Inventory, StockTransfer, InventoryCheck, WarehouseLocation, Material, StockWarning
from apps.inventory.serializers import (
    WarehouseSerializer, InventorySerializer,
    StockTransferSerializer, InventoryCheckSerializer, WarehouseLocationSerializer, MaterialSerializer, StockWarningSerializer
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

    def get_queryset(self):
        queryset = super().get_queryset()
        # 自动更新预警状态
        warning = self.request.query_params.get('warning')
        if warning == 'true':
            queryset = queryset.filter(qty__lte=50)
        # 支持按物料编码搜索
        search = self.request.query_params.get('search')
        if search:
            from apps.inventory.models import Material
            matched_codes = Material.objects.filter(
                models.Q(code__icontains=search) | models.Q(name__icontains=search)
            ).exclude(name='').values_list('name', flat=True)
            queryset = queryset.filter(
                models.Q(material_name__icontains=search) |
                models.Q(spec__icontains=search) |
                models.Q(material_name__in=list(matched_codes))
            )
        return queryset


class StockStatsView(views.APIView):
    """
    库存统计：总库存量、物料种类数、仓库数、零库存数
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:stock:view'

    def get(self, request):
        from django.db.models import Sum, Count, Q
        queryset = Inventory.objects.all()
        warehouse = request.query_params.get('warehouse')
        search = request.query_params.get('search')
        if warehouse:
            queryset = queryset.filter(warehouse_id=warehouse)
        if search:
            queryset = queryset.filter(
                Q(material_name__icontains=search) | Q(spec__icontains=search)
            )

        total_qty = queryset.aggregate(total=Sum('qty'))['total'] or 0
        material_count = queryset.values('material_name', 'spec').distinct().count()
        zero_count = queryset.filter(qty=0).count()
        warehouse_count = queryset.values('warehouse').distinct().count()

        data = {
            'total_qty': str(total_qty),
            'material_count': material_count,
            'zero_count': zero_count,
            'warehouse_count': warehouse_count,
        }
        return success_response(data=data)


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


class WarehouseLocationListCreateView(generics.ListCreateAPIView):
    queryset = WarehouseLocation.objects.all().order_by('location_code')
    serializer_class = WarehouseLocationSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:location:view'
    search_fields = ['location_code', 'product_name', 'barcode', 'product_code']
    filterset_fields = ['warehouse', 'is_empty']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'inventory:location:add'
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        # 使用 location_size 参数筛选库位大小，避免与分页参数 size 冲突
        loc_size = self.request.query_params.get('location_size')
        if loc_size and loc_size in ('小', '中', '大'):
            queryset = queryset.filter(size=loc_size)
        return queryset


class WarehouseLocationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WarehouseLocation.objects.all()
    serializer_class = WarehouseLocationSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'inventory:location:edit'
        elif method == 'DELETE':
            self.required_permission = 'inventory:location:delete'
        else:
            self.required_permission = 'inventory:location:view'
        return super().get_permissions()


class MaterialListCreateView(generics.ListCreateAPIView):
    queryset = Material.objects.all().order_by('-id')
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:material:view'
    search_fields = ['code', 'name', 'spec', 'barcode']
    filterset_fields = ['category', 'status']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'inventory:material:add'
        return super().get_permissions()


class MaterialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'inventory:material:edit'
        elif method == 'DELETE':
            self.required_permission = 'inventory:material:delete'
        else:
            self.required_permission = 'inventory:material:view'
        return super().get_permissions()


class StockWarningListView(generics.ListAPIView):
    """
    库存预警列表
    """
    queryset = StockWarning.objects.all().order_by('-id')
    serializer_class = StockWarningSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:stock:view'
    search_fields = ['material_name']
    filterset_fields = ['status', 'is_handled']


class StockWarningHandleView(views.APIView):
    """
    标记预警为已处理
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:stock:view'

    def post(self, request, pk):
        try:
            warning = StockWarning.objects.get(pk=pk)
        except StockWarning.DoesNotExist:
            return success_response(message='预警记录不存在', code=404)
        warning.is_handled = True
        warning.handler = request.user
        warning.handled_at = __import__('django.utils.timezone').utils.timezone.now()
        warning.save()
        return success_response(message='已标记为处理')


class StockWarningStatsView(views.APIView):
    """
    预警统计：未处理数量
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:stock:view'

    def get(self, request):
        unhandled = StockWarning.objects.filter(is_handled=False).count()
        warning_cnt = StockWarning.objects.filter(is_handled=False, status='warning').count()
        urgent_cnt = StockWarning.objects.filter(is_handled=False, status='urgent').count()
        return success_response(data={
            'unhandled': unhandled,
            'warning': warning_cnt,
            'urgent': urgent_cnt,
        })


class MaterialOptionsView(views.APIView):
    """
    物料档案下拉选项
    用于销售订单创建时选择物料
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'inventory:material:view'

    def get(self, request):
        search = request.query_params.get('search', '')
        queryset = Material.objects.filter(status='active').exclude(name='').order_by('id')
        if search:
            queryset = queryset.filter(
                models.Q(code__icontains=search) | models.Q(name__icontains=search)
            )
        data = [{
            'id': m.id,
            'code': m.code,
            'name': m.name,
            'spec': m.spec or '',
            'unit': m.unit,
            'qty': str(m.qty),
        } for m in queryset[:200]]
        return success_response(data=data)
