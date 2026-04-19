from rest_framework import serializers
from apps.finance.models import AccountSubject, Voucher, VoucherItem, ReceivablePayable, PaymentReceipt, Settlement


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

    class Meta:
        model = ReceivablePayable
        fields = '__all__'


class PaymentReceiptSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    settled_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    unsettled_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    settlements = SettlementSerializer(many=True, read_only=True)

    class Meta:
        model = PaymentReceipt
        fields = '__all__'
