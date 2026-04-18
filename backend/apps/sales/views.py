from rest_framework import generics, views, status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from apps.system.permissions import RBACPermission
from utils.response import success_response, error_response

from apps.sales.models import Customer, SalesOrder, SalesOutStock, SalesReturn
from apps.sales.serializers import (
    CustomerSerializer, CustomerListSerializer, SalesOrderSerializer,
    SalesOutStockSerializer, SalesReturnSerializer
)


class CustomerListCreateView(generics.ListCreateAPIView):
    """
    客户列表 / 新增
    GET  -> 列表（支持搜索 name、code、contact、phone；支持筛选 is_active、level、industry）
    POST -> 新增客户
    """
    queryset = Customer.objects.all().order_by('-id')
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:customer:view'
    search_fields = ['name', 'code', 'contact', 'phone', 'email', 'industry']
    filterset_fields = ['is_active', 'level', 'industry']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomerListSerializer
        return CustomerSerializer

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


class CustomerStatsView(views.APIView):
    """
    客户统计信息：订单数、订单总金额、出库金额、退货金额
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:customer:view'

    def get(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return error_response(message='客户不存在', code=404)

        order_stats = SalesOrder.objects.filter(customer=customer).aggregate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        )
        outstock_total = SalesOutStock.objects.filter(order__customer=customer).count()
        return_total = SalesReturn.objects.filter(customer=customer).aggregate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        )

        data = {
            'customer_id': customer.id,
            'customer_name': customer.name,
            'order_count': order_stats['count'] or 0,
            'order_total_amount': str(order_stats['total_amount'] or 0),
            'outstock_count': outstock_total,
            'return_count': return_total['count'] or 0,
            'return_total_amount': str(return_total['total_amount'] or 0),
        }
        return success_response(data=data)


class CustomerDetailStatsView(views.APIView):
    """
    客户详情页数据：基本信息 + 最近订单/出库/退货记录
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:customer:view'

    def get(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return error_response(message='客户不存在', code=404)

        # 基本信息
        base_info = CustomerSerializer(customer).data

        # 最近5条销售订单
        recent_orders = SalesOrder.objects.filter(customer=customer).order_by('-id')[:5]
        order_data = []
        for o in recent_orders:
            order_data.append({
                'id': o.id,
                'order_no': o.order_no,
                'order_date': o.order_date,
                'status': o.status,
                'status_display': o.get_status_display(),
                'total_amount': str(o.total_amount),
            })

        # 最近5条出库记录
        recent_outstocks = SalesOutStock.objects.filter(order__customer=customer).order_by('-id')[:5]
        outstock_data = []
        for s in recent_outstocks:
            outstock_data.append({
                'id': s.id,
                'stock_no': s.stock_no,
                'stock_date': s.stock_date,
                'warehouse': s.warehouse,
            })

        # 最近5条退货记录
        recent_returns = SalesReturn.objects.filter(customer=customer).order_by('-id')[:5]
        return_data = []
        for r in recent_returns:
            return_data.append({
                'id': r.id,
                'return_no': r.return_no,
                'return_date': r.return_date,
                'total_amount': str(r.total_amount),
            })

        data = {
            'base_info': base_info,
            'recent_orders': order_data,
            'recent_outstocks': outstock_data,
            'recent_returns': return_data,
        }
        return success_response(data=data)


class CustomerExportView(views.APIView):
    """
    导出客户列表到 Excel
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:customer:view'

    def get(self, request):
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
        import io

        queryset = Customer.objects.all().order_by('-id')
        # 应用搜索和筛选（复用视图逻辑）
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search) |
                Q(contact__icontains=search) | Q(phone__icontains=search) |
                Q(email__icontains=search) | Q(industry__icontains=search)
            )
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        level = request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        industry = request.query_params.get('industry')
        if industry:
            queryset = queryset.filter(industry__icontains=industry)

        wb = Workbook()
        ws = wb.active
        ws.title = '客户列表'

        headers = ['客户编码', '客户名称', '联系人', '联系电话', '邮箱', '地址',
                   '所属行业', '客户等级', '信用额度', '税号', '银行信息', '状态', '备注']
        ws.append(headers)

        # 表头样式
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        for customer in queryset:
            ws.append([
                customer.code, customer.name, customer.contact or '',
                customer.phone or '', customer.email or '', customer.address or '',
                customer.industry or '', customer.get_level_display(),
                float(customer.credit_limit) if customer.credit_limit else 0,
                customer.tax_no or '', customer.bank_info or '',
                '启用' if customer.is_active else '禁用',
                customer.remark or '',
            ])

        # 设置边框和列宽
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=len(headers)):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(vertical='center')

        col_widths = [14, 20, 12, 14, 20, 30, 12, 14, 12, 22, 30, 8, 20]
        for i, w in enumerate(col_widths, 1):
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=customers.xlsx'
        return response


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
