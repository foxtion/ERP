from django.urls import path
from apps.finance import views

urlpatterns = [
    path('subjects/', views.AccountSubjectListCreateView.as_view(), name='subject_list'),
    path('subjects/flat/', views.AccountSubjectAllFlatView.as_view(), name='subject_flat'),
    path('subjects/<int:pk>/', views.AccountSubjectRetrieveUpdateDestroyView.as_view(), name='subject_detail'),

    path('vouchers/', views.VoucherListCreateView.as_view(), name='voucher_list'),
    path('vouchers/<int:pk>/', views.VoucherRetrieveUpdateDestroyView.as_view(), name='voucher_detail'),

    path('receivables/', views.ReceivablePayableListCreateView.as_view(), name='receivable_list'),
    path('receivables/<int:pk>/', views.ReceivablePayableRetrieveUpdateDestroyView.as_view(), name='receivable_detail'),

    path('payments/', views.PaymentReceiptListCreateView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', views.PaymentReceiptRetrieveUpdateDestroyView.as_view(), name='payment_detail'),

    path('summary/', views.FinanceSummaryView.as_view(), name='finance_summary'),
]
