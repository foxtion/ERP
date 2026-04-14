from django.urls import path
from apps.inventory import views

urlpatterns = [
    path('warehouses/', views.WarehouseListCreateView.as_view(), name='warehouse_list'),
    path('warehouses/<int:pk>/', views.WarehouseRetrieveUpdateDestroyView.as_view(), name='warehouse_detail'),
    path('warehouses/options/', views.WarehouseOptionsView.as_view(), name='warehouse_options'),

    path('stocks/', views.InventoryListView.as_view(), name='stock_list'),

    path('transfers/', views.StockTransferListCreateView.as_view(), name='transfer_list'),
    path('transfers/<int:pk>/', views.StockTransferRetrieveUpdateDestroyView.as_view(), name='transfer_detail'),

    path('checks/', views.InventoryCheckListCreateView.as_view(), name='check_list'),
    path('checks/<int:pk>/', views.InventoryCheckRetrieveUpdateDestroyView.as_view(), name='check_detail'),
]
