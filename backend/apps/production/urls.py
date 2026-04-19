from django.urls import path
from apps.production import views

urlpatterns = [
    path('boms/', views.BOMListCreateView.as_view(), name='bom_list'),
    path('boms/<int:pk>/', views.BOMRetrieveUpdateDestroyView.as_view(), name='bom_detail'),
    path('boms/<int:pk>/copy/', views.BOMCopyView.as_view(), name='bom_copy'),
    path('boms/options/', views.BOMOptionsView.as_view(), name='bom_options'),

    path('plans/', views.ProductionPlanListCreateView.as_view(), name='plan_list'),
    path('plans/<int:pk>/', views.ProductionPlanRetrieveUpdateDestroyView.as_view(), name='plan_detail'),
    path('plans/<int:pk>/confirm/', views.ProductionPlanConfirmView.as_view(), name='plan_confirm'),
    path('plans/<int:pk>/complete/', views.ProductionPlanCompleteView.as_view(), name='plan_complete'),
    path('plans/<int:pk>/cancel/', views.ProductionPlanCancelView.as_view(), name='plan_cancel'),
    path('plans/<int:pk>/order/', views.ProductionPlanCreateOrderView.as_view(), name='plan_order'),
    path('plans/options/', views.ProductionPlanOptionsView.as_view(), name='plan_options'),

    path('orders/', views.ProductionOrderListCreateView.as_view(), name='production_order_list'),
    path('orders/<int:pk>/', views.ProductionOrderRetrieveUpdateDestroyView.as_view(), name='production_order_detail'),
    path('orders/<int:pk>/release/', views.ProductionOrderReleaseView.as_view(), name='order_release'),
    path('orders/<int:pk>/start/', views.ProductionOrderStartView.as_view(), name='order_start'),
    path('orders/<int:pk>/complete/', views.ProductionOrderCompleteView.as_view(), name='order_complete'),
    path('orders/<int:pk>/cancel/', views.ProductionOrderCancelView.as_view(), name='order_cancel'),
    path('orders/<int:pk>/requisition/', views.ProductionOrderCreateRequisitionView.as_view(), name='order_requisition'),
    path('orders/<int:pk>/instock/', views.ProductionOrderCreateInStockView.as_view(), name='order_instock'),
    path('orders/options/', views.ProductionOrderOptionsView.as_view(), name='production_order_options'),

    path('requisitions/', views.MaterialRequisitionListCreateView.as_view(), name='requisition_list'),
    path('requisitions/<int:pk>/', views.MaterialRequisitionRetrieveUpdateDestroyView.as_view(), name='requisition_detail'),
    path('requisitions/<int:pk>/submit/', views.MaterialRequisitionSubmitView.as_view(), name='requisition_submit'),
    path('requisitions/<int:pk>/approve/', views.MaterialRequisitionApproveView.as_view(), name='requisition_approve'),
    path('requisitions/<int:pk>/issue/', views.MaterialRequisitionIssueView.as_view(), name='requisition_issue'),
    path('requisitions/<int:pk>/cancel/', views.MaterialRequisitionCancelView.as_view(), name='requisition_cancel'),

    path('instocks/', views.ProductionInStockListCreateView.as_view(), name='production_instock_list'),
    path('instocks/<int:pk>/', views.ProductionInStockRetrieveUpdateDestroyView.as_view(), name='production_instock_detail'),
    path('instocks/<int:pk>/submit/', views.ProductionInStockSubmitView.as_view(), name='instock_submit'),
    path('instocks/<int:pk>/approve/', views.ProductionInStockApproveView.as_view(), name='instock_approve'),
    path('instocks/<int:pk>/confirm/', views.ProductionInStockConfirmView.as_view(), name='instock_confirm'),
    path('instocks/<int:pk>/cancel/', views.ProductionInStockCancelView.as_view(), name='instock_cancel'),
]
