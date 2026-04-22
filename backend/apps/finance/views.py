from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from apps.system.permissions import RBACPermission
from utils.response import success_response, error_response
from django.db.models import Sum, Q, F
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from datetime import date

from apps.finance.models import (
    AccountSubject, Voucher, Counterparty,
    ReceivablePayable, PaymentReceipt, Settlement
)
from apps.finance.serializers import (
    AccountSubjectSerializer, VoucherSerializer,
    CounterpartySerializer, CounterpartyOptionSerializer,
    ReceivablePayableSerializer, PaymentReceiptSerializer, SettlementSerializer
)


# ==================== 会计科目 ====================

class AccountSubjectListCreateView(generics.ListCreateAPIView):
    queryset = AccountSubject.objects.filter(is_active=True)
    serializer_class = AccountSubjectSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:subject:view'
    search_fields = ['code', 'name']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'finance:subject:add'
        return super().get_permissions()

    def get_queryset(self):
        return AccountSubject.objects.filter(is_active=True, parent__isnull=True).order_by('code')


class AccountSubjectAllFlatView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:subject:view'

    def get(self, request):
        queryset = AccountSubject.objects.filter(is_active=True).order_by('code')
        data = AccountSubjectSerializer(queryset, many=True).data
        return success_response(data=data)


class AccountSubjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccountSubject.objects.all()
    serializer_class = AccountSubjectSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'finance:subject:edit'
        elif method == 'DELETE':
            self.required_permission = 'finance:subject:delete'
        else:
            self.required_permission = 'finance:subject:view'
        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


# ==================== 记账凭证 ====================

class VoucherListCreateView(generics.ListCreateAPIView):
    queryset = Voucher.objects.all().order_by('-id')
    serializer_class = VoucherSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:voucher:view'
    search_fields = ['voucher_no']
    filterset_fields = ['status']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'finance:voucher:add'
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(voucher_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(voucher_date__lte=date_to)
        return queryset


class VoucherRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'finance:voucher:edit'
        elif method == 'DELETE':
            self.required_permission = 'finance:voucher:delete'
        else:
            self.required_permission = 'finance:voucher:view'
        return super().get_permissions()


class VoucherAuditView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:voucher:edit'

    def post(self, request, pk):
        try:
            voucher = Voucher.objects.get(pk=pk)
        except Voucher.DoesNotExist:
            return error_response(message='凭证不存在', code=404)

        if voucher.status == 'audited':
            return error_response(message='凭证已审核，无需重复审核', code=400)
        if voucher.status == 'cancelled':
            return error_response(message='已作废的凭证不能审核', code=400)

        if voucher.total_debit != voucher.total_credit:
            return error_response(message='借贷不平衡，不能审核', code=400)
        if voucher.total_debit == 0:
            return error_response(message='金额为0的凭证不能审核', code=400)

        voucher.status = 'audited'
        voucher.auditor = request.user
        voucher.audit_date = timezone.now()
        voucher.save()

        return success_response(
            data=VoucherSerializer(voucher).data,
            message='审核成功'
        )


class VoucherCancelAuditView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:voucher:edit'

    def post(self, request, pk):
        try:
            voucher = Voucher.objects.get(pk=pk)
        except Voucher.DoesNotExist:
            return error_response(message='凭证不存在', code=404)

        if voucher.status != 'audited':
            return error_response(message='只有已审核的凭证才能取消审核', code=400)

        voucher.status = 'draft'
        voucher.auditor = None
        voucher.audit_date = None
        voucher.save()

        return success_response(
            data=VoucherSerializer(voucher).data,
            message='取消审核成功'
        )


class VoucherGenerateNoView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:voucher:add'

    def get(self, request):
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        prefix = f'PZ{date_str}'
        existing = Voucher.objects.filter(voucher_no__startswith=prefix).order_by('-id').first()
        if existing:
            try:
                seq = int(existing.voucher_no.split('-')[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        return success_response(data={'voucher_no': f'{prefix}-{seq:03d}'})


# ==================== 往来单位 ====================

class CounterpartyListCreateView(generics.ListCreateAPIView):
    queryset = Counterparty.objects.filter(is_active=True).order_by('-id')
    serializer_class = CounterpartySerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:receivable:view'
    search_fields = ['name', 'contact', 'phone']
    filterset_fields = ['type']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'finance:receivable:edit'
        return super().get_permissions()


class CounterpartyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Counterparty.objects.all()
    serializer_class = CounterpartySerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'finance:receivable:edit'
        elif method == 'DELETE':
            self.required_permission = 'finance:receivable:delete'
        else:
            self.required_permission = 'finance:receivable:view'
        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class CounterpartyOptionView(views.APIView):
    """获取往来单位下拉选项"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:receivable:view'

    def get(self, request):
        queryset = Counterparty.objects.filter(is_active=True).order_by('name')
        data = CounterpartyOptionSerializer(queryset, many=True).data
        return success_response(data=data)


class CounterpartyStatsView(views.APIView):
    """往来单位统计：Top 欠款/应付款单位"""
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:receivable:view'

    def get(self, request):
        from decimal import Decimal
        receivable_stats = []
        rp_qs = ReceivablePayable.objects.filter(
            doc_type='receivable'
        ).exclude(status='paid').values('counterparty').annotate(
            total=Sum('amount'),
            paid=Sum('paid_amount')
        ).order_by('-total')[:10]
        for d in rp_qs:
            receivable_stats.append({
                'counterparty': d['counterparty'],
                'total': str(d['total'] or Decimal('0')),
                'unpaid': str((d['total'] or Decimal('0')) - (d['paid'] or Decimal('0'))),
            })

        payable_stats = []
        py_qs = ReceivablePayable.objects.filter(
            doc_type='payable'
        ).exclude(status='paid').values('counterparty').annotate(
            total=Sum('amount'),
            paid=Sum('paid_amount')
        ).order_by('-total')[:10]
        for d in py_qs:
            payable_stats.append({
                'counterparty': d['counterparty'],
                'total': str(d['total'] or Decimal('0')),
                'unpaid': str((d['total'] or Decimal('0')) - (d['paid'] or Decimal('0'))),
            })

        return success_response(data={
            'receivable_top': receivable_stats,
            'payable_top': payable_stats,
        })


# ==================== 应收应付 ====================

class ReceivablePayableListCreateView(generics.ListCreateAPIView):
    queryset = ReceivablePayable.objects.all().order_by('-id')
    serializer_class = ReceivablePayableSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:receivable:view'
    search_fields = ['doc_no', 'counterparty', 'source_no']
    filterset_fields = ['doc_type', 'status', 'source_type', 'counterparty']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'finance:receivable:add'
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        due_date_from = self.request.query_params.get('due_date_from')
        due_date_to = self.request.query_params.get('due_date_to')
        if date_from:
            queryset = queryset.filter(doc_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(doc_date__lte=date_to)
        if due_date_from:
            queryset = queryset.filter(due_date__gte=due_date_from)
        if due_date_to:
            queryset = queryset.filter(due_date__lte=due_date_to)
        status_in = self.request.query_params.get('status__in')
        if status_in:
            queryset = queryset.filter(status__in=status_in.split(','))
        overdue = self.request.query_params.get('overdue')
        if overdue == '1':
            queryset = queryset.filter(due_date__lt=date.today()).exclude(status='paid')
        return queryset


class ReceivablePayableRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReceivablePayable.objects.all()
    serializer_class = ReceivablePayableSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'finance:receivable:edit'
        elif method == 'DELETE':
            self.required_permission = 'finance:receivable:delete'
        else:
            self.required_permission = 'finance:receivable:view'
        return super().get_permissions()


# ==================== 收付款 ====================

class PaymentReceiptListCreateView(generics.ListCreateAPIView):
    queryset = PaymentReceipt.objects.all().order_by('-id')
    serializer_class = PaymentReceiptSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:payment:view'
    search_fields = ['doc_no', 'counterparty']
    filterset_fields = ['doc_type', 'payment_method', 'counterparty']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'finance:payment:add'
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(doc_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(doc_date__lte=date_to)
        return queryset


class PaymentReceiptRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PaymentReceipt.objects.all()
    serializer_class = PaymentReceiptSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_permissions(self):
        method = self.request.method
        if method in ('PUT', 'PATCH'):
            self.required_permission = 'finance:payment:edit'
        elif method == 'DELETE':
            self.required_permission = 'finance:payment:delete'
        else:
            self.required_permission = 'finance:payment:view'
        return super().get_permissions()


# ==================== 核销明细 ====================

class SettlementListCreateView(generics.ListCreateAPIView):
    queryset = Settlement.objects.all().order_by('-id')
    serializer_class = SettlementSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:payment:view'
    filterset_fields = ['payment_receipt', 'receivable_payable']


class SettlementRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:payment:edit'

    def destroy(self, request, *args, **kwargs):
        return error_response(message='核销记录不允许直接删除，请使用取消核销接口', code=400)


# ==================== 核销操作 ====================

class PaymentSettleView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:payment:edit'

    @transaction.atomic
    def post(self, request, pk):
        receivable_id = request.data.get('receivable_id')
        amount = request.data.get('amount')

        if not receivable_id or amount is None:
            return error_response(message='缺少必要参数：receivable_id, amount', code=400)

        from decimal import Decimal
        try:
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            return error_response(message='核销金额格式错误', code=400)

        if amount <= 0:
            return error_response(message='核销金额必须大于0', code=400)

        try:
            payment = PaymentReceipt.objects.get(pk=pk)
        except PaymentReceipt.DoesNotExist:
            return error_response(message='收付款单不存在', code=404)

        try:
            receivable = ReceivablePayable.objects.get(pk=receivable_id)
        except ReceivablePayable.DoesNotExist:
            return error_response(message='应收应付单不存在', code=404)

        type_map = {'receipt': 'receivable', 'payment': 'payable'}
        if type_map.get(payment.doc_type) != receivable.doc_type:
            return error_response(
                message=f'类型不匹配：{payment.get_doc_type_display()}不能核销{receivable.get_doc_type_display()}',
                code=400
            )

        unsettled = Decimal(str(payment.unsettled_amount))
        remaining = Decimal(str(receivable.remaining_amount))
        if amount > unsettled:
            return error_response(
                message=f'核销金额超出收付款单未核销金额（剩余{unsettled}）',
                code=400
            )
        if amount > remaining:
            return error_response(
                message=f'核销金额超出应收应付单剩余金额（剩余{remaining}）',
                code=400
            )

        settlement = Settlement.objects.create(
            payment_receipt=payment,
            receivable_payable=receivable,
            amount=amount
        )

        receivable.paid_amount += amount
        if receivable.paid_amount >= receivable.amount:
            receivable.status = 'paid'
        elif receivable.paid_amount > 0:
            receivable.status = 'partial'
        else:
            receivable.status = 'unpaid'
        receivable.save()

        return success_response(
            data=SettlementSerializer(settlement).data,
            message='核销成功'
        )


class CancelSettleView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:payment:edit'

    @transaction.atomic
    def post(self, request, pk):
        try:
            settlement = Settlement.objects.get(pk=pk)
        except Settlement.DoesNotExist:
            return error_response(message='核销记录不存在', code=404)

        receivable = settlement.receivable_payable
        amount = settlement.amount

        settlement.delete()

        receivable.paid_amount -= amount
        if receivable.paid_amount <= 0:
            receivable.paid_amount = 0
            receivable.status = 'unpaid'
        else:
            receivable.status = 'partial'
        receivable.save()

        return success_response(message='取消核销成功')


# ==================== 逾期查询 ====================

class OverdueReceivableView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:receivable:view'

    def get(self, request):
        doc_type = request.query_params.get('doc_type')
        queryset = ReceivablePayable.objects.filter(
            due_date__lt=date.today()
        ).exclude(status='paid')
        if doc_type:
            queryset = queryset.filter(doc_type=doc_type)
        queryset = queryset.order_by('due_date')
        serializer = ReceivablePayableSerializer(queryset, many=True)
        return success_response(data=serializer.data)


# ==================== 对账单 ====================

class StatementView(views.APIView):
    """
    往来对账单：按往来单位汇总展示应收应付和收付款明细
    GET /statement/?counterparty=xxx&date_from=2024-01-01&date_to=2024-12-31
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:receivable:view'

    def get(self, request):
        counterparty = request.query_params.get('counterparty')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if not counterparty:
            return error_response(message='请指定往来单位', code=400)

        # 应收应付明细
        rp_qs = ReceivablePayable.objects.filter(counterparty=counterparty)
        if date_from:
            rp_qs = rp_qs.filter(doc_date__gte=date_from)
        if date_to:
            rp_qs = rp_qs.filter(doc_date__lte=date_to)
        rp_qs = rp_qs.order_by('doc_date')

        # 收付款明细
        pm_qs = PaymentReceipt.objects.filter(counterparty=counterparty)
        if date_from:
            pm_qs = pm_qs.filter(doc_date__gte=date_from)
        if date_to:
            pm_qs = pm_qs.filter(doc_date__lte=date_to)
        pm_qs = pm_qs.order_by('doc_date')

        # 合并排序
        items = []
        for rp in rp_qs:
            items.append({
                'date': rp.doc_date,
                'doc_no': rp.doc_no,
                'type': 'receivable_payable',
                'doc_type': rp.doc_type,
                'doc_type_text': rp.get_doc_type_display(),
                'amount': str(rp.amount),
                'paid_amount': str(rp.paid_amount),
                'remaining': str(rp.remaining_amount),
                'status': rp.status,
                'status_text': rp.get_status_display(),
                'remark': rp.remark or '',
            })
        for pm in pm_qs:
            items.append({
                'date': pm.doc_date,
                'doc_no': pm.doc_no,
                'type': 'payment_receipt',
                'doc_type': pm.doc_type,
                'doc_type_text': pm.get_doc_type_display(),
                'amount': str(pm.amount),
                'paid_amount': str(pm.settled_amount),
                'remaining': str(pm.unsettled_amount),
                'status': '',
                'status_text': '',
                'remark': pm.remark or '',
            })
        items.sort(key=lambda x: x['date'])

        # 汇总
        receivable_total = rp_qs.filter(doc_type='receivable').aggregate(t=Sum('amount'))['t'] or 0
        receivable_paid = rp_qs.filter(doc_type='receivable').aggregate(t=Sum('paid_amount'))['t'] or 0
        payable_total = rp_qs.filter(doc_type='payable').aggregate(t=Sum('amount'))['t'] or 0
        payable_paid = rp_qs.filter(doc_type='payable').aggregate(t=Sum('paid_amount'))['t'] or 0
        receipt_total = pm_qs.filter(doc_type='receipt').aggregate(t=Sum('amount'))['t'] or 0
        payment_total = pm_qs.filter(doc_type='payment').aggregate(t=Sum('amount'))['t'] or 0

        return success_response(data={
            'counterparty': counterparty,
            'items': items,
            'summary': {
                'receivable_total': str(receivable_total),
                'receivable_paid': str(receivable_paid),
                'receivable_unpaid': str(receivable_total - receivable_paid),
                'payable_total': str(payable_total),
                'payable_paid': str(payable_paid),
                'payable_unpaid': str(payable_total - payable_paid),
                'receipt_total': str(receipt_total),
                'payment_total': str(payment_total),
            }
        })


# ==================== 往来余额表 ====================

class CounterpartyBalanceView(views.APIView):
    """
    往来余额表：按往来单位展示期初余额、本期发生额、期末余额
    GET /balance/?date_from=2024-01-01&date_to=2024-12-31
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:receivable:view'

    def get(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if not date_from or not date_to:
            return error_response(message='请指定日期范围', code=400)

        from decimal import Decimal

        # 获取所有有业务往来的单位
        all_parties = set()
        for rp in ReceivablePayable.objects.values('counterparty', 'doc_type').distinct():
            all_parties.add((rp['counterparty'], rp['doc_type']))
        for pm in PaymentReceipt.objects.values('counterparty', 'doc_type').distinct():
            all_parties.add((pm['counterparty'], pm['doc_type']))

        # 按单位名称聚合
        counterparty_names = set(p[0] for p in all_parties)

        results = []
        for name in sorted(counterparty_names):
            # 期初余额（date_from 之前的累计）
            opening_rp = ReceivablePayable.objects.filter(
                counterparty=name,
                doc_date__lt=date_from
            )
            opening_receivable = opening_rp.filter(doc_type='receivable').aggregate(
                t=Sum(F('amount') - F('paid_amount'))
            )['t'] or Decimal('0')
            opening_payable = opening_rp.filter(doc_type='payable').aggregate(
                t=Sum(F('amount') - F('paid_amount'))
            )['t'] or Decimal('0')

            # 本期应收应付发生额
            period_rp = ReceivablePayable.objects.filter(
                counterparty=name,
                doc_date__gte=date_from,
                doc_date__lte=date_to
            )
            period_receivable = period_rp.filter(doc_type='receivable').aggregate(t=Sum('amount'))['t'] or Decimal('0')
            period_receivable_paid = period_rp.filter(doc_type='receivable').aggregate(t=Sum('paid_amount'))['t'] or Decimal('0')
            period_payable = period_rp.filter(doc_type='payable').aggregate(t=Sum('amount'))['t'] or Decimal('0')
            period_payable_paid = period_rp.filter(doc_type='payable').aggregate(t=Sum('paid_amount'))['t'] or Decimal('0')

            # 本期收付款发生额
            period_pm = PaymentReceipt.objects.filter(
                counterparty=name,
                doc_date__gte=date_from,
                doc_date__lte=date_to
            )
            period_receipt = period_pm.filter(doc_type='receipt').aggregate(t=Sum('amount'))['t'] or Decimal('0')
            period_payment = period_pm.filter(doc_type='payment').aggregate(t=Sum('amount'))['t'] or Decimal('0')

            # 期末余额 = 期初 + 本期应收 - 本期收款（简化计算：直接用应收应付剩余金额）
            closing_rp = ReceivablePayable.objects.filter(counterparty=name, doc_date__lte=date_to)
            closing_receivable = closing_rp.filter(doc_type='receivable').aggregate(
                t=Sum(F('amount') - F('paid_amount'))
            )['t'] or Decimal('0')
            closing_payable = closing_rp.filter(doc_type='payable').aggregate(
                t=Sum(F('amount') - F('paid_amount'))
            )['t'] or Decimal('0')

            # 只显示有数据的单位
            has_data = (
                opening_receivable or opening_payable or
                period_receivable or period_payable or
                period_receipt or period_payment
            )
            if has_data:
                results.append({
                    'counterparty': name,
                    'opening_receivable': str(opening_receivable),
                    'opening_payable': str(opening_payable),
                    'period_receivable': str(period_receivable),
                    'period_receivable_paid': str(period_receivable_paid),
                    'period_payable': str(period_payable),
                    'period_payable_paid': str(period_payable_paid),
                    'period_receipt': str(period_receipt),
                    'period_payment': str(period_payment),
                    'closing_receivable': str(closing_receivable),
                    'closing_payable': str(closing_payable),
                    'net_balance': str(closing_receivable - closing_payable),
                })

        return success_response(data=results)


# ==================== 财务汇总 ====================

class FinanceSummaryView(views.APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:receivable:view'

    def get(self, request):
        receivable_total = ReceivablePayable.objects.filter(doc_type='receivable').aggregate(total=Sum('amount'))['total'] or 0
        receivable_paid = ReceivablePayable.objects.filter(doc_type='receivable').aggregate(total=Sum('paid_amount'))['total'] or 0
        payable_total = ReceivablePayable.objects.filter(doc_type='payable').aggregate(total=Sum('amount'))['total'] or 0
        payable_paid = ReceivablePayable.objects.filter(doc_type='payable').aggregate(total=Sum('paid_amount'))['total'] or 0
        receipt_total = PaymentReceipt.objects.filter(doc_type='receipt').aggregate(total=Sum('amount'))['total'] or 0
        payment_total = PaymentReceipt.objects.filter(doc_type='payment').aggregate(total=Sum('amount'))['total'] or 0

        # 逾期统计
        overdue_receivable = ReceivablePayable.objects.filter(
            doc_type='receivable', due_date__lt=date.today()
        ).exclude(status='paid').aggregate(total=Sum('amount'))['total'] or 0
        overdue_receivable_unpaid = ReceivablePayable.objects.filter(
            doc_type='receivable', due_date__lt=date.today()
        ).exclude(status='paid').aggregate(total=Sum(F('amount') - F('paid_amount')))['total'] or 0

        # 按往来单位 Top 10 欠款
        top_debtors = []
        debtor_qs = ReceivablePayable.objects.filter(
            doc_type='receivable'
        ).exclude(status='paid').values('counterparty').annotate(
            total=Sum('amount'),
            paid=Sum('paid_amount')
        ).order_by('-total')[:10]
        for d in debtor_qs:
            top_debtors.append({
                'counterparty': d['counterparty'],
                'total': str(d['total'] or 0),
                'unpaid': str((d['total'] or 0) - (d['paid'] or 0)),
            })

        return success_response(data={
            'receivable_total': str(receivable_total),
            'receivable_unpaid': str(receivable_total - receivable_paid),
            'payable_total': str(payable_total),
            'payable_unpaid': str(payable_total - payable_paid),
            'receipt_total': str(receipt_total),
            'payment_total': str(payment_total),
            'overdue_receivable': str(overdue_receivable),
            'overdue_receivable_unpaid': str(overdue_receivable_unpaid or 0),
            'top_debtors': top_debtors,
        })
