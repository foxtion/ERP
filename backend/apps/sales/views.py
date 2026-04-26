from decimal import Decimal

from rest_framework import generics, views, status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from apps.system.permissions import RBACPermission
from apps.system.views import CreateResponseMixin, RUDResponseMixin
from utils.response import success_response, error_response
from utils.pagination import StandardPagination

from apps.sales.models import Customer, SalesOrder, SalesOutStock, SalesReturn, SalesPickingList, SalesPickingListItem
from apps.sales.serializers import (
    CustomerSerializer, CustomerListSerializer, SalesOrderSerializer,
    SalesOutStockSerializer, SalesReturnSerializer,
    SalesPickingListSerializer, SalesPickingListItemSerializer,
    generate_order_no
)


class CustomerListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    """
    客户列表 / 新增
    """
    queryset = Customer.objects.filter(is_active=True).order_by('-id')
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:customer:view'
    search_fields = ['name', 'code', 'contact', 'phone', 'email', 'industry']
    filterset_fields = ['is_active', 'level', 'industry', 'allow_partial_shipment']
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomerListSerializer
        return CustomerSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'sales:customer:add'
        return super().get_permissions()


class CustomerRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
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

        base_info = CustomerSerializer(customer).data

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

        recent_outstocks = SalesOutStock.objects.filter(order__customer=customer).order_by('-id')[:5]
        outstock_data = []
        for s in recent_outstocks:
            outstock_data.append({
                'id': s.id,
                'stock_no': s.stock_no,
                'stock_date': s.stock_date,
                'warehouse': s.warehouse,
            })

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

        queryset = Customer.objects.filter(is_active=True).order_by('-id')
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


class SalesOrderListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = SalesOrder.objects.all().order_by('-id')
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:order:view'
    search_fields = ['order_no', 'customer__name']
    filterset_fields = ['status']
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'sales:order:add'
        return super().get_permissions()


class SalesOrderRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
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


class SalesOrderConfirmView(views.APIView):
    """确认销售订单：draft → confirmed"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:order:edit'

    def post(self, request, pk):
        try:
            order = SalesOrder.objects.get(pk=pk)
        except SalesOrder.DoesNotExist:
            return error_response(message='销售订单不存在', code=404)
        if order.status != 'draft':
            return error_response(message='只有草稿状态的订单可以确认', code=400)
        # 信用额度校验
        customer = order.customer
        if customer and customer.credit_limit and customer.credit_limit > 0:
            from decimal import Decimal
            existing_unpaid = Decimal('0')
            from apps.finance.models import ReceivablePayable
            unpaid = ReceivablePayable.objects.filter(
                counterparty=customer.name, doc_type='receivable'
            ).exclude(status='paid').aggregate(t=Sum('amount'))['t']
            if unpaid:
                existing_unpaid = Decimal(str(unpaid))
            if existing_unpaid + (order.total_amount or Decimal('0')) > customer.credit_limit:
                return error_response(
                    message=f'客户信用额度不足，当前已用 {existing_unpaid}，额度 {customer.credit_limit}，本次订单 {order.total_amount}',
                    code=400
                )
        order.status = 'confirmed'
        order.save()
        return success_response(data={'id': pk, 'status': order.status}, message='订单确认成功')


class SalesOrderCancelView(views.APIView):
    """取消销售订单：draft/confirmed → cancelled"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:order:edit'

    def post(self, request, pk):
        try:
            order = SalesOrder.objects.get(pk=pk)
        except SalesOrder.DoesNotExist:
            return error_response(message='销售订单不存在', code=404)
        if order.status not in ('draft', 'confirmed'):
            return error_response(message='只有草稿或已确认状态的订单可以取消', code=400)
        # 校验是否已有出库记录
        if order.salesoutstock_set.exists():
            return error_response(message='该订单已存在出库记录，不能取消', code=400)
        order.status = 'cancelled'
        order.save()
        return success_response(data={'id': pk, 'status': order.status}, message='订单取消成功')


class SalesOrderCompleteView(views.APIView):
    """手动完成销售订单：confirmed/partial → completed"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:order:edit'

    def post(self, request, pk):
        try:
            order = SalesOrder.objects.get(pk=pk)
        except SalesOrder.DoesNotExist:
            return error_response(message='销售订单不存在', code=404)
        if order.status not in ('confirmed', 'partial'):
            return error_response(message='只有已确认或部分出库状态的订单可以手动完成', code=400)
        for item in order.items.all():
            if (item.delivered_qty or 0) < (item.quantity or 0):
                return error_response(message='订单仍有未出库物料，不能手动完成', code=400)
        order.status = 'completed'
        order.save()
        return success_response(data={'id': pk, 'status': order.status}, message='订单已完成')


class SalesOrderExportView(views.APIView):
    """
    导出销售订单列表到 Excel
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:order:view'

    def get(self, request):
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
        import io

        queryset = SalesOrder.objects.all().order_by('-id')
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_no__icontains=search) | Q(customer__name__icontains=search)
            )
        status = request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        wb = Workbook()
        ws = wb.active
        ws.title = '销售订单'

        headers = ['订单编号', '客户', '订单日期', '交货日期', '状态', '总金额', '销售员', '备注']
        ws.append(headers)

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

        status_map = {
            'draft': '草稿',
            'confirmed': '已确认',
            'partial': '部分出库',
            'completed': '已完成',
            'cancelled': '已取消',
        }

        for order in queryset:
            ws.append([
                order.order_no,
                order.customer.name if order.customer else '',
                str(order.order_date) if order.order_date else '',
                str(order.delivery_date) if order.delivery_date else '',
                status_map.get(order.status, order.status),
                float(order.total_amount) if order.total_amount else 0,
                order.salesman.username if order.salesman else '',
                order.remark or '',
            ])

        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=len(headers)):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(vertical='center')

        col_widths = [20, 20, 12, 12, 10, 12, 12, 30]
        for i, w in enumerate(col_widths, 1):
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=sales_orders.xlsx'
        return response


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


class PendingOutStockOrderView(views.APIView):
    """
    待出库订单列表（收货员作业用）
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:outstock:view'

    def get(self, request):
        from apps.inventory.models import Inventory
        queryset = SalesOrder.objects.filter(status__in=['confirmed', 'partial']).order_by('-id')
        data = []
        for order in queryset:
            items = []
            for item in order.items.all():
                remaining = (item.quantity or 0) - (item.delivered_qty or 0)
                if remaining <= 0:
                    continue
                inv = Inventory.objects.filter(material_name=item.material_name, spec=item.spec or '').first()
                stock_qty = inv.qty if inv else 0
                items.append({
                    'id': item.id,
                    'material_code': item.material_code or '',
                    'material_name': item.material_name,
                    'spec': item.spec,
                    'quantity': str(item.quantity),
                    'delivered_qty': str(item.delivered_qty),
                    'remaining': str(remaining),
                    'unit': item.unit,
                    'stock_qty': str(stock_qty),
                })
            if items:
                data.append({
                    'id': order.id,
                    'order_no': order.order_no,
                    'customer_name': order.customer.name,
                    'customer_id': order.customer.id,
                    'allow_partial_shipment': order.customer.allow_partial_shipment,
                    'order_date': order.order_date,
                    'status': order.status,
                    'status_display': order.get_status_display(),
                    'items': items,
                })
        return success_response(data=data)


class OrderOutStockItemsView(views.APIView):
    """
    获取单个订单的可出库明细
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:outstock:view'

    def get(self, request, pk):
        from apps.inventory.models import Inventory
        try:
            order = SalesOrder.objects.get(pk=pk)
        except SalesOrder.DoesNotExist:
            return error_response(message='订单不存在', code=404)

        items = []
        for item in order.items.all():
            remaining = (item.quantity or 0) - (item.delivered_qty or 0)
            inv = Inventory.objects.filter(material_name=item.material_name, spec=item.spec or '').first()
            stock_qty = inv.qty if inv else 0
            items.append({
                'id': item.id,
                'material_code': item.material_code or '',
                'material_name': item.material_name,
                'spec': item.spec,
                'quantity': str(item.quantity),
                'delivered_qty': str(item.delivered_qty),
                'remaining': str(remaining),
                'unit': item.unit,
                'stock_qty': str(stock_qty),
            })

        return success_response(data={
            'id': order.id,
            'order_no': order.order_no,
            'customer_name': order.customer.name,
            'customer_id': order.customer.id,
            'allow_partial_shipment': order.customer.allow_partial_shipment,
            'items': items,
        })


class SalesOutStockListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = SalesOutStock.objects.all().order_by('-id')
    serializer_class = SalesOutStockSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:outstock:view'
    search_fields = ['stock_no', 'order__order_no']
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'sales:outstock:add'
        return super().get_permissions()


class SalesOutStockRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
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


class SalesReturnListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = SalesReturn.objects.all().order_by('-id')
    serializer_class = SalesReturnSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:return:view'
    search_fields = ['return_no', 'customer__name']
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'sales:return:add'
        return super().get_permissions()


class SalesReturnRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
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


# ==================== 拣货单 ====================

class SalesPickingListListCreateView(CreateResponseMixin, generics.ListCreateAPIView):
    queryset = SalesPickingList.objects.all().order_by('-id')
    serializer_class = SalesPickingListSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:picking:view'
    search_fields = ['picking_no', 'order__order_no']
    filterset_fields = ['status', 'warehouse', 'assigned_to', 'picker']
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'sales:picking:add'
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        # 非管理员只能看到：指派给自己的 + 未指派的（可以指派给别人）
        if not user.is_superuser:
            queryset = queryset.filter(
                Q(assigned_to=user) | Q(assigned_to__isnull=True)
            )
        # 按创建时间范围查询
        created_at_start = self.request.query_params.get('created_at_start')
        created_at_end = self.request.query_params.get('created_at_end')
        if created_at_start:
            queryset = queryset.filter(created_at__date__gte=created_at_start)
        if created_at_end:
            queryset = queryset.filter(created_at__date__lte=created_at_end)
        # 按员工姓名模糊查询（指派员工或实际拿货人）
        user_name = self.request.query_params.get('user_name')
        if user_name:
            queryset = queryset.filter(
                Q(assigned_to__username__icontains=user_name) | Q(picker__username__icontains=user_name)
            )
        return queryset


class SalesPickingListRetrieveUpdateDestroyView(RUDResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = SalesPickingList.objects.all()
    serializer_class = SalesPickingListSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'sales:picking:edit'
        elif method == 'DELETE':
            self.required_permission = 'sales:picking:delete'
        # GET / Retrieve 不再强制要求 sales:picking:view 权限，
        # 出货员/拣货员只要能登录就能查看被指派的拣货单详情
        return super().get_permissions()


class SalesOrderCreatePickingView(views.APIView):
    """
    从销售订单生成拣货单：自动复制订单明细并匹配库位
    POST /orders/<pk>/create-picking/
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:picking:add'

    def post(self, request, pk):
        from apps.inventory.models import WarehouseLocation
        try:
            order = SalesOrder.objects.prefetch_related('items').get(pk=pk)
        except SalesOrder.DoesNotExist:
            return error_response(message='销售订单不存在', code=404)

        if order.status not in ('confirmed', 'partial'):
            return error_response(message='只有已确认或部分出库的订单可以生成拣货单', code=400)

        # 检查是否已有未完成的拣货单
        existing = SalesPickingList.objects.filter(order=order).exclude(status__in=['done', 'cancelled']).first()
        if existing:
            return error_response(message=f'该订单已有未完成的拣货单 {existing.picking_no}', code=400)

        picking_no = generate_order_no('JH', model=SalesPickingList, field='picking_no')
        picking = SalesPickingList.objects.create(
            picking_no=picking_no,
            order=order,
            status='pending',
            warehouse='默认仓库',
        )

        for order_item in order.items.all():
            remaining = (order_item.quantity or Decimal('0')) - (order_item.delivered_qty or Decimal('0'))
            if remaining <= 0:
                continue

            # 匹配库位
            location_code = ''
            if order_item.material_code:
                loc = WarehouseLocation.objects.filter(
                    product_code=order_item.material_code,
                    is_empty=False
                ).first()
                if loc:
                    location_code = loc.location_code

            # 匹配物料图片
            image = ''
            from apps.inventory.models import Material
            mat = Material.objects.filter(code=order_item.material_code or '').first()
            if mat:
                image = ''  # 物料档案目前没有图片字段，预留

            SalesPickingListItem.objects.create(
                picking_list=picking,
                order_item=order_item,
                material_code=order_item.material_code,
                material_name=order_item.material_name,
                spec=order_item.spec,
                quantity=remaining,
                unit=order_item.unit,
                location_code=location_code,
                image=image,
            )

        return success_response(
            data=SalesPickingListSerializer(picking).data,
            message='拣货单生成成功'
        )


class SalesPickingListAssignView(views.APIView):
    """
    指派拣货单给员工
    POST /pickings/<pk>/assign/  {assignee_id}
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:picking:assign'

    def post(self, request, pk):
        from apps.system.models import User
        try:
            picking = SalesPickingList.objects.get(pk=pk)
        except SalesPickingList.DoesNotExist:
            return error_response(message='拣货单不存在', code=404)

        if picking.status not in ('pending', 'assigned'):
            return error_response(message='该拣货单当前状态不可指派', code=400)

        assignee_id = request.data.get('assignee_id')
        if not assignee_id:
            return error_response(message='请选择指派员工', code=400)

        try:
            assignee = User.objects.get(pk=assignee_id)
        except User.DoesNotExist:
            return error_response(message='员工不存在', code=404)

        picking.assigned_to = assignee
        picking.status = 'assigned'
        picking.save()
        return success_response(data=SalesPickingListSerializer(picking).data, message='指派成功')


class SalesPickingListAcceptView(views.APIView):
    """
    员工接单
    POST /pickings/<pk>/accept/
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:picking:job'

    def post(self, request, pk):
        try:
            picking = SalesPickingList.objects.get(pk=pk)
        except SalesPickingList.DoesNotExist:
            return error_response(message='拣货单不存在', code=404)

        if picking.status != 'assigned':
            return error_response(message='该拣货单当前状态不可接单', code=400)

        picking.picker = request.user
        picking.status = 'picking'
        picking.save()
        return success_response(data=SalesPickingListSerializer(picking).data, message='接单成功')


class SalesPickingListPickItemView(views.APIView):
    """
    标记拣货明细已拿/缺货
    POST /pickings/<pk>/pick-item/  {item_id, picked_qty, shortage_qty}
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:picking:job'

    def post(self, request, pk):
        try:
            picking = SalesPickingList.objects.get(pk=pk)
        except SalesPickingList.DoesNotExist:
            return error_response(message='拣货单不存在', code=404)

        # 只有已完成的拣货单才禁止继续操作
        if picking.status in ('done', 'cancelled'):
            return error_response(message='该拣货单当前不可操作', code=400)

        item_id = request.data.get('item_id')
        if not item_id:
            return error_response(message='缺少 item_id 参数', code=400)

        picked_qty_raw = request.data.get('picked_qty')
        shortage_qty_raw = request.data.get('shortage_qty')
        try:
            def _to_decimal(v):
                if v is None or v == '':
                    return Decimal('0')
                if isinstance(v, bool):
                    return Decimal('1') if v else Decimal('0')
                return Decimal(str(v))
            picked_qty = _to_decimal(picked_qty_raw)
            shortage_qty = _to_decimal(shortage_qty_raw)
        except Exception as e:
            return error_response(
                message=f'数量格式不正确: picked_qty={picked_qty_raw!r}({type(picked_qty_raw).__name__}), shortage_qty={shortage_qty_raw!r}({type(shortage_qty_raw).__name__}), 错误: {e}',
                code=400
            )

        try:
            item = SalesPickingListItem.objects.get(pk=item_id, picking_list=picking)
        except (SalesPickingListItem.DoesNotExist, ValueError):
            return error_response(message='拣货明细不存在', code=404)

        if item.status == 'refunded':
            return error_response(message='该商品已退款，不可操作', code=400)

        if picked_qty < 0 or shortage_qty < 0:
            return error_response(message='数量不能为负数', code=400)

        item_qty = item.quantity or Decimal('0')
        if picked_qty + shortage_qty > item_qty:
            return error_response(
                message=f'实际拿到({picked_qty}) + 缺货({shortage_qty}) 超过需拿数量({item_qty})',
                code=400
            )

        # 如果之前是缺货状态，本次点击"已拿"时先清零缺货数量（补货后继续拣货）
        if item.status == 'shortage' and picked_qty > 0:
            item.shortage_qty = Decimal('0')

        # 累加模式：本次录入的数量叠加到已有数量上
        new_picked = (item.picked_qty or Decimal('0')) + picked_qty
        new_shortage = (item.shortage_qty or Decimal('0')) + shortage_qty

        if new_picked + new_shortage > item_qty:
            return error_response(
                message=f'累计已拿({new_picked}) + 累计缺货({new_shortage}) 超过需拿数量({item_qty})',
                code=400
            )

        # 判断是否是本次新产生的缺货（之前 shortage 为 0，现在 > 0）
        is_new_shortage = (item.shortage_qty or Decimal('0')) == 0 and new_shortage > 0

        item.picked_qty = new_picked
        item.shortage_qty = new_shortage
        if new_shortage > 0:
            item.status = 'shortage'
        elif new_picked >= item_qty:
            item.status = 'picked'
        else:
            item.status = 'pending'
        item.save()

        # 本次新产生缺货时，自动创建库存预警
        if is_new_shortage:
            from apps.inventory.models import StockWarning, Warehouse, Material
            warehouse = Warehouse.objects.filter(name=picking.warehouse).first()
            material = Material.objects.filter(code=item.material_code).first()
            StockWarning.objects.create(
                material=material,
                material_code=item.material_code or '',
                material_name=item.material_name,
                picking_item_id=item.id,
                warehouse=warehouse,
                current_qty=0,
                threshold=0,
                status='urgent',
                warning_type='picking_shortage',
                remark=f'拣货单 {picking.picking_no} 缺货：{item.material_name} ({item.material_code or ""})，库位 {item.location_code or ""}',
            )

        # 更新拣货单状态
        self._update_picking_status(picking)
        return success_response(data=SalesPickingListSerializer(picking).data, message='操作成功')

    def _update_picking_status(self, picking):
        items = picking.items.all()
        has_shortage = any((i.shortage_qty or 0) > 0 for i in items)
        # 排除已退款的商品后再判断是否全部拿齐
        active_items = [i for i in items if i.status != 'refunded']
        all_picked = len(active_items) > 0 and all((i.picked_qty or 0) >= (i.quantity or 0) for i in active_items)
        # 是否所有商品都已处理完毕（已拿完 或 已标记缺货 或 已退款）
        all_done = all(
            (i.picked_qty or 0) >= (i.quantity or 0) or (i.shortage_qty or 0) > 0 or i.status == 'refunded'
            for i in items
        )

        if all_picked:
            picking.status = 'complete'
        elif all_done and has_shortage:
            picking.status = 'shortage'
        else:
            # 还有商品未处理完，保持 picking 状态以便继续作业
            picking.status = 'picking'
        picking.save()


class SalesPickingListReportShortageView(views.APIView):
    """
    报告缺货并通知理货员/库管（创建库存预警）
    POST /pickings/<pk>/report-shortage/  {item_id, remark}
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:picking:job'

    def post(self, request, pk):
        from apps.inventory.models import StockWarning, Warehouse, Material
        try:
            picking = SalesPickingList.objects.get(pk=pk)
        except SalesPickingList.DoesNotExist:
            return error_response(message='拣货单不存在', code=404)

        item_id = request.data.get('item_id')
        remark = request.data.get('remark', '')

        try:
            item = SalesPickingListItem.objects.get(pk=item_id, picking_list=picking)
        except SalesPickingListItem.DoesNotExist:
            return error_response(message='拣货明细不存在', code=404)

        if item.status == 'refunded':
            return error_response(message='该商品已退款，不可重复操作', code=400)

        warehouse = Warehouse.objects.filter(name=picking.warehouse).first()
        material = Material.objects.filter(code=item.material_code).first()

        StockWarning.objects.create(
            material=material,
            material_code=item.material_code or '',
            material_name=item.material_name,
            picking_item_id=item.id,
            warehouse=warehouse,
            current_qty=0,
            threshold=0,
            status='urgent',
            warning_type='picking_shortage',
            remark=f'拣货单 {picking.picking_no} 缺货：{item.material_name} ({item.material_code or ""})，库位 {item.location_code or ""}。{remark}',
        )

        # 同时标记该明细为缺货
        item.shortage_qty = item.quantity
        item.picked_qty = 0
        item.status = 'shortage'
        item.save()

        return success_response(message='缺货上报成功，已通知理货员/库管')


class SalesPickingListSubmitView(views.APIView):
    """
    提交发货：根据拣货结果生成出库单并扣减库存
    POST /pickings/<pk>/submit/
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:picking:job'

    def post(self, request, pk):
        from apps.inventory.models import Inventory, Warehouse
        try:
            picking = SalesPickingList.objects.prefetch_related('items', 'order__items').get(pk=pk)
        except SalesPickingList.DoesNotExist:
            return error_response(message='拣货单不存在', code=404)

        if picking.status not in ('complete', 'shortage', 'picking'):
            return error_response(message='该拣货单当前状态不可提交', code=400)

        order = picking.order
        if not order:
            return error_response(message='拣货单未关联订单', code=400)

        warehouse_name = picking.warehouse or '默认仓库'
        warehouse = Warehouse.objects.filter(name=warehouse_name).first()

        # 构建出库明细（只出 picked_qty > 0 的）
        outstock_items = []
        for item in picking.items.all():
            picked = item.picked_qty or Decimal('0')
            if picked > 0:
                outstock_items.append({
                    'material_name': item.material_name,
                    'spec': item.spec or '',
                    'quantity': picked,
                    'unit': item.unit or '件',
                    'remark': item.remark or '',
                })

        if not outstock_items:
            return error_response(message='没有可出库的商品', code=400)

        # 库存校验 + 扣减
        for item_data in outstock_items:
            material_name = item_data['material_name']
            spec = item_data['spec']
            out_qty = item_data['quantity']
            inv_query = Inventory.objects.filter(material_name=material_name, spec=spec)
            if warehouse:
                inv_query = inv_query.filter(warehouse=warehouse)
            inv = inv_query.first()
            if not inv:
                return error_response(message=f'物料 "{material_name}" 在仓库中无库存记录', code=400)
            if inv.qty < out_qty:
                return error_response(message=f'物料 "{material_name}" 库存不足，当前库存 {inv.qty}', code=400)

        # 创建出库单
        stock_no = generate_order_no('CK', model=SalesOutStock, field='stock_no')
        outstock = SalesOutStock.objects.create(
            stock_no=stock_no,
            order=order,
            stock_date=datetime.date.today(),
            warehouse=warehouse_name,
            operator=request.user,
            remark=f'由拣货单 {picking.picking_no} 提交生成',
        )

        for item_data in outstock_items:
            SalesOutStockItem.objects.create(stock=outstock, **item_data)
            # 扣减库存
            material_name = item_data['material_name']
            spec = item_data['spec']
            out_qty = item_data['quantity']
            inv_query = Inventory.objects.filter(material_name=material_name, spec=spec)
            if warehouse:
                inv_query = inv_query.filter(warehouse=warehouse)
            inv = inv_query.first()
            if inv:
                inv.qty -= out_qty
                inv.save()

            # 更新订单明细已出库数量
            order_item = SalesOrderItem.objects.filter(
                order=order,
                material_name=material_name,
                spec=spec
            ).first()
            if order_item:
                order_item.delivered_qty = (order_item.delivered_qty or Decimal('0')) + out_qty
                order_item.save()

        # 更新订单状态（复用 SalesOutStockSerializer 的拆单逻辑）
        serializer = SalesOutStockSerializer()
        serializer._update_order_status(order, order.customer)

        picking.status = 'done'
        picking.save()

        return success_response(
            data={'picking_id': picking.id, 'outstock_no': outstock.stock_no},
            message='发货提交成功'
        )


class SalesPickingListRefundItemView(views.APIView):
    """
    标记拣货明细已退款
    POST /pickings/<pk>/refund-item/  {item_id}
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'sales:picking:edit'

    def post(self, request, pk):
        try:
            picking = SalesPickingList.objects.get(pk=pk)
        except SalesPickingList.DoesNotExist:
            return error_response(message='拣货单不存在', code=404)

        if picking.status in ('done', 'cancelled'):
            return error_response(message='该拣货单当前不可操作', code=400)

        item_id = request.data.get('item_id')
        if not item_id:
            return error_response(message='缺少 item_id 参数', code=400)

        try:
            item = SalesPickingListItem.objects.get(pk=item_id, picking_list=picking)
        except (SalesPickingListItem.DoesNotExist, ValueError):
            return error_response(message='拣货明细不存在', code=404)

        if item.status == 'refunded':
            return error_response(message='该商品已标记退款', code=400)

        item.picked_qty = Decimal('0')
        item.shortage_qty = Decimal('0')
        item.refunded_qty = item.quantity or Decimal('0')
        item.status = 'refunded'
        item.save()

        # 更新拣货单状态
        SalesPickingListPickItemView()._update_picking_status(picking)
        return success_response(data=SalesPickingListSerializer(picking).data, message='标记退款成功')
