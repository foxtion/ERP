import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
django.setup()

from apps.inventory.models import Inventory

def main():
    queryset = Inventory.objects.all()
    total = queryset.count()
    print(f'>>> 开始同步库存预警，共 {total} 条库存记录')
    updated = 0
    for idx, inv in enumerate(queryset.iterator(), 1):
        inv.save()
        updated += 1
        if idx % 500 == 0:
            print(f'  已处理 {idx}/{total}')
    print(f'>>> 同步完成，共更新 {updated} 条记录')

if __name__ == '__main__':
    main()
