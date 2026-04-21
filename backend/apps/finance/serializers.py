from rest_framework import serializers
from apps.finance.models import (
    AccountSubject, Voucher, VoucherItem,
    Counterparty, ReceivablePayable, PaymentReceipt, Settlement
)


class AccountSubjectSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = AccountSubject
        fields = '__all__'

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        if children.exists():
            return AccountSubjectSerializer(children, many=True, context=self.context).data
        return []


class VoucherItemSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_category = serializers.CharField(source='subject.category', read_only=True)

    class Meta:
        model = VoucherItem
        fields = '__all__'


class VoucherSerializer(serializers.ModelSerializer):
    items = VoucherItemSerializer(many=True, required=False)
    preparer_name = serializers.CharField(source='preparer.username', read_only=True)
    auditor_name = serializers.CharField(source='auditor.username', read_only=True)

    class Meta:
        model = Voucher
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        voucher = Voucher.objects.create(**validated_data)
        total_debit = 0
        total_credit = 0
        for idx, item_data in enumerate(items_data, start=1):
            item_data['line_no'] = idx
            item = VoucherItem.objects.create(voucher=voucher, **item_data)
            total_debit += item.debit or 0
            total_credit += item.credit or 0
        voucher.total_debit = total_debit
        voucher.total_credit = total_credit
        voucher.save()
        return voucher

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            total_debit = 0
            total_credit = 0
            for idx, item_data in enumerate(items_data, start=1):
                item_data['line_no'] = idx
                item = VoucherItem.objects.create(voucher=instance, **item_data)
                total_debit += item.debit or 0
                total_credit += item.credit or 0
            instance.total_debit = total_debit
            instance.total_credit = total_credit
            instance.save()
        return instance


# ==================== 往来单位 ====================

class CounterpartySerializer(serializers.ModelSerializer):
    receivable_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    receivable_unpaid = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    payable_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    payable_unpaid = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    net_balance = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Counterparty
        fields = '__all__'

    def get_net_balance(self, obj):
        """净余额 = 应收未结 - 应付未结"""
        return float(obj.receivable_unpaid) - float(obj.payable_unpaid)


class CounterpartyOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Counterparty
        fields = ['id', 'name', 'type']


# ==================== 应收应付 / 收付款 / 核销 ====================

class SettlementSerializer(serializers.ModelSerializer):
    payment_receipt_no = serializers.CharField(source='payment_receipt.doc_no', read_only=True)
    receivable_payable_no = serializers.CharField(source='receivable_payable.doc_no', read_only=True)
    receivable_payable_type = serializers.CharField(source='receivable_payable.doc_type', read_only=True)

    class Meta:
        model = Settlement
        fields = '__all__'


class ReceivablePayableSerializer(serializers.ModelSerializer):
    remaining_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    overdue_days = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    settlements = SettlementSerializer(many=True, read_only=True)
    counterparty_name = serializers.CharField(source='counterparty_obj.name', read_only=True)

    class Meta:
        model = ReceivablePayable
        fields = '__all__'


class PaymentReceiptSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    settled_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    unsettled_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    settlements = SettlementSerializer(many=True, read_only=True)
    counterparty_name = serializers.CharField(source='counterparty_obj.name', read_only=True)

    class Meta:
        model = PaymentReceipt
        fields = '__all__'


# ==================== 对账往来专用序列化器 ====================

class CounterpartyBalanceSerializer(serializers.Serializer):
    """往来余额表序列化器"""
    counterparty = serializers.CharField()
    type = serializers.CharField()
    # 期初余额（截止到查询开始日期之前的累计）
    opening_receivable = serializers.DecimalField(max_digits=14, decimal_places=2)
    opening_payable = serializers.DecimalField(max_digits=14, decimal_places=2)
    # 本期发生额
    period_receivable = serializers.DecimalField(max_digits=14, decimal_places=2)
    period_receivable_paid = serializers.DecimalField(max_digits=14, decimal_places=2)
    period_payable = serializers.DecimalField(max_digits=14, decimal_places=2)
    period_payable_paid = serializers.DecimalField(max_digits=14, decimal_places=2)
    period_receipt = serializers.DecimalField(max_digits=14, decimal_places=2)
    period_payment = serializers.DecimalField(max_digits=14, decimal_places=2)
    # 期末余额
    closing_receivable = serializers.DecimalField(max_digits=14, decimal_places=2)
    closing_payable = serializers.DecimalField(max_digits=14, decimal_places=2)
