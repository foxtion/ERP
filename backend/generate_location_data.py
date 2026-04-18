#!/usr/bin/env python
"""
仓库库位管理测试数据生成脚本
数据参照金山文档表格
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.inventory.models import Warehouse, WarehouseLocation

# 有货库位数据（编码, 货物名称, 大小）
# 条码规则：有货的库位条码与库位编码一致（如 A00F101），部分为空
OCCUPIED_LOCATIONS = [
    ("A00F101", "D1247", "水晶形长条模具", "小"),
    ("A00F102", "D5985", "复活节兔子软陶泥模具", "小"),
    ("A00F103", "D5145", "房子插排", "小"),
    ("A00F104", "D3625", "椭圆碟子", "小"),
    ("A00F105", "D5388-3", "六连圆圈", "小"),
    ("A00F106", "D6151-1", "太阳花收纳盒盖", "小"),
    ("A00F107", "D6151-2", "太阳花收纳盒底/树桩花盆", "小"),
    ("A00F108", "D4850-2", "啄木鸟钟摆模具", "小"),
    ("A00F109", "D0541", "高透免打磨球25mm", "小"),
    ("A00F110", "D4439", "圣诞树蜡烛杯", "小"),
    ("A00F111", "D2611", "六边满芒星杯垫模具", "小"),
    ("A00F112", "D4905", "锥行中号", "小"),
    ("A00F113", "D4906", "锥形小号", "小"),
    ("A00F114", "D4904", "锥形大号", "小"),
    ("A00F115", "D5542", "天鹅摆件左01", "小"),
    ("A00F116", "D5543", "天鹅摆件右02", "小"),
    ("A00F117", "D3926", "圆形花瓶模具", "小"),
    ("A00F118", "D3927", "矮胖形花瓶模具", "小"),
    ("A00F201", "D5129", "兔子骑车摆件", "小"),
    ("A00F202", "D5130", "兔子蝴蝶摆件模具", "小"),
    ("A00F203", "D5220", "7连爱心兔子整版02", "小"),
    ("A00F204", "D2282", "圆形摆台模具7in本色", "小"),
    ("A00F205", "D4567", "08254-吊坠模具", "小"),
    ("A00F206", "D1921", "新款大方托盘", "小"),
    ("A00F207", "D5193", "复活节大号镂空兔子", "小"),
    ("A00F208", "D3163", "梳子03", "小"),
    ("A00F209", "D0799", "镜面不规则长方托盘模具（小号）", "小"),
    ("A00F210", "D1259H", "白色垫片中20*15", "小"),
    ("A00F211", "D3321", "D3321", "小"),
    ("A00F212", "D2610", "六边十二芒星杯垫", "小"),
    ("A00F213", "D5006", "D5006", "小"),
    ("A00F214", "D4374", "圣诞雪花礼物盒模具", "小"),
    ("A00F215", "D4375", "圣诞帽子麋鹿模具", "小"),
    ("A00F216", "D4376", "圣诞手套毛衣模具", "小"),
    ("A00F217", "D5254", "大圆盘", "小"),
    ("A00F218", "D1106", "迷你4连猫爪模具（02）", "小"),
    ("A00F301", "D4950", "骷髅头模具", "小"),
    ("A00F302", "D0336", "镜面手环模具（内径90mm）", "小"),
    ("A00F303", "D4765", "蜡烛杯", "小"),
    ("A00F304", "D4990", "巧克力模具（咖啡色）", "小"),
    ("A00F305", "D3420-2", "小领结收纳盒（盖）", "小"),
    ("A00F306", "D5518", "纸杯蛋糕蜡烛摆件", "小"),
    ("A00F307", "D3049", "D3049", "小"),
    ("A00F308", "D2516", "免打磨正方体模具2.2in", "小"),
    ("A00F309", "D3689", "35*15*16长方体模具", "小"),
    ("A00F310", "D5995-2", "圣诞圆环托盘配件", "小"),
    ("A00F311", "D5995-1", "圆环圣诞托盘", "小"),
    ("A00F312", "D1264", "卢恩符文占卜骰子（一套3个）", "小"),
    ("A00F313", "D5787-1", "南瓜杯垫模具", "小"),
    ("A00F314", "D5787-2", "南瓜杯垫支架模具", "小"),
    ("A00F315", "D3358", "大脚美国雪人模具", "小"),
    ("A00F316", "D3164", "梳子04", "小"),
    ("A00F317", "D3173", "4连四叶草蜡烛模具", "小"),
    ("A00F318", "D1266", "占卜圆盘小号", "小"),
    ("A01F101", "D4941", "姜饼人", "小"),
    ("A01F102", "D2581", "树腾书签硅胶模具", "小"),
    ("A01F103", "D4410", "折耳兔子蛋模具", "小"),
    ("A01F104", "D0872", "耳环吊坠模具03", "小"),
    ("A01F105", "D0647", "镜面小鹿模具", "小"),
    ("A01F106", "D5422", "镂空房子摆件", "小"),
    ("A01F107", "D0981", "镜面方形吊坠模具", "小"),
    ("A01F108", "D0576", "镜面小号树叶杯垫模具", "小"),
    ("A01F109", "D3053", "D3053", "小"),
    ("A01F110", "D5581-1", "齿轮蜡烛烛台", "小"),
    ("A01F111", "D5581-2", "三圆圌措烛摆台", "小"),
    ("A01F112", "D5581-3", "梅花蜡烛烛台", "小"),
    ("A01F113", "D5581-4", "圆形蜡烛烛台", "小"),
    ("A01F114", "D5586", "正方蜡烛摆台", "小"),
    ("A01F115", "D5587", "半圆圈蜡烛摆台", "小"),
    ("A01F116", "D5588", "辅南瓜蜡烛摆台", "小"),
    ("A01F117", "D5589", "圆环蜡烛摆台", "小"),
    ("A01F118", "D0364", "镜面手镯内径尺寸54mm", "小"),
]

# 空库位编码生成
EMPTY_LOCATIONS = []
# A00 区 F排 1-3层
for floor in range(1, 4):
    for num in range(1, 19):
        code = f"A00F{floor}{num:02d}"
        # 排除已有货物的库位
        occupied = [x[0] for x in OCCUPIED_LOCATIONS]
        if code not in occupied:
            EMPTY_LOCATIONS.append((code, "小"))

# A01 区 F排 1层（补充一些空位）
for num in range(1, 19):
    code = f"A01F1{num:02d}"
    occupied = [x[0] for x in OCCUPIED_LOCATIONS]
    if code not in occupied:
        EMPTY_LOCATIONS.append((code, "小"))

# B00 区 新增一些空库位
for floor in range(1, 4):
    for num in range(1, 19):
        code = f"B00F{floor}{num:02d}"
        EMPTY_LOCATIONS.append((code, random.choice(["小", "中", "大"])))


def main():
    print(">>> 开始生成仓库库位数据...")

    # 创建或获取默认仓库
    wh, created = Warehouse.objects.get_or_create(
        code="MAIN",
        defaults={"name": "主仓库", "location": "一楼", "manager": "管理员", "is_active": True}
    )
    if created:
        print(f"    创建仓库: {wh.name}")
    else:
        print(f"    使用已有仓库: {wh.name}")

    # 清空已有库位数据
    WarehouseLocation.objects.filter(warehouse=wh).delete()
    print(f"    清空仓库 {wh.name} 的旧库位数据")

    locations = []
    base_time = datetime.now() - timedelta(days=19)

    # 生成有货库位
    for loc_code, product_code, product_name, size in OCCUPIED_LOCATIONS:
        inbound = base_time + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        locations.append(WarehouseLocation(
            warehouse=wh,
            location_code=loc_code,
            barcode=loc_code if random.random() > 0.3 else '',
            size=size,
            product_code=product_code,
            product_name=product_name,
            is_empty=False,
            inbound_time=inbound,
            outbound_barcode='',
            remark=''
        ))

    # 生成空库位（只取前150个，避免数据过多）
    random.shuffle(EMPTY_LOCATIONS)
    for loc_code, size in EMPTY_LOCATIONS[:150]:
        locations.append(WarehouseLocation(
            warehouse=wh,
            location_code=loc_code,
            barcode='',
            size=size,
            product_code='',
            product_name='',
            is_empty=True,
            inbound_time=None,
            outbound_barcode='',
            remark=''
        ))

    WarehouseLocation.objects.bulk_create(locations, batch_size=100)

    total = WarehouseLocation.objects.filter(warehouse=wh).count()
    occupied = WarehouseLocation.objects.filter(warehouse=wh, is_empty=False).count()
    empty = WarehouseLocation.objects.filter(warehouse=wh, is_empty=True).count()
    print(f"    已创建 {total} 个库位（有货 {occupied}，空位 {empty}）")
    print(">>> 完成!")


if __name__ == '__main__':
    main()
