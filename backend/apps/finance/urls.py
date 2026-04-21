from django.urls import path
from apps.finance import views

urlpatterns = [
    # 会计科目
    path('subjects/', views.AccountSubjectListCreateView.as_view(), name='subject_list'),
    path('subjects/flat/', views.AccountSubjectAllFlatView.as_view(), name='subject_flat'),
    path('subjects/<int:pk>/', views.AccountSubjectRetrieveUpdateDestroyView.as_view(), name='subject_detail'),

    # 记账凭证
    path('vouchers/', views.VoucherListCreateView.as_view(), name='voucher_list'),
    path('vouchers/<int:pk>/', views.VoucherRetrieveUpdateDestroyView.as_view(), name='voucher_detail'),
    path('vouchers/<int:pk>/audit/', views.VoucherAuditView.as_view(), name='voucher_audit'),
    path('vouchers/<int:pk>/cancel_audit/', views.VoucherCancelAuditView.as_view(), name='voucher_cancel_audit'),
    path('vouchers/generate_no/', views.VoucherGenerateNoView.as_view(), name='voucher_generate_no'),

    # 往来单位
    path('counterparties/', views.CounterpartyListCreateView.as_view(), name='counterparty_list'),
    path('counterparties/<int:pk>/', views.CounterpartyRetrieveUpdateDestroyView.as_view(), name='counterparty_detail'),
    path('counterparties/options/', views.CounterpartyOptionView.as_view(), name='counterparty_options'),
    path('counterparties/stats/', views.CounterpartyStatsView.as_view(), name='counterparty_stats'),

    # 应收应付
    path('receivables/', views.ReceivablePayableListCreateView.as_view(), name='receivable_list'),
    path('receivables/<int:pk>/', views.ReceivablePayableRetrieveUpdateDestroyView.as_view(), name='receivable_detail'),
    path('receivables/overdue/', views.OverdueReceivableView.as_view(), name='receivable_overdue'),

    # 收付款
    path('payments/', views.PaymentReceiptListCreateView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', views.PaymentReceiptRetrieveUpdateDestroyView.as_view(), name='payment_detail'),
    path('payments/<int:pk>/settle/', views.PaymentSettleView.as_view(), name='payment_settle'),

    # 核销
    path('settlements/', views.SettlementListCreateView.as_view(), name='settlement_list'),
    path('settlements/<int:pk>/', views.SettlementRetrieveUpdateDestroyView.as_view(), name='settlement_detail'),
    path('settlements/<int:pk>/cancel/', views.CancelSettleView.as_view(), name='settlement_cancel'),

    # 对账单
    path('statement/', views.StatementView.as_view(), name='finance_statement'),

    # 往来余额表
    path('balance/', views.CounterpartyBalanceView.as_view(), name='finance_balance'),

    # 财务汇总
    path('summary/', views.FinanceSummaryView.as_view(), name='finance_summary'),
]
