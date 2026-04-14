from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from apps.system.permissions import RBACPermission
from utils.response import success_response
from django.db.models import Sum

from apps.finance.models import AccountSubject, Voucher, ReceivablePayable, PaymentReceipt
from apps.finance.serializers import (
    AccountSubjectSerializer, VoucherSerializer,
    ReceivablePayableSerializer, PaymentReceiptSerializer
)


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
    """
    获取所有科目的平铺列表（用于凭证明细选择）
    """
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


class VoucherListCreateView(generics.ListCreateAPIView):
    queryset = Voucher.objects.all().order_by('-id')
    serializer_class = VoucherSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:voucher:view'
    search_fields = ['voucher_no']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'finance:voucher:add'
        return super().get_permissions()


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


class ReceivablePayableListCreateView(generics.ListCreateAPIView):
    queryset = ReceivablePayable.objects.all().order_by('-id')
    serializer_class = ReceivablePayableSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:receivable:view'
    search_fields = ['doc_no', 'counterparty']
    filterset_fields = ['doc_type', 'status']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'finance:receivable:add'
        return super().get_permissions()


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


class PaymentReceiptListCreateView(generics.ListCreateAPIView):
    queryset = PaymentReceipt.objects.all().order_by('-id')
    serializer_class = PaymentReceiptSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:payment:view'
    search_fields = ['doc_no', 'counterparty']
    filterset_fields = ['doc_type']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.required_permission = 'finance:payment:add'
        return super().get_permissions()


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


class FinanceSummaryView(views.APIView):
    """
    财务报表基础：应收应付、收付款汇总
    """
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = 'finance:receivable:view'

    def get(self, request):
        receivable_total = ReceivablePayable.objects.filter(doc_type='receivable').aggregate(total=Sum('amount'))['total'] or 0
        receivable_paid = ReceivablePayable.objects.filter(doc_type='receivable').aggregate(total=Sum('paid_amount'))['total'] or 0
        payable_total = ReceivablePayable.objects.filter(doc_type='payable').aggregate(total=Sum('amount'))['total'] or 0
        payable_paid = ReceivablePayable.objects.filter(doc_type='payable').aggregate(total=Sum('paid_amount'))['total'] or 0
        receipt_total = PaymentReceipt.objects.filter(doc_type='receipt').aggregate(total=Sum('amount'))['total'] or 0
        payment_total = PaymentReceipt.objects.filter(doc_type='payment').aggregate(total=Sum('amount'))['total'] or 0

        return success_response(data={
            'receivable_total': receivable_total,
            'receivable_unpaid': receivable_total - receivable_paid,
            'payable_total': payable_total,
            'payable_unpaid': payable_total - payable_paid,
            'receipt_total': receipt_total,
            'payment_total': payment_total,
        })
