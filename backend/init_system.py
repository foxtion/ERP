#!/usr/bin/env python
"""
系统完整初始化：菜单(含按钮权限)、部门、角色、角色权限分配、用户角色绑定
执行: python init_system.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.system.models import Menu, Role, Department

User = get_user_model()

print("='*50")
print("开始系统初始化...")
print("='*50")

# ========== 1. 清空旧数据（保留用户） ==========
Menu.objects.all().delete()
Role.objects.all().delete()
Department.objects.all().delete()
print("[1/5] 已清空旧菜单、角色、部门数据")

# ========== 2. 创建部门 ==========
depts = {
    '总经办': Department.objects.create(name='总经办', code='DEPT001', sort_order=1),
    '技术部': Department.objects.create(name='技术部', code='DEPT002', sort_order=2),
    '财务部': Department.objects.create(name='财务部', code='DEPT003', sort_order=3),
    '人力资源部': Department.objects.create(name='人力资源部', code='DEPT004', sort_order=4),
    '销售部': Department.objects.create(name='销售部', code='DEPT005', sort_order=5),
    '采购部': Department.objects.create(name='采购部', code='DEPT006', sort_order=6),
    '生产部': Department.objects.create(name='生产部', code='DEPT007', sort_order=7),
    '仓储部': Department.objects.create(name='仓储部', code='DEPT008', sort_order=8),
}
print("[2/5] 已创建 8 个部门")

# ========== 3. 创建菜单（DIR + MENU + BUTTON） ==========
def create_dir(name, title, icon, sort_order):
    return Menu.objects.create(name=name, title=title, menu_type='DIR', path=f'/{name}', icon=icon, sort_order=sort_order)

def create_menu(name, title, path, component, icon, parent, sort_order, perm_prefix):
    menu = Menu.objects.create(
        name=name, title=title, menu_type='MENU', path=path,
        component=component, icon=icon, parent=parent,
        sort_order=sort_order, permission=f'{perm_prefix}:view'
    )
    # 为每个菜单创建按钮权限
    buttons = [
        (f'{name}_add', '新增', f'{perm_prefix}:add'),
        (f'{name}_edit', '编辑', f'{perm_prefix}:edit'),
        (f'{name}_delete', '删除', f'{perm_prefix}:delete'),
    ]
    for b_name, b_title, b_perm in buttons:
        Menu.objects.create(
            name=b_name, title=b_title, menu_type='BUTTON',
            parent=menu, permission=b_perm
        )
    return menu

# 系统管理
sys_dir = create_dir('system', '系统管理', 'Setting', 100)
create_menu('user', '用户管理', '/system/user', 'views/system/UserList.vue', 'UserFilled', sys_dir, 1, 'system:user')
create_menu('role', '角色管理', '/system/role', 'views/system/RoleList.vue', 'User', sys_dir, 2, 'system:role')
create_menu('menu', '菜单管理', '/system/menu', 'views/system/MenuList.vue', 'Menu', sys_dir, 3, 'system:menu')
create_menu('dept', '部门管理', '/system/dept', 'views/system/DeptList.vue', 'OfficeBuilding', sys_dir, 4, 'system:dept')

# 人力资源
hr_dir = create_dir('hr', '人力资源', 'UserFilled', 200)
create_menu('employee', '员工管理', '/hr/employee', 'views/hr/EmployeeList.vue', 'Avatar', hr_dir, 1, 'hr:employee')
create_menu('attendance', '考勤管理', '/hr/attendance', 'views/hr/AttendanceList.vue', 'Calendar', hr_dir, 2, 'hr:attendance')
create_menu('salary', '薪资管理', '/hr/salary', 'views/hr/SalaryList.vue', 'Money', hr_dir, 3, 'hr:salary')

# 财务管理
fin_dir = create_dir('finance', '财务管理', 'Coin', 300)
create_menu('subject', '科目管理', '/finance/subject', 'views/finance/SubjectList.vue', 'Notebook', fin_dir, 1, 'finance:subject')
create_menu('voucher', '凭证管理', '/finance/voucher', 'views/finance/VoucherList.vue', 'Document', fin_dir, 2, 'finance:voucher')
create_menu('receivable', '应收管理', '/finance/receivable', 'views/finance/ReceivableList.vue', 'Download', fin_dir, 3, 'finance:receivable')
create_menu('payment', '应付管理', '/finance/payment', 'views/finance/PaymentList.vue', 'Upload', fin_dir, 4, 'finance:payment')
create_menu('statement', '对账单', '/finance/statement', 'views/finance/StatementList.vue', 'DocumentChecked', fin_dir, 5, 'finance:statement')
create_menu('counterparty', '往来单位', '/finance/counterparty', 'views/finance/CounterpartyList.vue', 'OfficeBuilding', fin_dir, 6, 'finance:counterparty')

# 库存管理
inv_dir = create_dir('inventory', '库存管理', 'Box', 400)
create_menu('warehouse', '仓库管理', '/inventory/warehouse', 'views/inventory/WarehouseList.vue', 'House', inv_dir, 1, 'inventory:warehouse')
create_menu('location', '库位管理', '/inventory/location', 'views/inventory/LocationList.vue', 'MapLocation', inv_dir, 2, 'inventory:location')
create_menu('material', '物料管理', '/inventory/material', 'views/inventory/MaterialList.vue', 'Goods', inv_dir, 3, 'inventory:material')
create_menu('stock', '库存查询', '/inventory/stock', 'views/inventory/StockList.vue', 'Search', inv_dir, 4, 'inventory:stock')
create_menu('check', '盘点管理', '/inventory/check', 'views/inventory/CheckList.vue', 'Edit', inv_dir, 5, 'inventory:check')
create_menu('transfer', '调拨管理', '/inventory/transfer', 'views/inventory/TransferList.vue', 'Switch', inv_dir, 6, 'inventory:transfer')
create_menu('warning', '库存预警', '/inventory/warning', 'views/inventory/WarningList.vue', 'Warning', inv_dir, 7, 'inventory:warning')

# 生产管理
prod_dir = create_dir('production', '生产管理', 'Tools', 500)
create_menu('bom', 'BOM管理', '/production/bom', 'views/production/BomList.vue', 'List', prod_dir, 1, 'production:bom')
create_menu('plan', '生产计划', '/production/plan', 'views/production/PlanList.vue', 'Calendar', prod_dir, 2, 'production:plan')
create_menu('workorder', '工单管理', '/production/workorder', 'views/production/WorkOrderList.vue', 'Tickets', prod_dir, 3, 'production:workorder')
create_menu('requisition', '领料管理', '/production/requisition', 'views/production/RequisitionList.vue', 'TakeawayBox', prod_dir, 4, 'production:requisition')
create_menu('production_instock', '生产入库', '/production/instock', 'views/production/ProductionInStockList.vue', 'FolderAdd', prod_dir, 5, 'production:instock')

# 采购管理
pur_dir = create_dir('purchase', '采购管理', 'ShoppingCart', 600)
create_menu('supplier', '供应商管理', '/purchase/supplier', 'views/purchase/SupplierList.vue', 'Shop', pur_dir, 1, 'purchase:supplier')
create_menu('purchase_request', '采购申请', '/purchase/request', 'views/purchase/RequestList.vue', 'EditPen', pur_dir, 2, 'purchase:request')
create_menu('purchase_order', '采购订单', '/purchase/order', 'views/purchase/OrderList.vue', 'Document', pur_dir, 3, 'purchase:order')
create_menu('purchase_instock', '采购入库', '/purchase/instock', 'views/purchase/InStockList.vue', 'FolderAdd', pur_dir, 4, 'purchase:instock')

# 销售管理
sales_dir = create_dir('sales', '销售管理', 'Sell', 700)
create_menu('customer', '客户管理', '/sales/customer', 'views/sales/CustomerList.vue', 'User', sales_dir, 1, 'sales:customer')
create_menu('sales_order', '销售订单', '/sales/order', 'views/sales/OrderList.vue', 'Document', sales_dir, 2, 'sales:order')
create_menu('picking', '拣货管理', '/sales/picking', 'views/sales/PickingList.vue', 'Box', sales_dir, 3, 'sales:picking')
create_menu('outstock', '出库管理', '/sales/outstock', 'views/sales/OutStockList.vue', 'Upload', sales_dir, 4, 'sales:outstock')
create_menu('return', '退货管理', '/sales/return', 'views/sales/ReturnList.vue', 'RefreshLeft', sales_dir, 5, 'sales:return')

menu_count = Menu.objects.count()
print(f"[3/5] 已创建 {menu_count} 个菜单（含按钮权限）")

# ========== 4. 创建角色并分配所有权限 ==========
admin_role = Role.objects.create(name='系统管理员', code='admin', sort_order=1)
admin_role.menus.set(Menu.objects.all())
print("[4/5] 已创建'系统管理员'角色，关联所有菜单权限")

# ========== 5. 给用户分配角色和部门 ==========
admin = User.objects.filter(username='admin').first()
if admin:
    admin.roles.set([admin_role])
    admin.dept = depts['总经办']
    admin.save()
    print(f"[5/5] 用户 '{admin.username}' 已绑定'系统管理员'角色和'总经办'部门")
else:
    print("[5/5] 警告: 未找到 admin 用户")

print("=" * 50)
print("系统初始化完成！")
print(f"  - 部门: {Department.objects.count()} 个")
print(f"  - 菜单: {Menu.objects.count()} 个")
print(f"  - 角色: {Role.objects.count()} 个")
print("=" * 50)
