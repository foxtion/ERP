from django.urls import path
from apps.inventory import views

urlpatterns = [
    path('warehouses/', views.WarehouseListCreateView.as_view(), name='warehouse_list'),
    path('warehouses/<int:pk>/', views.WarehouseRetrieveUpdateDestroyView.as_view(), name='warehouse_detail'),
    path('warehouses/options/', views.WarehouseOptionsView.as_view(), name='warehouse_options'),

    path('stocks/', views.InventoryListView.as_view(), name='stock_list'),
    path('stocks/stats/', views.StockStatsView.as_view(), name='stock_stats'),

    path('warnings/', views.StockWarningListView.as_view(), name='warning_list'),
    path('warnings/<int:pk>/handle/', views.StockWarningHandleView.as_view(), name='warning_handle'),
    path('warnings/stats/', views.StockWarningStatsView.as_view(), name='warning_stats'),

    path('transfers/', views.StockTransferListCreateView.as_view(), name='transfer_list'),
    path('transfers/<int:pk>/', views.StockTransferRetrieveUpdateDestroyView.as_view(), name='transfer_detail'),
    path('transfers/<int:pk>/execute/', views.StockTransferExecuteView.as_view(), name='transfer_execute'),

    path('checks/', views.InventoryCheckListCreateView.as_view(), name='check_list'),
    path('checks/<int:pk>/', views.InventoryCheckRetrieveUpdateDestroyView.as_view(), name='check_detail'),
    path('checks/<int:pk>/complete/', views.InventoryCheckCompleteView.as_view(), name='check_complete'),

    path('locations/', views.WarehouseLocationListCreateView.as_view(), name='location_list'),
    path('locations/<int:pk>/', views.WarehouseLocationRetrieveUpdateDestroyView.as_view(), name='location_detail'),

    path('materials/', views.MaterialListCreateView.as_view(), name='material_list'),
    path('materials/<int:pk>/', views.MaterialRetrieveUpdateDestroyView.as_view(), name='material_detail'),
    path('materials/options/', views.MaterialOptionsView.as_view(), name='material_options'),
]
