<template>
  <div class="detail-page">
    <div v-if="detail" class="detail-wrap">
      <div class="info-card">
        <div class="detail-header">
          <div class="detail-no">{{ detail.stock_no }}</div>
          <van-tag type="success" size="medium">已出库</van-tag>
        </div>
        <div class="meta-info">
          <div class="meta-item">
            <span class="label">关联订单：</span>
            <span class="value">{{ detail.order_no || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">出库日期：</span>
            <span class="value">{{ detail.stock_date || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">仓库：</span>
            <span class="value">{{ detail.warehouse || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">操作人：</span>
            <span class="value">{{ detail.operator_name || '-' }}</span>
          </div>
          <div class="meta-item" v-if="detail.remark">
            <span class="label">备注：</span>
            <span class="value">{{ detail.remark }}</span>
          </div>
        </div>
      </div>

      <div class="section-title">出库明细（{{ detail.items?.length || 0 }}）</div>
      <div class="item-list">
        <div v-for="item in detail.items" :key="item.id" class="item-card">
          <div class="item-header">
            <div class="item-name">{{ item.material_name }}</div>
            <div class="item-qty">{{ item.quantity }} {{ item.unit }}</div>
          </div>
          <div class="item-body">
            <div class="item-info">
              <span class="label">规格：</span>
              <span>{{ item.spec || '-' }}</span>
            </div>
            <div class="item-info" v-if="item.remark">
              <span class="label">备注：</span>
              <span>{{ item.remark }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { showToast } from 'vant'
import { getOutStockDetail } from '@/api/sales'

const route = useRoute()
const detail = ref(null)

onMounted(async () => {
  try {
    const res = await getOutStockDetail(route.params.id)
    detail.value = res.data
  } catch (e) {
    showToast('加载详情失败')
  }
})
</script>

<style scoped>
.detail-wrap {
  padding-bottom: 20px;
}
.info-card {
  margin: 10px 12px;
  background-color: #fff;
  border-radius: 8px;
  padding: 12px;
}
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.detail-no {
  font-size: 16px;
  font-weight: bold;
  color: #323233;
}
.meta-info {
  font-size: 13px;
}
.meta-item {
  display: flex;
  padding: 4px 0;
}
.meta-item .label {
  color: #969799;
  width: 70px;
}
.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #666;
  padding: 12px 12px 8px;
}
.item-list {
  padding: 0 12px;
}
.item-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
}
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.item-name {
  font-size: 15px;
  font-weight: bold;
  color: #323233;
}
.item-qty {
  font-size: 14px;
  color: #1989fa;
  font-weight: 600;
}
.item-body {
  font-size: 13px;
  color: #666;
}
.item-info {
  display: flex;
  padding: 3px 0;
}
.item-info .label {
  color: #969799;
  width: 50px;
}
</style>
