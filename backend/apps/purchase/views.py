from io import BytesIO

from django.db.models import ProtectedError
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
    queryset = Supplier.objects.all().order_by('-id')
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
        try:
            instance.is_active = False
            instance.save()
        except ProtectedError:
            raise error_response(message='该供应商已被采购订单引用，无法删除', code=400)


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
        queryset = Supplier.objects.all().order_by('-id')
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


class PurchaseOrderListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
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


class PurchaseInStockListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = PurchaseInStock.objects.all().order_by('-id')
    serializer_class = PurchaseInStockSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'purchase:instock:view'
    search_fields = ['stock_no', 'order__order_no']

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
