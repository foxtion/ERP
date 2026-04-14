from django.contrib import admin
from apps.finance.models import AccountSubject, Voucher, VoucherItem, ReceivablePayable, PaymentReceipt


class VoucherItemInline(admin.TabularInline):
    model = VoucherItem
    extra = 1


@admin.register(AccountSubject)
class AccountSubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['code', 'name']


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['voucher_no', 'voucher_date', 'total_debit', 'total_credit', 'preparer']
    inlines = [VoucherItemInline]
    search_fields = ['voucher_no']


@admin.register(ReceivablePayable)
class ReceivablePayableAdmin(admin.ModelAdmin):
    list_display = ['doc_no', 'doc_type', 'counterparty', 'amount', 'paid_amount', 'status', 'doc_date']
    list_filter = ['doc_type', 'status']
    search_fields = ['doc_no', 'counterparty']


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ['doc_no', 'doc_type', 'counterparty', 'amount', 'doc_date', 'operator']
    list_filter = ['doc_type']
    search_fields = ['doc_no', 'counterparty']
