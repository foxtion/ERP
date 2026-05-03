<template>
  <div class="detail-page">
    <div v-if="detail" class="detail-wrap">
      <div class="info-card">
        <div class="detail-header">
          <div class="detail-no">{{ detail.voucher_no }}</div>
          <van-tag :type="detail.status === 'audited' ? 'success' : 'default'">
            {{ detail.status === 'audited' ? '已审核' : '草稿' }}
          </van-tag>
        </div>
        <div class="meta-info">
          <div class="meta-item">
            <span class="label">凭证日期：</span>
            <span class="value">{{ detail.voucher_date || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">摘要：</span>
            <span class="value">{{ detail.summary || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">借方合计：</span>
            <span class="value amount">¥ {{ Number(detail.total_debit || 0).toFixed(2) }}</span>
          </div>
          <div class="meta-item">
            <span class="label">贷方合计：</span>
            <span class="value amount">¥ {{ Number(detail.total_credit || 0).toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <div class="section-title">凭证明细（{{ detail.items?.length || 0 }}）</div>
      <div class="item-list">
        <div v-for="item in detail.items" :key="item.id" class="item-card">
          <div class="item-header">
            <div class="item-name">{{ item.summary }}</div>
          </div>
          <div class="item-body">
            <div class="item-info"><span class="label">借方：</span><span class="amount">¥ {{ Number(item.debit || 0).toFixed(2) }}</span></div>
            <div class="item-info"><span class="label">贷方：</span><span class="amount">¥ {{ Number(item.credit || 0).toFixed(2) }}</span></div>
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
import { getVoucherDetail } from '@/api/finance'

const route = useRoute()
const detail = ref(null)

onMounted(async () => {
  try {
    const res = await getVoucherDetail(route.params.id)
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
.section-title { font-size: 14px; font-weight: bold; color: #666; padding: 12px 12px 8px; }
.item-list { padding: 0 12px; }
.item-card { background-color: #fff; border-radius: 8px; padding: 12px; margin-bottom: 10px; }
.item-header { margin-bottom: 8px; }
.item-name { font-size: 15px; font-weight: bold; color: #323233; }
.item-body { font-size: 13px; color: #666; }
.item-info { display: flex; padding: 3px 0; }
.item-info .label { color: #969799; width: 50px; }
</style>
