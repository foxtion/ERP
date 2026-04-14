from django.urls import path
from apps.purchase import views

urlpatterns = [
    path('suppliers/', views.SupplierListCreateView.as_view(), name='supplier_list'),
    path('suppliers/<int:pk>/', views.SupplierRetrieveUpdateDestroyView.as_view(), name='supplier_detail'),

    path('requests/', views.PurchaseRequestListCreateView.as_view(), name='request_list'),
    path('requests/<int:pk>/', views.PurchaseRequestRetrieveUpdateDestroyView.as_view(), name='request_detail'),

    path('orders/', views.PurchaseOrderListCreateView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.PurchaseOrderRetrieveUpdateDestroyView.as_view(), name='order_detail'),
    path('orders/options/', views.PurchaseOrderOptionsView.as_view(), name='order_options'),

    path('instocks/', views.PurchaseInStockListCreateView.as_view(), name='instock_list'),
    path('instocks/<int:pk>/', views.PurchaseInStockRetrieveUpdateDestroyView.as_view(), name='instock_detail'),
]
