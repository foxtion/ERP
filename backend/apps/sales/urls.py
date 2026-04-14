from django.urls import path
from apps.sales import views

urlpatterns = [
    path('customers/', views.CustomerListCreateView.as_view(), name='customer_list'),
    path('customers/<int:pk>/', views.CustomerRetrieveUpdateDestroyView.as_view(), name='customer_detail'),
    path('customers/options/', views.CustomerOptionsView.as_view(), name='customer_options'),

    path('orders/', views.SalesOrderListCreateView.as_view(), name='sales_order_list'),
    path('orders/<int:pk>/', views.SalesOrderRetrieveUpdateDestroyView.as_view(), name='sales_order_detail'),
    path('orders/options/', views.SalesOrderOptionsView.as_view(), name='sales_order_options'),

    path('outstocks/', views.SalesOutStockListCreateView.as_view(), name='outstock_list'),
    path('outstocks/<int:pk>/', views.SalesOutStockRetrieveUpdateDestroyView.as_view(), name='outstock_detail'),

    path('returns/', views.SalesReturnListCreateView.as_view(), name='return_list'),
    path('returns/<int:pk>/', views.SalesReturnRetrieveUpdateDestroyView.as_view(), name='return_detail'),
]
