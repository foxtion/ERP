import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import { usePermissionStore } from '@/store/permission'

const DevPlaceholder = () => import('@/views/DevPlaceholder.vue')

const constantRoutes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { hidden: true },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/components/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'home-o', keepAlive: true },
      },
      // 已实现的表单页/详情页（隐藏菜单，不走动态路由）
      {
        path: '/hr/attendance/form',
        name: 'AttendanceForm',
        component: () => import('@/views/hr/AttendanceForm.vue'),
        meta: { title: '考勤录入', hidden: true },
      },
      {
        path: '/hr/employee/form',
        name: 'EmployeeForm',
        component: () => import('@/views/hr/EmployeeForm.vue'),
        meta: { title: '员工表单', hidden: true },
      },
      {
        path: '/hr/salary/form',
        name: 'SalaryForm',
        component: DevPlaceholder,
        meta: { title: '薪资表单', hidden: true },
      },
      {
        path: '/sales/order-form',
        name: 'SalesOrderForm',
        component: () => import('@/views/sales/OrderForm.vue'),
        meta: { title: '销售订单表单', hidden: true },
      },
      {
        path: '/sales/order-detail/:id',
        name: 'SalesOrderDetail',
        component: () => import('@/views/sales/OrderDetail.vue'),
        meta: { title: '销售订单详情', hidden: true },
      },
      {
        path: '/sales/customer-form',
        name: 'CustomerForm',
        component: () => import('@/views/sales/CustomerForm.vue'),
        meta: { title: '客户表单', hidden: true },
      },
      {
        path: '/sales/outstock',
        name: 'OutStockList',
        component: () => import('@/views/sales/OutStockList.vue'),
        meta: { title: '出库管理', hidden: true },
      },
      {
        path: '/sales/outstock-job',
        name: 'OutStockJob',
        component: () => import('@/views/sales/OutStockList.vue'),
        meta: { title: '出库作业', hidden: true },
      },
      {
        path: '/sales/outstock-form',
        name: 'OutStockForm',
        component: () => import('@/views/sales/OutStockForm.vue'),
        meta: { title: '出库表单', hidden: true },
      },
      {
        path: '/sales/outstock-detail/:id',
        name: 'OutStockDetail',
        component: () => import('@/views/sales/OutStockDetail.vue'),
        meta: { title: '出库详情', hidden: true },
      },
      {
        path: '/sales/picking-detail/:id',
        name: 'PickingDetail',
        component: DevPlaceholder,
        meta: { title: '拣货详情', hidden: true },
      },
      {
        path: '/sales/picking-job/:id',
        name: 'PickingJob',
        component: () => import('@/views/sales/PickingJob.vue'),
        meta: { title: '拣货作业', hidden: true },
      },
      {
        path: '/sales/return-form',
        name: 'ReturnForm',
        component: DevPlaceholder,
        meta: { title: '退货表单', hidden: true },
      },
      {
        path: '/sales/return-detail/:id',
        name: 'ReturnDetail',
        component: DevPlaceholder,
        meta: { title: '退货详情', hidden: true },
      },
      {
        path: '/purchase/order-form',
        name: 'PurchaseOrderForm',
        component: () => import('@/views/purchase/OrderForm.vue'),
        meta: { title: '采购订单表单', hidden: true },
      },
      {
        path: '/purchase/instock/add',
        name: 'PurchaseInStockAdd',
        component: DevPlaceholder,
        meta: { title: '采购入库新增', hidden: true },
      },
      {
        path: '/purchase/instock/edit/:id',
        name: 'PurchaseInStockEdit',
        component: DevPlaceholder,
        meta: { title: '采购入库编辑', hidden: true },
      },
      {
        path: '/purchase/request/add',
        name: 'PurchaseRequestAdd',
        component: DevPlaceholder,
        meta: { title: '采购申请新增', hidden: true },
      },
      {
        path: '/purchase/request/edit/:id',
        name: 'PurchaseRequestEdit',
        component: DevPlaceholder,
        meta: { title: '采购申请编辑', hidden: true },
      },
      {
        path: '/purchase/supplier/add',
        name: 'SupplierAdd',
        component: () => import('@/views/purchase/SupplierForm.vue'),
        meta: { title: '供应商新增', hidden: true },
      },
      {
        path: '/purchase/supplier/edit/:id',
        name: 'SupplierEdit',
        component: () => import('@/views/purchase/SupplierForm.vue'),
        meta: { title: '供应商编辑', hidden: true },
      },
      {
        path: '/inventory/check/add',
        name: 'InventoryCheckAdd',
        component: DevPlaceholder,
        meta: { title: '库存盘点新增', hidden: true },
      },
      {
        path: '/inventory/check/edit/:id',
        name: 'InventoryCheckEdit',
        component: DevPlaceholder,
        meta: { title: '库存盘点编辑', hidden: true },
      },
      {
        path: '/inventory/location/add',
        name: 'LocationAdd',
        component: () => import('@/views/inventory/LocationForm.vue'),
        meta: { title: '库位新增', hidden: true },
      },
      {
        path: '/inventory/location/edit/:id',
        name: 'LocationEdit',
        component: () => import('@/views/inventory/LocationForm.vue'),
        meta: { title: '库位编辑', hidden: true },
      },
      {
        path: '/inventory/material/add',
        name: 'MaterialAdd',
        component: () => import('@/views/inventory/MaterialForm.vue'),
        meta: { title: '物料新增', hidden: true },
      },
      {
        path: '/inventory/material/edit/:id',
        name: 'MaterialEdit',
        component: () => import('@/views/inventory/MaterialForm.vue'),
        meta: { title: '物料编辑', hidden: true },
      },
      {
        path: '/inventory/transfer/add',
        name: 'TransferAdd',
        component: DevPlaceholder,
        meta: { title: '库存调拨新增', hidden: true },
      },
      {
        path: '/inventory/transfer/edit/:id',
        name: 'TransferEdit',
        component: DevPlaceholder,
        meta: { title: '库存调拨编辑', hidden: true },
      },
      {
        path: '/inventory/warehouse/add',
        name: 'WarehouseAdd',
        component: () => import('@/views/inventory/WarehouseForm.vue'),
        meta: { title: '仓库新增', hidden: true },
      },
      {
        path: '/inventory/warehouse/edit/:id',
        name: 'WarehouseEdit',
        component: () => import('@/views/inventory/WarehouseForm.vue'),
        meta: { title: '仓库编辑', hidden: true },
      },
      {
        path: '/production/bom/add',
        name: 'BomAdd',
        component: () => import('@/views/production/BomForm.vue'),
        meta: { title: 'BOM新增', hidden: true },
      },
      {
        path: '/production/bom/detail/:id',
        name: 'BomDetail',
        component: () => import('@/views/production/BomDetail.vue'),
        meta: { title: 'BOM详情', hidden: true },
      },
      {
        path: '/production/bom/edit/:id',
        name: 'BomEdit',
        component: () => import('@/views/production/BomForm.vue'),
        meta: { title: 'BOM编辑', hidden: true },
      },
      {
        path: '/production/plan/add',
        name: 'PlanAdd',
        component: () => import('@/views/production/PlanForm.vue'),
        meta: { title: '生产计划新增', hidden: true },
      },
      {
        path: '/production/plan/detail/:id',
        name: 'PlanDetail',
        component: () => import('@/views/production/PlanDetail.vue'),
        meta: { title: '生产计划详情', hidden: true },
      },
      {
        path: '/production/plan/edit/:id',
        name: 'PlanEdit',
        component: () => import('@/views/production/PlanForm.vue'),
        meta: { title: '生产计划编辑', hidden: true },
      },
      {
        path: '/production/instock/add',
        name: 'ProductionInStockAdd',
        component: () => import('@/views/production/ProductionInStockForm.vue'),
        meta: { title: '生产入库新增', hidden: true },
      },
      {
        path: '/production/instock/detail/:id',
        name: 'ProductionInStockDetail',
        component: () => import('@/views/production/ProductionInStockDetail.vue'),
        meta: { title: '生产入库详情', hidden: true },
      },
      {
        path: '/production/instock/edit/:id',
        name: 'ProductionInStockEdit',
        component: () => import('@/views/production/ProductionInStockForm.vue'),
        meta: { title: '生产入库编辑', hidden: true },
      },
      {
        path: '/production/requisition/add',
        name: 'RequisitionAdd',
        component: () => import('@/views/production/RequisitionForm.vue'),
        meta: { title: '领料单新增', hidden: true },
      },
      {
        path: '/production/requisition/detail/:id',
        name: 'RequisitionDetail',
        component: () => import('@/views/production/RequisitionDetail.vue'),
        meta: { title: '领料单详情', hidden: true },
      },
      {
        path: '/production/requisition/edit/:id',
        name: 'RequisitionEdit',
        component: () => import('@/views/production/RequisitionForm.vue'),
        meta: { title: '领料单编辑', hidden: true },
      },
      {
        path: '/production/workorder/add',
        name: 'WorkOrderAdd',
        component: () => import('@/views/production/WorkOrderForm.vue'),
        meta: { title: '工单新增', hidden: true },
      },
      {
        path: '/production/workorder/detail/:id',
        name: 'WorkOrderDetail',
        component: () => import('@/views/production/WorkOrderDetail.vue'),
        meta: { title: '工单详情', hidden: true },
      },
      {
        path: '/production/workorder/edit/:id',
        name: 'WorkOrderEdit',
        component: () => import('@/views/production/WorkOrderForm.vue'),
        meta: { title: '工单编辑', hidden: true },
      },
      {
        path: '/finance/payment/add',
        name: 'PaymentAdd',
        component: () => import('@/views/finance/PaymentForm.vue'),
        meta: { title: '收付款新增', hidden: true },
      },
      {
        path: '/finance/payment/detail/:id',
        name: 'PaymentDetail',
        component: () => import('@/views/finance/PaymentDetail.vue'),
        meta: { title: '收付款详情', hidden: true },
      },
      {
        path: '/finance/payment/edit/:id',
        name: 'PaymentEdit',
        component: () => import('@/views/finance/PaymentForm.vue'),
        meta: { title: '收付款编辑', hidden: true },
      },
      {
        path: '/finance/receivable/add',
        name: 'ReceivableAdd',
        component: () => import('@/views/finance/ReceivableForm.vue'),
        meta: { title: '应收应付新增', hidden: true },
      },
      {
        path: '/finance/receivable/detail/:id',
        name: 'ReceivableDetail',
        component: () => import('@/views/finance/ReceivableDetail.vue'),
        meta: { title: '应收应付详情', hidden: true },
      },
      {
        path: '/finance/receivable/edit/:id',
        name: 'ReceivableEdit',
        component: () => import('@/views/finance/ReceivableForm.vue'),
        meta: { title: '应收应付编辑', hidden: true },
      },
      {
        path: '/finance/subject/add',
        name: 'SubjectAdd',
        component: DevPlaceholder,
        meta: { title: '科目新增', hidden: true },
      },
      {
        path: '/finance/subject/detail/:id',
        name: 'SubjectDetail',
        component: DevPlaceholder,
        meta: { title: '科目详情', hidden: true },
      },
      {
        path: '/finance/subject/edit/:id',
        name: 'SubjectEdit',
        component: DevPlaceholder,
        meta: { title: '科目编辑', hidden: true },
      },
      {
        path: '/finance/voucher/add',
        name: 'VoucherAdd',
        component: () => import('@/views/finance/VoucherForm.vue'),
        meta: { title: '凭证新增', hidden: true },
      },
      {
        path: '/finance/voucher/detail/:id',
        name: 'VoucherDetail',
        component: () => import('@/views/finance/VoucherDetail.vue'),
        meta: { title: '凭证详情', hidden: true },
      },
      {
        path: '/finance/voucher/edit/:id',
        name: 'VoucherEdit',
        component: () => import('@/views/finance/VoucherForm.vue'),
        meta: { title: '凭证编辑', hidden: true },
      },
      {
        path: '/system/dept/form',
        name: 'DeptForm',
        component: () => import('@/views/system/DeptForm.vue'),
        meta: { title: '部门表单', hidden: true },
      },
      {
        path: '/system/menu/form',
        name: 'MenuForm',
        component: () => import('@/views/system/MenuForm.vue'),
        meta: { title: '菜单表单', hidden: true },
      },
      {
        path: '/system/role/form',
        name: 'RoleForm',
        component: () => import('@/views/system/RoleForm.vue'),
        meta: { title: '角色表单', hidden: true },
      },
      {
        path: '/system/user/form',
        name: 'UserForm',
        component: () => import('@/views/system/UserForm.vue'),
        meta: { title: '用户表单', hidden: true },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { hidden: true },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
  routes: constantRoutes,
  scrollBehavior() {
    return { top: 0 }
  },
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()

  if (to.path === '/login') {
    if (userStore.isLoggedIn) {
      next('/dashboard')
    } else {
      next()
    }
    return
  }

  if (!userStore.isLoggedIn) {
    next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
    return
  }

  // 动态路由未生成时，根据菜单生成
  if (permissionStore.dynamicRoutes.length === 0 && userStore.menus.length > 0) {
    const routes = permissionStore.generateRoutes(userStore.menus)
    console.log('[Router Guard] generated routes count:', routes.length, 'menus count:', userStore.menus.length)
    routes.forEach((route) => {
      if (!router.hasRoute(route.name)) {
        router.addRoute('Layout', route)
        console.log('[Router Guard] addRoute:', route.name, '->', route.path)
      }
    })
    // 避免 generateRoutes 返回空数组导致无限重定向
    if (routes.length > 0) {
      next({ ...to, replace: true })
      return
    }
  }

  next()
})

export default router
