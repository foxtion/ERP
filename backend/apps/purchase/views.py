from io import BytesIO

from django.db.models import ProtectedError
from django.db import transaction
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from rest_framework import generics, views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from apps.system.permissions import RBACPermission
from apps.system.views import CreateResponseMixin, RUDResponseMixin
from utils.response import success_response, error_response
from utils.pagination import StandardPagination

from apps.purchase.models import (
    Supplier, PurchaseRequest, PurchaseOrder, PurchaseInStock
)
from apps.purchase.serializers import (
    SupplierSerializer, PurchaseRequestSerializer,
    PurchaseOrderSerializer, PurchaseInStockSerializer
)
from apps.purchase.filters import SupplierFilter


class SupplierListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = Supplier.objects.filter(is_active=True).order_by('-id')
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:supplier:view'
    pagination_class = StandardPagination
    filterset_class = SupplierFilter

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'purchase:supplier:add'
        return super().get_permissions()


class SupplierRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
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


class SupplierToggleStatusView(views.APIView):
    """
    切换供应商启用/禁用状态
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:supplier:edit'

    def post(self, request, pk):
        try:
            supplier = Supplier.objects.get(pk=pk)
            supplier.is_active = not supplier.is_active
            supplier.save()
            return success_response(
                data={'id': pk, 'is_active': supplier.is_active},
                message='状态更新成功'
            )
        except Supplier.DoesNotExist:
            return error_response(message='供应商不存在', code=404)


class SupplierExportView(views.APIView):
    """
    导出供应商列表为 Excel
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:supplier:view'

    def get(self, request):
        queryset = Supplier.objects.filter(is_active=True).order_by('-id')
        keyword = request.query_params.get('keyword')
        is_active = request.query_params.get('is_active')
        if keyword:
            queryset = queryset.filter(
                code__icontains=keyword
            ) | queryset.filter(
                name__icontains=keyword
            ) | queryset.filter(
                contact__icontains=keyword
            ) | queryset.filter(
                phone__icontains=keyword
            )
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        wb = Workbook()
        ws = wb.active
        ws.title = '供应商列表'

        headers = ['供应商编码', '供应商名称', '联系人', '联系电话', '地址', '状态', '备注']
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')

        for supplier in queryset:
            ws.append([
                supplier.code,
                supplier.name,
                supplier.contact or '',
                supplier.phone or '',
                supplier.address or '',
                '启用' if supplier.is_active else '禁用',
                supplier.remark or '',
            ])

        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        from django.http import HttpResponse
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="suppliers.xlsx"'
        return response


class SupplierImportView(views.APIView):
    """
    从 Excel 导入供应商
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:supplier:add'
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return error_response(message='请上传文件', code=400)

        try:
            from openpyxl import load_workbook
            wb = load_workbook(file)
            ws = wb.active
        except Exception as e:
            return error_response(message=f'文件解析失败: {str(e)}', code=400)

        expected_headers = ['供应商编码', '供应商名称', '联系人', '联系电话', '地址', '状态', '备注']
        headers = [cell.value for cell in ws[1]]
        if headers[:len(expected_headers)] != expected_headers:
            return error_response(
                message=f'表头格式不正确，期望: {", ".join(expected_headers)}',
                code=400
            )

        created_count = 0
        updated_count = 0
        errors = []

        for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            code, name, contact, phone, address, status_val, remark = row[:7]
            if not code or not name:
                errors.append(f'第 {idx} 行: 编码和名称不能为空')
                continue

            is_active = True
            if status_val and str(status_val).strip() == '禁用':
                is_active = False

            defaults = {
                'name': str(name).strip(),
                'contact': str(contact).strip() if contact else None,
                'phone': str(phone).strip() if phone else None,
                'address': str(address).strip() if address else None,
                'is_active': is_active,
                'remark': str(remark).strip() if remark else None,
            }

            supplier, created = Supplier.objects.update_or_create(
                code=str(code).strip(),
                defaults=defaults
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        return success_response(data={
            'created': created_count,
            'updated': updated_count,
            'errors': errors,
        }, message='导入完成')


class PurchaseRequestListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = PurchaseRequest.objects.all().order_by('-id')
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:request:view'
    search_fields = ['request_no']
    filterset_fields = ['status']
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'purchase:request:add'
        return super().get_permissions()


class PurchaseRequestRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'draft':
            return error_response(message='只有草稿状态的申请单可以编辑', code=400)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'draft':
            return error_response(message='只有草稿状态的申请单可以删除', code=400)
        return super().destroy(request, *args, **kwargs)


class PurchaseRequestSubmitView(views.APIView):
    """提交采购申请：draft → pending"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:request:edit'

    def post(self, request, pk):
        try:
            req = PurchaseRequest.objects.get(pk=pk)
        except PurchaseRequest.DoesNotExist:
            return error_response(message='采购申请不存在', code=404)
        if req.status != 'draft':
            return error_response(message='只有草稿状态的申请单可以提交', code=400)
        req.status = 'pending'
        req.save()
        return success_response(data={'id': pk, 'status': req.status}, message='提交成功')


class PurchaseRequestApproveView(views.APIView):
    """审批采购申请：pending → approved"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:request:edit'

    def post(self, request, pk):
        try:
            req = PurchaseRequest.objects.get(pk=pk)
        except PurchaseRequest.DoesNotExist:
            return error_response(message='采购申请不存在', code=404)
        if req.status != 'pending':
            return error_response(message='只有待审批状态的申请单可以审批', code=400)
        req.status = 'approved'
        req.save()
        return success_response(data={'id': pk, 'status': req.status}, message='审批通过')


class PurchaseRequestRejectView(views.APIView):
    """驳回采购申请：pending → draft"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:request:edit'

    def post(self, request, pk):
        try:
            req = PurchaseRequest.objects.get(pk=pk)
        except PurchaseRequest.DoesNotExist:
            return error_response(message='采购申请不存在', code=404)
        if req.status != 'pending':
            return error_response(message='只有待审批状态的申请单可以驳回', code=400)
        req.status = 'draft'
        req.save()
        return success_response(data={'id': pk, 'status': req.status}, message='已驳回')


class PurchaseOrderListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all().order_by('-id')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:order:view'
    search_fields = ['order_no', 'supplier__name']
    filterset_fields = ['status']
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'purchase:order:add'
        return super().get_permissions()


class PurchaseOrderRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'draft':
            return error_response(message='只有草稿状态的订单可以编辑', code=400)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'draft':
            return error_response(message='只有草稿状态的订单可以删除', code=400)
        return super().destroy(request, *args, **kwargs)


class PurchaseInStockListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = PurchaseInStock.objects.all().order_by('-id')
    serializer_class = PurchaseInStockSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:instock:view'
    search_fields = ['stock_no', 'order__order_no']
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'purchase:instock:add'
        return super().get_permissions()


class PurchaseInStockRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
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


class PurchaseOrderConfirmView(views.APIView):
    """
    确认采购订单：draft -> confirmed
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:order:edit'

    def post(self, request, pk):
        try:
            order = PurchaseOrder.objects.get(pk=pk)
        except PurchaseOrder.DoesNotExist:
            return error_response(message='采购订单不存在', code=404)
        if order.status != 'draft':
            return error_response(message='只有草稿状态的订单可以确认', code=400)
        order.status = 'confirmed'
        order.save()
        return success_response(data={'id': pk, 'status': order.status}, message='订单确认成功')


class PurchaseOrderCancelView(views.APIView):
    """
    取消采购订单：draft/confirmed -> cancelled
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:order:edit'

    def post(self, request, pk):
        try:
            order = PurchaseOrder.objects.get(pk=pk)
        except PurchaseOrder.DoesNotExist:
            return error_response(message='采购订单不存在', code=404)
        if order.status not in ('draft', 'confirmed'):
            return error_response(message='只有草稿或已确认状态的订单可以取消', code=400)
        # 校验是否已有入库记录
        if order.purchaseinstock_set.exists():
            return error_response(message='该订单已存在入库记录，不能取消', code=400)
        order.status = 'cancelled'
        order.save()
        return success_response(data={'id': pk, 'status': order.status}, message='订单取消成功')


class PurchaseOrderCompleteView(views.APIView):
    """
    手动完成采购订单：confirmed/partial -> completed
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:order:edit'

    def post(self, request, pk):
        try:
            order = PurchaseOrder.objects.get(pk=pk)
        except PurchaseOrder.DoesNotExist:
            return error_response(message='采购订单不存在', code=404)
        if order.status not in ('confirmed', 'partial'):
            return error_response(message='只有已确认或部分入库状态的订单可以手动完成', code=400)
        # 校验是否全部入库
        for item in order.items.all():
            if (item.received_qty or 0) < (item.quantity or 0):
                return error_response(message='订单仍有未入库物料，不能手动完成', code=400)
        order.status = 'completed'
        order.save()
        return success_response(data={'id': pk, 'status': order.status}, message='订单已完成')


class PurchaseOrderExportView(views.APIView):
    """
    导出采购订单列表为 Excel（含明细）
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:order:view'

    def get(self, request):
        queryset = PurchaseOrder.objects.all().order_by('-id')
        keyword = request.query_params.get('keyword')
        status = request.query_params.get('status')
        if keyword:
            queryset = queryset.filter(order_no__icontains=keyword) | queryset.filter(supplier__name__icontains=keyword)
        if status:
            queryset = queryset.filter(status=status)

        wb = Workbook()
        ws = wb.active
        ws.title = '采购订单列表'

        headers = ['订单编号', '供应商', '来源申请单', '订单日期', '交货日期', '状态', '总金额', '采购员', '备注']
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')

        status_map = dict(PurchaseOrder.STATUS_CHOICES)
        for order in queryset:
            ws.append([
                order.order_no,
                order.supplier.name if order.supplier else '',
                order.request.request_no if order.request else '',
                str(order.order_date) if order.order_date else '',
                str(order.delivery_date) if order.delivery_date else '',
                status_map.get(order.status, order.status),
                float(order.total_amount) if order.total_amount else 0,
                order.purchaser.username if order.purchaser else '',
                order.remark or '',
            ])

        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        from django.http import HttpResponse
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="purchase_orders.xlsx"'
        return response


class PurchaseRequestConvertView(views.APIView):
    """
    将已批准的采购申请转为采购订单
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:order:add'

    @transaction.atomic
    def post(self, request, pk):
        try:
            req = PurchaseRequest.objects.prefetch_related('items').get(pk=pk)
        except PurchaseRequest.DoesNotExist:
            return error_response(message='采购申请不存在', code=404)
        if req.status != 'approved':
            return error_response(message='只有已批准的申请单可以转采购订单', code=400)

        data = request.data
        order_no = data.get('order_no')
        supplier_id = data.get('supplier')
        order_date = data.get('order_date')
        delivery_date = data.get('delivery_date')
        remark = data.get('remark', '')

        if not order_no or not supplier_id or not order_date:
            return error_response(message='订单编号、供应商、订单日期为必填项', code=400)

        from apps.purchase.models import Supplier, PurchaseOrder, PurchaseOrderItem
        try:
            supplier = Supplier.objects.get(pk=supplier_id)
        except Supplier.DoesNotExist:
            return error_response(message='供应商不存在', code=400)

        if not supplier.is_active:
            return error_response(message='该供应商已被禁用，不能下订单', code=400)

        if PurchaseOrder.objects.filter(order_no=order_no).exists():
            return error_response(message='订单编号已存在', code=400)

        order = PurchaseOrder.objects.create(
            order_no=order_no,
            supplier=supplier,
            request=req,
            order_date=order_date,
            delivery_date=delivery_date or None,
            remark=remark,
            purchaser=request.user,
            status='draft',
        )

        total = 0
        for ri in req.items.all():
            oi = PurchaseOrderItem.objects.create(
                order=order,
                material_name=ri.material_name,
                spec=ri.spec,
                quantity=ri.quantity,
                unit=ri.unit,
                price=ri.estimated_price,
                remark=ri.remark,
            )
            total += oi.amount

        order.total_amount = total
        order.save()

        req.status = 'ordered'
        req.save()

        serializer = PurchaseOrderSerializer(order)
        return success_response(data=serializer.data, message='转单成功')
