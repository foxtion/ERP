from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from apps.system.permissions import RBACPermission
from utils.response import success_response, error_response

from apps.production.models import (
    BOM, BOMItem, ProductionPlan, ProductionOrder,
    MaterialRequisition, MaterialRequisitionItem, ProductionInStock
)
from apps.production.serializers import (
    BOMSerializer, ProductionPlanSerializer,
    ProductionOrderSerializer, MaterialRequisitionSerializer, ProductionInStockSerializer
)


class BOMListCreateView(generics.ListCreateAPIView):
    queryset = BOM.objects.all().order_by('-id')
    serializer_class = BOMSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:bom:view'
    search_fields = ['product_name', 'product_code']
    filterset_fields = ['is_active', 'version']
    ordering_fields = ['id', 'product_code', 'product_name', 'created_at', 'updated_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'production:bom:add'
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        # 默认只展示启用状态，但可通过 is_active 参数筛选全部
        is_active = self.request.query_params.get('is_active')
        if is_active is None:
            queryset = queryset.filter(is_active=True)
        return queryset


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


class BOMCopyView(views.APIView):
    """
    复制BOM：基于现有BOM创建一个新BOM（带副本标记）
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:bom:add'

    def post(self, request, pk):
        try:
            source = BOM.objects.get(pk=pk)
        except BOM.DoesNotExist:
            return success_response(message='BOM不存在', code=404)

        # 复制主记录
        new_bom = BOM.objects.create(
            product_code=source.product_code + '_COPY',
            product_name=source.product_name + '（副本）',
            version=source.version,
            is_active=True,
            remark=source.remark or '',
        )

        # 复制明细
        for item in source.items.all():
            BOMItem.objects.create(
                bom=new_bom,
                material=item.material,
                material_name=item.material_name,
                spec=item.spec,
                quantity=item.quantity,
                unit=item.unit,
                unit_price=item.unit_price,
                remark=item.remark,
            )

        serializer = BOMSerializer(new_bom)
        return success_response(data=serializer.data, message='复制成功')


class ProductionPlanListCreateView(generics.ListCreateAPIView):
    queryset = ProductionPlan.objects.all().order_by('-id')
    serializer_class = ProductionPlanSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:plan:view'
    search_fields = ['plan_no', 'product_name']
    filterset_fields = ['status']
    ordering_fields = ['id', 'plan_date', 'created_at']

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


class ProductionPlanConfirmView(views.APIView):
    """确认计划：草稿 → 已确认"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:plan:edit'

    def post(self, request, pk):
        try:
            plan = ProductionPlan.objects.get(pk=pk)
        except ProductionPlan.DoesNotExist:
            return error_response(message='计划不存在', code=404)
        if plan.status != 'draft':
            return error_response(message='只有草稿状态的计划可以确认', code=400)
        plan.status = 'confirmed'
        plan.save()
        serializer = ProductionPlanSerializer(plan)
        return success_response(data=serializer.data, message='确认成功')


class ProductionPlanCompleteView(views.APIView):
    """完成计划"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:plan:edit'

    def post(self, request, pk):
        try:
            plan = ProductionPlan.objects.get(pk=pk)
        except ProductionPlan.DoesNotExist:
            return error_response(message='计划不存在', code=404)
        if plan.status != 'confirmed':
            return error_response(message='只有已确认状态的计划可以完成', code=400)
        plan.status = 'completed'
        plan.save()
        serializer = ProductionPlanSerializer(plan)
        return success_response(data=serializer.data, message='完成成功')


class ProductionPlanCancelView(views.APIView):
    """取消计划"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:plan:edit'

    def post(self, request, pk):
        try:
            plan = ProductionPlan.objects.get(pk=pk)
        except ProductionPlan.DoesNotExist:
            return error_response(message='计划不存在', code=404)
        if plan.status in ['completed', 'cancelled']:
            return error_response(message='已完成或已取消的计划无法再次取消', code=400)
        plan.status = 'cancelled'
        plan.save()
        serializer = ProductionPlanSerializer(plan)
        return success_response(data=serializer.data, message='取消成功')


class ProductionPlanCreateOrderView(views.APIView):
    """根据计划下推生成生产工单"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:order:add'

    def post(self, request, pk):
        try:
            plan = ProductionPlan.objects.select_related('bom').get(pk=pk)
        except ProductionPlan.DoesNotExist:
            return error_response(message='计划不存在', code=404)
        if plan.status != 'confirmed':
            return error_response(message='只有已确认状态的计划可以生成工单', code=400)

        # 生成工单编号
        from datetime import datetime
        prefix = 'GD' + datetime.now().strftime('%Y%m%d')
        count = ProductionOrder.objects.filter(order_no__startswith=prefix).count()
        order_no = f'{prefix}-{count + 1:03d}'

        order = ProductionOrder.objects.create(
            order_no=order_no,
            plan=plan,
            bom=plan.bom,
            order_date=plan.plan_date,
            product_name=plan.product_name,
            quantity=plan.quantity,
            status='draft',
            operator=request.user,
            remark=f'由计划 {plan.plan_no} 自动生成',
        )

        serializer = ProductionOrderSerializer(order)
        return success_response(data=serializer.data, message='工单生成成功')


class ProductionPlanOptionsView(views.APIView):
    """计划下拉选项"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:plan:view'

    def get(self, request):
        queryset = ProductionPlan.objects.filter(status__in=['draft', 'confirmed']).order_by('-id')
        data = [{'id': p.id, 'plan_no': p.plan_no, 'product_name': p.product_name, 'product_code': p.product_code} for p in queryset]
        return success_response(data=data)


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
    filterset_fields = ['status', 'warehouse']
    ordering_fields = ['id', 'requisition_date', 'created_at']

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


class MaterialRequisitionSubmitView(views.APIView):
    """提交领料单：草稿 → 待审核"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:requisition:edit'

    def post(self, request, pk):
        try:
            req = MaterialRequisition.objects.get(pk=pk)
        except MaterialRequisition.DoesNotExist:
            return error_response(message='领料单不存在', code=404)
        if req.status != 'draft':
            return error_response(message='只有草稿状态的领料单可以提交', code=400)
        req.status = 'pending'
        req.save()
        serializer = MaterialRequisitionSerializer(req)
        return success_response(data=serializer.data, message='提交成功')


class MaterialRequisitionApproveView(views.APIView):
    """审核领料单：待审核 → 已审核"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:requisition:edit'

    def post(self, request, pk):
        try:
            req = MaterialRequisition.objects.get(pk=pk)
        except MaterialRequisition.DoesNotExist:
            return error_response(message='领料单不存在', code=404)
        if req.status != 'pending':
            return error_response(message='只有待审核状态的领料单可以审核', code=400)
        req.status = 'approved'
        req.auditor = request.user
        req.audit_date = timezone.now()
        req.save()
        serializer = MaterialRequisitionSerializer(req)
        return success_response(data=serializer.data, message='审核通过')


class MaterialRequisitionIssueView(views.APIView):
    """出库发料：已审核 → 已出库，同时扣减库存"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:requisition:edit'

    @transaction.atomic
    def post(self, request, pk):
        try:
            req = MaterialRequisition.objects.prefetch_related('items').get(pk=pk)
        except MaterialRequisition.DoesNotExist:
            return error_response(message='领料单不存在', code=404)
        if req.status != 'approved':
            return error_response(message='只有已审核状态的领料单可以出库', code=400)

        # 扣减库存
        from apps.inventory.models import Warehouse, Inventory
        warehouse = Warehouse.objects.filter(name=req.warehouse).first()
        if not warehouse:
            return error_response(message=f'仓库 "{req.warehouse}" 不存在，无法出库', code=400)

        for item in req.items.all():
            issue_qty = item.actual_quantity if item.actual_quantity and item.actual_quantity > 0 else item.quantity
            spec = item.spec or ''
            # 查找库存记录（按仓库+物料名称+规格）
            inv = Inventory.objects.select_for_update().filter(warehouse=warehouse, material_name=item.material_name, spec=spec).first()
            if not inv:
                return error_response(message=f'物料 "{item.material_name}({spec})" 在仓库 "{req.warehouse}" 中无库存记录', code=400)
            if inv.qty < issue_qty:
                return error_response(
                    message=f'物料 "{item.material_name}" 库存不足，当前库存 {inv.qty}，需要出库 {issue_qty}',
                    code=400
                )
            inv.qty -= issue_qty
            inv.save()
            # 更新实发数量
            if not item.actual_quantity or item.actual_quantity == 0:
                item.actual_quantity = issue_qty
                item.save()

        req.status = 'issued'
        req.issue_date = timezone.now()
        req.save()
        serializer = MaterialRequisitionSerializer(req)
        return success_response(data=serializer.data, message='出库成功')


class MaterialRequisitionCancelView(views.APIView):
    """取消领料单"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:requisition:edit'

    @transaction.atomic
    def post(self, request, pk):
        try:
            req = MaterialRequisition.objects.prefetch_related('items').get(pk=pk)
        except MaterialRequisition.DoesNotExist:
            return error_response(message='领料单不存在', code=404)
        if req.status in ['closed', 'cancelled']:
            return error_response(message='已关闭或已取消的领料单无法再次取消', code=400)
        # 已出库的领料单取消时回滚库存
        if req.status == 'issued':
            from apps.inventory.models import Warehouse, Inventory
            warehouse = Warehouse.objects.filter(name=req.warehouse).first()
            if warehouse:
                for item in req.items.all():
                    issue_qty = item.actual_quantity if item.actual_quantity and item.actual_quantity > 0 else item.quantity
                    spec = item.spec or ''
                    inv = Inventory.objects.select_for_update().filter(warehouse=warehouse, material_name=item.material_name, spec=spec).first()
                    if inv:
                        inv.qty += issue_qty
                        inv.save()
        req.status = 'cancelled'
        req.save()
        serializer = MaterialRequisitionSerializer(req)
        return success_response(data=serializer.data, message='取消成功')


class ProductionInStockListCreateView(generics.ListCreateAPIView):
    queryset = ProductionInStock.objects.all().order_by('-id')
    serializer_class = ProductionInStockSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:instock:view'
    search_fields = ['stock_no', 'product_name']
    filterset_fields = ['status', 'warehouse']
    ordering_fields = ['id', 'stock_date', 'created_at']

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


# ==================== 生产工单状态流转 ====================

class ProductionOrderReleaseView(views.APIView):
    """下达工单：草稿 → 已下达"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:order:edit'

    def post(self, request, pk):
        try:
            order = ProductionOrder.objects.get(pk=pk)
        except ProductionOrder.DoesNotExist:
            return error_response(message='工单不存在', code=404)
        if order.status != 'draft':
            return error_response(message='只有草稿状态的工单可以下达', code=400)
        order.status = 'released'
        order.save()
        serializer = ProductionOrderSerializer(order)
        return success_response(data=serializer.data, message='下达成功')


class ProductionOrderStartView(views.APIView):
    """开工：已下达 → 生产中"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:order:edit'

    def post(self, request, pk):
        try:
            order = ProductionOrder.objects.get(pk=pk)
        except ProductionOrder.DoesNotExist:
            return error_response(message='工单不存在', code=404)
        if order.status != 'released':
            return error_response(message='只有已下达状态的工单可以开工', code=400)
        order.status = 'processing'
        order.actual_start_date = timezone.now().date()
        order.save()
        serializer = ProductionOrderSerializer(order)
        return success_response(data=serializer.data, message='开工成功')


class ProductionOrderCompleteView(views.APIView):
    """完工：生产中 → 已完成"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:order:edit'

    def post(self, request, pk):
        try:
            order = ProductionOrder.objects.get(pk=pk)
        except ProductionOrder.DoesNotExist:
            return error_response(message='工单不存在', code=404)
        if order.status != 'processing':
            return error_response(message='只有生产中的工单可以完工', code=400)
        order.status = 'completed'
        order.actual_end_date = timezone.now().date()
        order.completed_qty = order.quantity
        order.save()
        serializer = ProductionOrderSerializer(order)
        return success_response(data=serializer.data, message='完工成功')


class ProductionOrderCancelView(views.APIView):
    """取消工单"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:order:edit'

    def post(self, request, pk):
        try:
            order = ProductionOrder.objects.get(pk=pk)
        except ProductionOrder.DoesNotExist:
            return error_response(message='工单不存在', code=404)
        if order.status in ['completed', 'cancelled']:
            return error_response(message='已完工或已取消的工单无法再次取消', code=400)
        order.status = 'cancelled'
        order.save()
        serializer = ProductionOrderSerializer(order)
        return success_response(data=serializer.data, message='取消成功')


# ==================== 工单下推功能 ====================

class ProductionOrderCreateRequisitionView(views.APIView):
    """根据工单和BOM生成领料单"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:requisition:add'

    def post(self, request, pk):
        try:
            order = ProductionOrder.objects.select_related('bom').prefetch_related('bom__items').get(pk=pk)
        except ProductionOrder.DoesNotExist:
            return error_response(message='工单不存在', code=404)
        if order.status not in ['released', 'processing']:
            return error_response(message='只有已下达或生产中的工单可以生成领料单', code=400)
        if not order.bom:
            return error_response(message='工单未关联BOM，无法生成领料单', code=400)

        # 生成领料单号
        from datetime import datetime
        prefix = 'LL' + datetime.now().strftime('%Y%m%d')
        count = MaterialRequisition.objects.filter(requisition_no__startswith=prefix).count()
        req_no = f'{prefix}-{count + 1:03d}'

        req = MaterialRequisition.objects.create(
            requisition_no=req_no,
            production_order=order,
            requisition_date=timezone.now().date(),
            warehouse='默认仓库',
            operator=request.user,
            remark=f'由工单 {order.order_no} 自动生成',
        )

        # 根据BOM明细生成领料明细（用量 × 工单数量）
        for item in order.bom.items.all():
            MaterialRequisitionItem.objects.create(
                requisition=req,
                material_name=item.material_name,
                spec=item.spec,
                quantity=item.quantity * order.quantity,
                unit=item.unit,
                remark=item.remark,
            )

        serializer = MaterialRequisitionSerializer(req)
        return success_response(data=serializer.data, message='领料单生成成功')


class ProductionOrderCreateInStockView(views.APIView):
    """根据工单生成生产入库单"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:instock:add'

    def post(self, request, pk):
        try:
            order = ProductionOrder.objects.get(pk=pk)
        except ProductionOrder.DoesNotExist:
            return error_response(message='工单不存在', code=404)
        if order.status not in ['released', 'processing', 'completed']:
            return error_response(message='当前状态不允许生成入库单', code=400)

        # 生成入库单号
        from datetime import datetime
        prefix = 'RK' + datetime.now().strftime('%Y%m%d')
        count = ProductionInStock.objects.filter(stock_no__startswith=prefix).count()
        stock_no = f'{prefix}-{count + 1:03d}'

        instock = ProductionInStock.objects.create(
            stock_no=stock_no,
            production_order=order,
            stock_date=timezone.now().date(),
            warehouse='默认仓库',
            product_name=order.product_name,
            quantity=order.quantity,
            operator=request.user,
            remark=f'由工单 {order.order_no} 自动生成',
        )

        serializer = ProductionInStockSerializer(instock)
        return success_response(data=serializer.data, message='入库单生成成功')


# ==================== 生产入库状态流转 ====================

class ProductionInStockSubmitView(views.APIView):
    """提交入库单：草稿 → 待审核"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:instock:edit'

    def post(self, request, pk):
        try:
            instock = ProductionInStock.objects.get(pk=pk)
        except ProductionInStock.DoesNotExist:
            return error_response(message='入库单不存在', code=404)
        if instock.status != 'draft':
            return error_response(message='只有草稿状态的入库单可以提交', code=400)
        instock.status = 'pending'
        instock.save()
        serializer = ProductionInStockSerializer(instock)
        return success_response(data=serializer.data, message='提交成功')


class ProductionInStockApproveView(views.APIView):
    """审核入库单：待审核 → 已审核"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:instock:edit'

    def post(self, request, pk):
        try:
            instock = ProductionInStock.objects.get(pk=pk)
        except ProductionInStock.DoesNotExist:
            return error_response(message='入库单不存在', code=404)
        if instock.status != 'pending':
            return error_response(message='只有待审核状态的入库单可以审核', code=400)
        instock.status = 'approved'
        instock.auditor = request.user
        instock.audit_date = timezone.now()
        instock.save()
        serializer = ProductionInStockSerializer(instock)
        return success_response(data=serializer.data, message='审核通过')


class ProductionInStockConfirmView(views.APIView):
    """入库确认：已审核 → 已入库，同时增加库存"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:instock:edit'

    @transaction.atomic
    def post(self, request, pk):
        try:
            instock = ProductionInStock.objects.get(pk=pk)
        except ProductionInStock.DoesNotExist:
            return error_response(message='入库单不存在', code=404)
        if instock.status != 'approved':
            return error_response(message='只有已审核状态的入库单可以确认入库', code=400)

        # 增加库存（成品入库）
        from apps.inventory.models import Warehouse, Inventory
        warehouse = Warehouse.objects.filter(name=instock.warehouse).first()
        if not warehouse:
            return error_response(message=f'仓库 "{instock.warehouse}" 不存在，无法入库', code=400)

        # 查找或创建库存记录
        inv, created = Inventory.objects.get_or_create(
            warehouse=warehouse,
            material_name=instock.product_name,
            defaults={'spec': '', 'unit': '件', 'qty': 0}
        )
        inv.qty += instock.quantity
        inv.save()

        instock.status = 'confirmed'
        instock.actual_quantity = instock.quantity
        instock.confirm_date = timezone.now()
        instock.save()
        serializer = ProductionInStockSerializer(instock)
        return success_response(data=serializer.data, message='入库确认成功')


class ProductionInStockCancelView(views.APIView):
    """取消入库单"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'production:instock:edit'

    @transaction.atomic
    def post(self, request, pk):
        try:
            instock = ProductionInStock.objects.get(pk=pk)
        except ProductionInStock.DoesNotExist:
            return error_response(message='入库单不存在', code=404)
        if instock.status == 'cancelled':
            return error_response(message='已取消的入库单无法再次取消', code=400)
        # 已入库的取消时回滚库存
        if instock.status == 'confirmed':
            from apps.inventory.models import Warehouse, Inventory
            warehouse = Warehouse.objects.filter(name=instock.warehouse).first()
            if warehouse:
                inv = Inventory.objects.select_for_update().filter(warehouse=warehouse, material_name=instock.product_name, spec='').first()
                if inv:
                    inv.qty -= instock.actual_quantity if instock.actual_quantity else instock.quantity
                    if inv.qty < 0:
                        inv.qty = 0
                    inv.save()
        instock.status = 'cancelled'
        instock.save()
        serializer = ProductionInStockSerializer(instock)
        return success_response(data=serializer.data, message='取消成功')
