<template>
  <div class="detail-page">
    <div v-if="detail" class="detail-wrap">
      <div class="info-card">
        <div class="detail-header">
          <div class="detail-no">{{ detail.plan_no }}</div>
          <van-tag :type="statusTypeMap[detail.status] || 'default'">
            {{ statusMap[detail.status] || detail.status }}
          </van-tag>
        </div>
        <div class="meta-info">
          <div class="meta-item">
            <span class="label">产品名称：</span>
            <span class="value">{{ detail.product_name || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">产品编码：</span>
            <span class="value">{{ detail.product_code || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">计划日期：</span>
            <span class="value">{{ detail.plan_date || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">计划数量：</span>
            <span class="value">{{ detail.quantity || 0 }}</span>
          </div>
          <div class="meta-item" v-if="detail.bom_product_name">
            <span class="label">关联BOM：</span>
            <span class="value">{{ detail.bom_product_name }}</span>
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
import { getPlanDetail } from '@/api/production'

const route = useRoute()
const detail = ref(null)

const statusMap = { draft: '草稿', confirmed: '已确认', cancelled: '已取消', completed: '已完成' }
const statusTypeMap = { draft: 'default', confirmed: 'primary', cancelled: 'danger', completed: 'success' }

onMounted(async () => {
  try {
    const res = await getPlanDetail(route.params.id)
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
</style>
