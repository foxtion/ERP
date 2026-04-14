from django.urls import path
from apps.production import views

urlpatterns = [
    path('boms/', views.BOMListCreateView.as_view(), name='bom_list'),
    path('boms/<int:pk>/', views.BOMRetrieveUpdateDestroyView.as_view(), name='bom_detail'),
    path('boms/options/', views.BOMOptionsView.as_view(), name='bom_options'),

    path('plans/', views.ProductionPlanListCreateView.as_view(), name='plan_list'),
    path('plans/<int:pk>/', views.ProductionPlanRetrieveUpdateDestroyView.as_view(), name='plan_detail'),

    path('orders/', views.ProductionOrderListCreateView.as_view(), name='production_order_list'),
    path('orders/<int:pk>/', views.ProductionOrderRetrieveUpdateDestroyView.as_view(), name='production_order_detail'),
    path('orders/options/', views.ProductionOrderOptionsView.as_view(), name='production_order_options'),

    path('requisitions/', views.MaterialRequisitionListCreateView.as_view(), name='requisition_list'),
    path('requisitions/<int:pk>/', views.MaterialRequisitionRetrieveUpdateDestroyView.as_view(), name='requisition_detail'),

    path('instocks/', views.ProductionInStockListCreateView.as_view(), name='production_instock_list'),
    path('instocks/<int:pk>/', views.ProductionInStockRetrieveUpdateDestroyView.as_view(), name='production_instock_detail'),
]
