#!/usr/bin/env python
"""
初始化系统菜单数据
在服务器上执行: python init_menus.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
django.setup()

from apps.system.models import Menu

Menu.objects.all().delete()

# ========== 系统管理 ==========
sys_dir = Menu.objects.create(
    name='system', title='系统管理', menu_type='DIR',
    path='/system', icon='Setting', sort_order=100
)
Menu.objects.create(
    name='user', title='用户管理', menu_type='MENU',
    path='/system/user', component='views/system/UserList.vue',
    icon='UserFilled', parent=sys_dir, sort_order=1,
    permission='system:user:view'
)
Menu.objects.create(
    name='role', title='角色管理', menu_type='MENU',
    path='/system/role', component='views/system/RoleList.vue',
    icon='User', parent=sys_dir, sort_order=2,
    permission='system:role:view'
)
Menu.objects.create(
    name='menu', title='菜单管理', menu_type='MENU',
    path='/system/menu', component='views/system/MenuList.vue',
    icon='Menu', parent=sys_dir, sort_order=3,
    permission='system:menu:view'
)
Menu.objects.create(
    name='dept', title='部门管理', menu_type='MENU',
    path='/system/dept', component='views/system/DeptList.vue',
    icon='OfficeBuilding', parent=sys_dir, sort_order=4,
    permission='system:dept:view'
)

# ========== 人力资源 ==========
hr_dir = Menu.objects.create(
    name='hr', title='人力资源', menu_type='DIR',
    path='/hr', icon='UserFilled', sort_order=200
)
Menu.objects.create(
    name='employee', title='员工管理', menu_type='MENU',
    path='/hr/employee', component='views/hr/EmployeeList.vue',
    icon='Avatar', parent=hr_dir, sort_order=1,
    permission='hr:employee:view'
)
Menu.objects.create(
    name='attendance', title='考勤管理', menu_type='MENU',
    path='/hr/attendance', component='views/hr/AttendanceList.vue',
    icon='Calendar', parent=hr_dir, sort_order=2,
    permission='hr:attendance:view'
)
Menu.objects.create(
    name='salary', title='薪资管理', menu_type='MENU',
    path='/hr/salary', component='views/hr/SalaryList.vue',
    icon='Money', parent=hr_dir, sort_order=3,
    permission='hr:salary:view'
)

# ========== 财务管理 ==========
fin_dir = Menu.objects.create(
    name='finance', title='财务管理', menu_type='DIR',
    path='/finance', icon='Coin', sort_order=300
)
Menu.objects.create(
    name='subject', title='科目管理', menu_type='MENU',
    path='/finance/subject', component='views/finance/SubjectList.vue',
    icon='Notebook', parent=fin_dir, sort_order=1,
    permission='finance:subject:view'
)
Menu.objects.create(
    name='voucher', title='凭证管理', menu_type='MENU',
    path='/finance/voucher', component='views/finance/VoucherList.vue',
    icon='Document', parent=fin_dir, sort_order=2,
    permission='finance:voucher:view'
)
Menu.objects.create(
    name='receivable', title='应收管理', menu_type='MENU',
    path='/finance/receivable', component='views/finance/ReceivableList.vue',
    icon='Download', parent=fin_dir, sort_order=3,
    permission='finance:receivable:view'
)
Menu.objects.create(
    name='payment', title='应付管理', menu_type='MENU',
    path='/finance/payment', component='views/finance/PaymentList.vue',
    icon='Upload', parent=fin_dir, sort_order=4,
    permission='finance:payment:view'
)
Menu.objects.create(
    name='statement', title='对账单', menu_type='MENU',
    path='/finance/statement', component='views/finance/StatementList.vue',
    icon='DocumentChecked', parent=fin_dir, sort_order=5,
    permission='finance:statement:view'
)
Menu.objects.create(
    name='counterparty', title='往来单位', menu_type='MENU',
    path='/finance/counterparty', component='views/finance/CounterpartyList.vue',
    icon='OfficeBuilding', parent=fin_dir, sort_order=6,
    permission='finance:counterparty:view'
)

# ========== 库存管理 ==========
inv_dir = Menu.objects.create(
    name='inventory', title='库存管理', menu_type='DIR',
    path='/inventory', icon='Box', sort_order=400
)
Menu.objects.create(
    name='warehouse', title='仓库管理', menu_type='MENU',
    path='/inventory/warehouse', component='views/inventory/WarehouseList.vue',
    icon='House', parent=inv_dir, sort_order=1,
    permission='inventory:warehouse:view'
)
Menu.objects.create(
    name='location', title='库位管理', menu_type='MENU',
    path='/inventory/location', component='views/inventory/LocationList.vue',
    icon='MapLocation', parent=inv_dir, sort_order=2,
    permission='inventory:location:view'
)
Menu.objects.create(
    name='material', title='物料管理', menu_type='MENU',
    path='/inventory/material', component='views/inventory/MaterialList.vue',
    icon='Goods', parent=inv_dir, sort_order=3,
    permission='inventory:material:view'
)
Menu.objects.create(
    name='stock', title='库存查询', menu_type='MENU',
    path='/inventory/stock', component='views/inventory/StockList.vue',
    icon='Search', parent=inv_dir, sort_order=4,
    permission='inventory:stock:view'
)
Menu.objects.create(
    name='check', title='盘点管理', menu_type='MENU',
    path='/inventory/check', component='views/inventory/CheckList.vue',
    icon='Edit', parent=inv_dir, sort_order=5,
    permission='inventory:check:view'
)
Menu.objects.create(
    name='transfer', title='调拨管理', menu_type='MENU',
    path='/inventory/transfer', component='views/inventory/TransferList.vue',
    icon='Switch', parent=inv_dir, sort_order=6,
    permission='inventory:transfer:view'
)
Menu.objects.create(
    name='warning', title='库存预警', menu_type='MENU',
    path='/inventory/warning', component='views/inventory/WarningList.vue',
    icon='Warning', parent=inv_dir, sort_order=7,
    permission='inventory:warning:view'
)

# ========== 生产管理 ==========
prod_dir = Menu.objects.create(
    name='production', title='生产管理', menu_type='DIR',
    path='/production', icon='Tools', sort_order=500
)
Menu.objects.create(
    name='bom', title='BOM管理', menu_type='MENU',
    path='/production/bom', component='views/production/BomList.vue',
    icon='List', parent=prod_dir, sort_order=1,
    permission='production:bom:view'
)
Menu.objects.create(
    name='plan', title='生产计划', menu_type='MENU',
    path='/production/plan', component='views/production/PlanList.vue',
    icon='Calendar', parent=prod_dir, sort_order=2,
    permission='production:plan:view'
)
Menu.objects.create(
    name='workorder', title='工单管理', menu_type='MENU',
    path='/production/workorder', component='views/production/WorkOrderList.vue',
    icon='Tickets', parent=prod_dir, sort_order=3,
    permission='production:workorder:view'
)
Menu.objects.create(
    name='requisition', title='领料管理', menu_type='MENU',
    path='/production/requisition', component='views/production/RequisitionList.vue',
    icon='TakeawayBox', parent=prod_dir, sort_order=4,
    permission='production:requisition:view'
)
Menu.objects.create(
    name='production_instock', title='生产入库', menu_type='MENU',
    path='/production/instock', component='views/production/ProductionInStockList.vue',
    icon='FolderAdd', parent=prod_dir, sort_order=5,
    permission='production:instock:view'
)

# ========== 采购管理 ==========
pur_dir = Menu.objects.create(
    name='purchase', title='采购管理', menu_type='DIR',
    path='/purchase', icon='ShoppingCart', sort_order=600
)
Menu.objects.create(
    name='supplier', title='供应商管理', menu_type='MENU',
    path='/purchase/supplier', component='views/purchase/SupplierList.vue',
    icon='Shop', parent=pur_dir, sort_order=1,
    permission='purchase:supplier:view'
)
Menu.objects.create(
    name='purchase_request', title='采购申请', menu_type='MENU',
    path='/purchase/request', component='views/purchase/RequestList.vue',
    icon='EditPen', parent=pur_dir, sort_order=2,
    permission='purchase:request:view'
)
Menu.objects.create(
    name='purchase_order', title='采购订单', menu_type='MENU',
    path='/purchase/order', component='views/purchase/OrderList.vue',
    icon='Document', parent=pur_dir, sort_order=3,
    permission='purchase:order:view'
)
Menu.objects.create(
    name='purchase_instock', title='采购入库', menu_type='MENU',
    path='/purchase/instock', component='views/purchase/InStockList.vue',
    icon='FolderAdd', parent=pur_dir, sort_order=4,
    permission='purchase:instock:view'
)

# ========== 销售管理 ==========
sales_dir = Menu.objects.create(
    name='sales', title='销售管理', menu_type='DIR',
    path='/sales', icon='Sell', sort_order=700
)
Menu.objects.create(
    name='customer', title='客户管理', menu_type='MENU',
    path='/sales/customer', component='views/sales/CustomerList.vue',
    icon='User', parent=sales_dir, sort_order=1,
    permission='sales:customer:view'
)
Menu.objects.create(
    name='sales_order', title='销售订单', menu_type='MENU',
    path='/sales/order', component='views/sales/OrderList.vue',
    icon='Document', parent=sales_dir, sort_order=2,
    permission='sales:order:view'
)
Menu.objects.create(
    name='picking', title='拣货管理', menu_type='MENU',
    path='/sales/picking', component='views/sales/PickingList.vue',
    icon='Box', parent=sales_dir, sort_order=3,
    permission='sales:picking:view'
)
Menu.objects.create(
    name='outstock', title='出库管理', menu_type='MENU',
    path='/sales/outstock', component='views/sales/OutStockList.vue',
    icon='Upload', parent=sales_dir, sort_order=4,
    permission='sales:outstock:view'
)
Menu.objects.create(
    name='return', title='退货管理', menu_type='MENU',
    path='/sales/return', component='views/sales/ReturnList.vue',
    icon='RefreshLeft', parent=sales_dir, sort_order=5,
    permission='sales:return:view'
)

print(f'初始化完成，共创建 {Menu.objects.count()} 个菜单')
