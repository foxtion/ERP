<template>
  <div class="detail-page">
    <div v-if="detail" class="detail-wrap">
      <div class="info-card">
        <div class="detail-header">
          <div class="detail-no">{{ detail.doc_no }}</div>
          <van-tag :type="detail.doc_type === 'receipt' ? 'success' : 'danger'">
            {{ detail.doc_type === 'receipt' ? '收款' : '付款' }}
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
            <span class="label">支付方式：</span>
            <span class="value">{{ methodMap[detail.payment_method] || detail.payment_method || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">日期：</span>
            <span class="value">{{ detail.payment_date || '-' }}</span>
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
import { getPaymentDetail } from '@/api/finance'

const route = useRoute()
const detail = ref(null)

const methodMap = {
  cash: '现金', bank_transfer: '银行转账', check: '支票', wechat: '微信支付', alipay: '支付宝',
}

onMounted(async () => {
  try {
    const res = await getPaymentDetail(route.params.id)
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
