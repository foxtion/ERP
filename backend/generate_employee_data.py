"""
初始化人事管理-员工档案测试数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from apps.hr.models import Employee

User = get_user_model()


def run():
    print("开始生成员工档案测试数据...")

    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("未找到管理员用户，跳过数据生成")
        return

    employees_data = [
        {
            'employee_no': 'EMP202601-001', 'name': '张三', 'gender': 'male',
            'phone': '13800138001', 'email': 'zhangsan@company.com',
            'id_card': '110101199001011234', 'birth_date': date(1990, 1, 1),
            'department': '技术部', 'position': '高级工程师',
            'education': 'bachelor', 'graduate_school': '清华大学',
            'entry_date': date(2023, 3, 1), 'contract_end_date': date(2026, 3, 1),
            'bank_name': '中国工商银行', 'bank_account': '6222021234567890001',
            'emergency_contact': '张父', 'emergency_phone': '13900139001',
            'status': 'active', 'address': '北京市海淀区',
            'remark': '技术骨干'
        },
        {
            'employee_no': 'EMP202601-002', 'name': '李四', 'gender': 'female',
            'phone': '13800138002', 'email': 'lisi@company.com',
            'id_card': '310101199502022345', 'birth_date': date(1995, 2, 2),
            'department': '财务部', 'position': '财务经理',
            'education': 'master', 'graduate_school': '北京大学',
            'entry_date': date(2022, 6, 15), 'contract_end_date': date(2025, 6, 15),
            'bank_name': '中国建设银行', 'bank_account': '6222021234567890002',
            'emergency_contact': '李母', 'emergency_phone': '13900139002',
            'status': 'active', 'address': '上海市浦东新区',
            'remark': '注册会计师'
        },
        {
            'employee_no': 'EMP202601-003', 'name': '王五', 'gender': 'male',
            'phone': '13800138003', 'email': 'wangwu@company.com',
            'id_card': '440101199803033456', 'birth_date': date(1998, 3, 3),
            'department': '销售部', 'position': '销售专员',
            'education': 'college', 'graduate_school': '深圳大学',
            'entry_date': date(2026, 1, 10), 'probation_end_date': date(2026, 4, 10),
            'contract_end_date': date(2027, 1, 10),
            'bank_name': '招商银行', 'bank_account': '6222021234567890003',
            'emergency_contact': '王兄', 'emergency_phone': '13900139003',
            'status': 'probation', 'address': '深圳市南山区',
            'remark': '新员工试用期'
        },
        {
            'employee_no': 'EMP202601-004', 'name': '赵六', 'gender': 'female',
            'phone': '13800138004', 'email': 'zhaoliu@company.com',
            'id_card': '500101199111114567', 'birth_date': date(1991, 11, 11),
            'department': '人力资源部', 'position': 'HR主管',
            'education': 'bachelor', 'graduate_school': '四川大学',
            'entry_date': date(2021, 9, 1), 'contract_end_date': date(2026, 9, 1),
            'bank_name': '中国农业银行', 'bank_account': '6222021234567890004',
            'emergency_contact': '赵父', 'emergency_phone': '13900139004',
            'status': 'active', 'address': '成都市武侯区',
            'remark': '负责招聘培训'
        },
        {
            'employee_no': 'EMP202601-005', 'name': '孙七', 'gender': 'male',
            'phone': '13800138005', 'email': 'sunqi@company.com',
            'id_card': '420101198505055678', 'birth_date': date(1985, 5, 5),
            'department': '技术部', 'position': '技术总监',
            'education': 'master', 'graduate_school': '华中科技大学',
            'entry_date': date(2020, 1, 1), 'contract_end_date': date(2025, 5, 1),
            'bank_name': '中国银行', 'bank_account': '6222021234567890005',
            'emergency_contact': '孙妻', 'emergency_phone': '13900139005',
            'status': 'active', 'address': '武汉市洪山区',
            'remark': '合同即将到期'
        },
        {
            'employee_no': 'EMP202601-006', 'name': '周八', 'gender': 'female',
            'phone': '13800138006', 'email': 'zhouba@company.com',
            'id_card': '330101199707076789', 'birth_date': date(1997, 7, 7),
            'department': '市场部', 'position': '市场专员',
            'education': 'bachelor', 'graduate_school': '浙江大学',
            'entry_date': date(2024, 7, 1), 'probation_end_date': date(2024, 10, 1),
            'contract_end_date': date(2025, 7, 1),
            'bank_name': '交通银行', 'bank_account': '6222021234567890006',
            'emergency_contact': '周母', 'emergency_phone': '13900139006',
            'status': 'probation', 'address': '杭州市西湖区',
            'remark': '试用期中'
        },
        {
            'employee_no': 'EMP202601-007', 'name': '吴九', 'gender': 'male',
            'phone': '13800138007', 'email': 'wujiu@company.com',
            'id_card': '610101198808088890', 'birth_date': date(1988, 8, 8),
            'department': '生产部', 'position': '生产主管',
            'education': 'high_school', 'graduate_school': '',
            'entry_date': date(2019, 5, 1), 'resignation_date': date(2026, 1, 15),
            'bank_name': '中国邮政储蓄银行', 'bank_account': '6222021234567890007',
            'emergency_contact': '吴父', 'emergency_phone': '13900139007',
            'status': 'resigned', 'address': '西安市雁塔区',
            'remark': '已离职'
        },
        {
            'employee_no': 'EMP202601-008', 'name': '郑十', 'gender': 'female',
            'phone': '13800138008', 'email': 'zhengshi@company.com',
            'id_card': '350101199404049901', 'birth_date': date(1994, 4, 4),
            'department': '采购部', 'position': '采购专员',
            'education': 'bachelor', 'graduate_school': '厦门大学',
            'entry_date': date(2023, 8, 1), 'contract_end_date': date(2026, 8, 1),
            'bank_name': '兴业银行', 'bank_account': '6222021234567890008',
            'emergency_contact': '郑兄', 'emergency_phone': '13900139008',
            'status': 'active', 'address': '厦门市思明区',
            'remark': ''
        },
    ]

    for data in employees_data:
        emp, created = Employee.objects.get_or_create(
            employee_no=data['employee_no'],
            defaults=data
        )
        if created:
            print(f"  创建员工: {emp.employee_no} - {emp.name} - {emp.department} - {emp.get_status_display()}")
        else:
            print(f"  已存在: {emp.employee_no} - {emp.name}")

    print(f"\n员工档案测试数据生成完成！共 {Employee.objects.count()} 条记录。")
    print(f"  在职: {Employee.objects.filter(status='active').count()}")
    print(f"  试用期: {Employee.objects.filter(status='probation').count()}")
    print(f"  离职: {Employee.objects.filter(status='resigned').count()}")


if __name__ == '__main__':
    run()
