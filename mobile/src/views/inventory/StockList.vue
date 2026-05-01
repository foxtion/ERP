<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="getStockList"
    search-placeholder="搜索物料名称/编码"
    :show-add="false"
  >
    <template #list="{ list }">
      <div v-for="item in list" :key="item.id" class="card-item">
        <div class="card-header">
          <span class="title">{{ item.material_name }}</span>
          <span class="quantity">{{ item.quantity }}</span>
        </div>
        <div class="card-body">
          <div><span class="label">物料编码：</span>{{ item.material_code || '-' }}</div>
          <div><span class="label">规格：</span>{{ item.specification || '-' }}</div>
          <div><span class="label">仓库：</span>{{ item.warehouse_name || '-' }}</div>
          <div><span class="label">库位：</span>{{ item.location_name || '-' }}</div>
          <div><span class="label">可用数量：</span><span class="available">{{ item.available_quantity || 0 }}</span></div>
          <div><span class="label">锁定数量：</span>{{ item.locked_quantity || 0 }}</div>
        </div>
      </div>
    </template>
  </ListPage>
</template>

<script setup>
import { ref } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getStockList } from '@/api/inventory'

const listPageRef = ref()
</script>

<style scoped>
.card-item {
  margin: 10px 12px;
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}
.quantity {
  font-size: 16px;
  font-weight: 700;
  color: #1989fa;
}
.card-body {
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}
.label {
  color: #999;
}
.available {
  color: #07c160;
  font-weight: 600;
}
</style>
