from django.urls import path
from apps.finance import views

urlpatterns = [
    path('subjects/', views.AccountSubjectListCreateView.as_view(), name='subject_list'),
    path('subjects/flat/', views.AccountSubjectAllFlatView.as_view(), name='subject_flat'),
    path('subjects/<int:pk>/', views.AccountSubjectRetrieveUpdateDestroyView.as_view(), name='subject_detail'),

    path('vouchers/', views.VoucherListCreateView.as_view(), name='voucher_list'),
    path('vouchers/<int:pk>/', views.VoucherRetrieveUpdateDestroyView.as_view(), name='voucher_detail'),
    path('vouchers/<int:pk>/audit/', views.VoucherAuditView.as_view(), name='voucher_audit'),
    path('vouchers/<int:pk>/cancel_audit/', views.VoucherCancelAuditView.as_view(), name='voucher_cancel_audit'),
    path('vouchers/generate_no/', views.VoucherGenerateNoView.as_view(), name='voucher_generate_no'),

    path('receivables/', views.ReceivablePayableListCreateView.as_view(), name='receivable_list'),
    path('receivables/<int:pk>/', views.ReceivablePayableRetrieveUpdateDestroyView.as_view(), name='receivable_detail'),
    path('receivables/overdue/', views.OverdueReceivableView.as_view(), name='receivable_overdue'),

    path('payments/', views.PaymentReceiptListCreateView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', views.PaymentReceiptRetrieveUpdateDestroyView.as_view(), name='payment_detail'),
    path('payments/<int:pk>/settle/', views.PaymentSettleView.as_view(), name='payment_settle'),

    path('settlements/', views.SettlementListCreateView.as_view(), name='settlement_list'),
    path('settlements/<int:pk>/', views.SettlementRetrieveUpdateDestroyView.as_view(), name='settlement_detail'),
    path('settlements/<int:pk>/cancel/', views.CancelSettleView.as_view(), name='settlement_cancel'),

    path('statement/', views.StatementView.as_view(), name='finance_statement'),

    path('summary/', views.FinanceSummaryView.as_view(), name='finance_summary'),
]
