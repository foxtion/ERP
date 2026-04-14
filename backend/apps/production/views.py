from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from apps.system.permissions import RBACPermission
from utils.response import success_response

from apps.production.models import BOM, ProductionPlan, ProductionOrder, MaterialRequisition, ProductionInStock
from apps.production.serializers import (
    BOMSerializer, ProductionPlanSerializer,
    ProductionOrderSerializer, MaterialRequisitionSerializer, ProductionInStockSerializer
)


class BOMListCreateView(generics.ListCreateAPIView):
    queryset = BOM.objects.filter(is_active=True).order_by('-id')
    serializer_class = BOMSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:bom:view'
    search_fields = ['product_name', 'product_code']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'production:bom:add'
        return super().get_permissions()


class BOMRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BOM.objects.all()
    serializer_class = BOMSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'production:bom:edit'
        elif method == 'DELETE':
            self.required_permission = 'production:bom:delete'
        else:
            self.required_permission = 'production:bom:view'
        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class BOMOptionsView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:bom:view'

    def get(self, request):
        queryset = BOM.objects.filter(is_active=True).order_by('-id')
        data = [{'id': b.id, 'product_name': b.product_name, 'product_code': b.product_code} for b in queryset]
        return success_response(data=data)


class ProductionPlanListCreateView(generics.ListCreateAPIView):
    queryset = ProductionPlan.objects.all().order_by('-id')
    serializer_class = ProductionPlanSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:plan:view'
    search_fields = ['plan_no', 'product_name']
    filterset_fields = ['status']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'production:plan:add'
        return super().get_permissions()


class ProductionPlanRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductionPlan.objects.all()
    serializer_class = ProductionPlanSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'production:plan:edit'
        elif method == 'DELETE':
            self.required_permission = 'production:plan:delete'
        else:
            self.required_permission = 'production:plan:view'
        return super().get_permissions()


class ProductionOrderListCreateView(generics.ListCreateAPIView):
    queryset = ProductionOrder.objects.all().order_by('-id')
    serializer_class = ProductionOrderSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:order:view'
    search_fields = ['order_no', 'product_name']
    filterset_fields = ['status']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'production:order:add'
        return super().get_permissions()


class ProductionOrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'production:order:edit'
        elif method == 'DELETE':
            self.required_permission = 'production:order:delete'
        else:
            self.required_permission = 'production:order:view'
        return super().get_permissions()


class ProductionOrderOptionsView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:order:view'

    def get(self, request):
        queryset = ProductionOrder.objects.filter(status__in=['draft', 'released', 'processing']).order_by('-id')
        data = [{'id': o.id, 'order_no': o.order_no, 'product_name': o.product_name} for o in queryset]
        return success_response(data=data)


class MaterialRequisitionListCreateView(generics.ListCreateAPIView):
    queryset = MaterialRequisition.objects.all().order_by('-id')
    serializer_class = MaterialRequisitionSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:requisition:view'
    search_fields = ['requisition_no']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'production:requisition:add'
        return super().get_permissions()


class MaterialRequisitionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MaterialRequisition.objects.all()
    serializer_class = MaterialRequisitionSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'production:requisition:edit'
        elif method == 'DELETE':
            self.required_permission = 'production:requisition:delete'
        else:
            self.required_permission = 'production:requisition:view'
        return super().get_permissions()


class ProductionInStockListCreateView(generics.ListCreateAPIView):
    queryset = ProductionInStock.objects.all().order_by('-id')
    serializer_class = ProductionInStockSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:instock:view'
    search_fields = ['stock_no']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'production:instock:add'
        return super().get_permissions()


class ProductionInStockRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductionInStock.objects.all()
    serializer_class = ProductionInStockSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'production:instock:edit'
        elif method == 'DELETE':
            self.required_permission = 'production:instock:delete'
        else:
            self.required_permission = 'production:instock:view'
        return super().get_permissions()
