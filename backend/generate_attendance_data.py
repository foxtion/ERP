"""
初始化人事管理-考勤记录测试数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
django.setup()

from datetime import date, timedelta, time
import random
from apps.hr.models import Employee, Attendance


def run():
    print("开始生成考勤记录测试数据...")

    employees = list(Employee.objects.filter(status__in=['active', 'probation']))
    if not employees:
        print("未找到在职员工，跳过数据生成")
        return

    # 生成最近30天的考勤记录
    today = date.today()
    statuses = ['normal', 'normal', 'normal', 'normal', 'late', 'early', 'leave', 'absent']
    created_count = 0

    for i in range(30):
        record_date = today - timedelta(days=i)
        # 跳过周末
        if record_date.weekday() >= 5:
            continue

        for emp in employees:
            # 随机状态，大部分正常
            status = random.choice(statuses)

            if status == 'absent':
                check_in = None
                check_out = None
            elif status == 'leave':
                check_in = None
                check_out = None
            elif status == 'late':
                check_in = time(9, random.randint(5, 45))
                check_out = time(18, random.randint(0, 30))
            elif status == 'early':
                check_in = time(8, random.randint(30, 55))
                check_out = time(16, random.randint(0, 30))
            else:
                check_in = time(8, random.randint(45, 59))
                check_out = time(18, random.randint(0, 15))

            try:
                Attendance.objects.update_or_create(
                    employee=emp,
                    date=record_date,
                    defaults={
                        'check_in': check_in,
                        'check_out': check_out,
                        'status': status,
                        'remark': ''
                    }
                )
                created_count += 1
            except Exception as e:
                print(f"  错误: {emp.name} {record_date} - {e}")

    print(f"\n考勤记录测试数据生成完成！共 {created_count} 条记录。")
    print(f"  正常: {Attendance.objects.filter(status='normal').count()}")
    print(f"  迟到: {Attendance.objects.filter(status='late').count()}")
    print(f"  早退: {Attendance.objects.filter(status='early').count()}")
    print(f"  旷工: {Attendance.objects.filter(status='absent').count()}")
    print(f"  请假: {Attendance.objects.filter(status='leave').count()}")


if __name__ == '__main__':
    run()
