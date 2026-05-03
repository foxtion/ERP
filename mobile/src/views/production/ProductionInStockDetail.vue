<template>
  <div class="detail-page">
    <div v-if="detail" class="detail-wrap">
      <div class="info-card">
        <div class="detail-header">
          <div class="detail-no">{{ detail.stock_no }}</div>
          <van-tag :type="statusTypeMap[detail.status] || 'default'">
            {{ statusMap[detail.status] || detail.status }}
          </van-tag>
        </div>
        <div class="meta-info">
          <div class="meta-item">
            <span class="label">关联工单：</span>
            <span class="value">{{ detail.production_order_no || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">入库日期：</span>
            <span class="value">{{ detail.stock_date || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">仓库：</span>
            <span class="value">{{ detail.warehouse || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">产品：</span>
            <span class="value">{{ detail.product_name || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">数量：</span>
            <span class="value">{{ detail.quantity || 0 }}</span>
          </div>
          <div class="meta-item" v-if="detail.remark">
            <span class="label">备注：</span>
            <span class="value">{{ detail.remark }}</span>
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
import { getProductionInStockDetail } from '@/api/production'

const route = useRoute()
const detail = ref(null)

const statusMap = { draft: '草稿', submitted: '已提交', approved: '已审核', confirmed: '已入库', cancelled: '已取消' }
const statusTypeMap = { draft: 'default', submitted: 'primary', approved: 'warning', confirmed: 'success', cancelled: 'danger' }

onMounted(async () => {
  try {
    const res = await getProductionInStockDetail(route.params.id)
    detail.value = res.data
  } catch (e) {
    showToast('加载详情失败')
  }
})
</script>

<style scoped>
.detail-wrap { padding-bottom: 20px; }
.info-card { margin: 10px 12px; background-color: #fff; border-radius: 8px; padding: 12px; }
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.detail-no { font-size: 16px; font-weight: bold; color: #323233; }
.meta-info { font-size: 13px; }
.meta-item { display: flex; padding: 4px 0; }
.meta-item .label { color: #969799; width: 70px; }
</style>
