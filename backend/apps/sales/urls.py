from django.urls import path
from apps.sales import views

urlpatterns = [
    path('customers/', views.CustomerListCreateView.as_view(), name='customer_list'),
    path('customers/<int:pk>/', views.CustomerRetrieveUpdateDestroyView.as_view(), name='customer_detail'),
    path('customers/<int:pk>/stats/', views.CustomerStatsView.as_view(), name='customer_stats'),
    path('customers/<int:pk>/detail-stats/', views.CustomerDetailStatsView.as_view(), name='customer_detail_stats'),
    path('customers/export/', views.CustomerExportView.as_view(), name='customer_export'),
    path('customers/options/', views.CustomerOptionsView.as_view(), name='customer_options'),

    path('orders/', views.SalesOrderListCreateView.as_view(), name='sales_order_list'),
    path('orders/<int:pk>/', views.SalesOrderRetrieveUpdateDestroyView.as_view(), name='sales_order_detail'),
    path('orders/options/', views.SalesOrderOptionsView.as_view(), name='sales_order_options'),
    path('orders/pending-outstock/', views.PendingOutStockOrderView.as_view(), name='pending_outstock_orders'),
    path('orders/<int:pk>/outstock-items/', views.OrderOutStockItemsView.as_view(), name='order_outstock_items'),

    path('outstocks/', views.SalesOutStockListCreateView.as_view(), name='outstock_list'),
    path('outstocks/<int:pk>/', views.SalesOutStockRetrieveUpdateDestroyView.as_view(), name='outstock_detail'),

    path('returns/', views.SalesReturnListCreateView.as_view(), name='return_list'),
    path('returns/<int:pk>/', views.SalesReturnRetrieveUpdateDestroyView.as_view(), name='return_detail'),
]
