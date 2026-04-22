from django.urls import path
from apps.purchase import views

urlpatterns = [
    path('suppliers/', views.SupplierListCreateView.as_view(), name='supplier_list'),
    path('suppliers/export/', views.SupplierExportView.as_view(), name='supplier_export'),
    path('suppliers/import/', views.SupplierImportView.as_view(), name='supplier_import'),
    path('suppliers/<int:pk>/', views.SupplierRetrieveUpdateDestroyView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/toggle_status/', views.SupplierToggleStatusView.as_view(), name='supplier_toggle_status'),

    path('requests/', views.PurchaseRequestListCreateView.as_view(), name='request_list'),
    path('requests/<int:pk>/', views.PurchaseRequestRetrieveUpdateDestroyView.as_view(), name='request_detail'),
    path('requests/<int:pk>/submit/', views.PurchaseRequestSubmitView.as_view(), name='request_submit'),
    path('requests/<int:pk>/approve/', views.PurchaseRequestApproveView.as_view(), name='request_approve'),
    path('requests/<int:pk>/reject/', views.PurchaseRequestRejectView.as_view(), name='request_reject'),

    path('orders/', views.PurchaseOrderListCreateView.as_view(), name='order_list'),
    path('orders/export/', views.PurchaseOrderExportView.as_view(), name='order_export'),
    path('orders/<int:pk>/', views.PurchaseOrderRetrieveUpdateDestroyView.as_view(), name='order_detail'),
    path('orders/<int:pk>/confirm/', views.PurchaseOrderConfirmView.as_view(), name='order_confirm'),
    path('orders/<int:pk>/cancel/', views.PurchaseOrderCancelView.as_view(), name='order_cancel'),
    path('orders/<int:pk>/complete/', views.PurchaseOrderCompleteView.as_view(), name='order_complete'),
    path('orders/options/', views.PurchaseOrderOptionsView.as_view(), name='order_options'),

    path('requests/<int:pk>/convert_to_order/', views.PurchaseRequestConvertView.as_view(), name='request_convert'),

    path('instocks/', views.PurchaseInStockListCreateView.as_view(), name='instock_list'),
    path('instocks/<int:pk>/', views.PurchaseInStockRetrieveUpdateDestroyView.as_view(), name='instock_detail'),
]
