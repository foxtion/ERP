<template>
  <div class="detail-page">
    <div v-if="detail" class="detail-wrap">
      <div class="info-card">
        <div class="detail-header">
          <div class="detail-no">{{ detail.doc_no }}</div>
          <van-tag :type="detail.doc_type === 'receivable' ? 'primary' : 'warning'">
            {{ detail.doc_type === 'receivable' ? '应收' : '应付' }}
          </van-tag>
        </div>
        <div class="meta-info">
          <div class="meta-item">
            <span class="label">往来单位：</span>
            <span class="value">{{ detail.counterparty || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">金额：</span>
            <span class="value amount">¥ {{ Number(detail.amount || 0).toFixed(2) }}</span>
          </div>
          <div class="meta-item">
            <span class="label">业务日期：</span>
            <span class="value">{{ detail.bill_date || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">状态：</span>
            <van-tag :type="statusTypeMap[detail.status] || 'default'" size="small">
              {{ statusMap[detail.status] || detail.status }}
            </van-tag>
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
import { getReceivableDetail } from '@/api/finance'

const route = useRoute()
const detail = ref(null)

const statusMap = { unsettled: '未结算', partial: '部分结算', settled: '已结清' }
const statusTypeMap = { unsettled: 'danger', partial: 'warning', settled: 'success' }

onMounted(async () => {
  try {
    const res = await getReceivableDetail(route.params.id)
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
.amount { color: #ee0a24; font-weight: 600; }
</style>
