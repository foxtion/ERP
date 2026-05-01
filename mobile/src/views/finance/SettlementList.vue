<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    search-placeholder="搜索单据号"
  >
    <template #list="{ list }">
      <div
        v-for="item in list"
        :key="item.id"
        class="card"
      >
        <div class="card-header">
          <span class="title">{{ item.settlement_no || item.id }}</span>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">收付款单</span>
            <span class="value">{{ item.payment_receipt_no || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">应收应付单</span>
            <span class="value">{{ item.receivable_payable_no || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">核销金额</span>
            <span class="value text-danger">¥{{ item.amount || 0 }}</span>
          </div>
          <div class="info-row">
            <span class="label">核销日期</span>
            <span class="value">{{ item.settlement_date || '-' }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="userStore.hasPermission('finance:settlement:delete')"
            size="small"
            type="danger"
            plain
            @click.stop="onDelete(item)"
          >
            删除
          </van-button>
        </div>
      </div>
    </template>
  </ListPage>
</template>

<script setup>
import { ref } from 'vue'
import { showConfirmDialog, showToast, showFailToast } from 'vant'
import { useUserStore } from '@/store/user'
import { getSettlementList, deleteSettlement } from '@/api/finance'
import ListPage from '@/components/ListPage.vue'

const userStore = useUserStore()
const listPageRef = ref()
const query = ref({})

const fetchApi = (params) => getSettlementList(params)

const onDelete = (item) => {
  showConfirmDialog({
    title: '确认删除',
    message: `确定删除核销记录吗？`,
  }).then(async () => {
    try {
      await deleteSettlement(item.id)
      showToast('删除成功')
      listPageRef.value.onRefresh()
    } catch (e) {
      showFailToast(e?.response?.data?.message || '删除失败')
    }
  }).catch(() => {})
}
</script>

<style scoped>
.card {
  margin: 8px 12px;
  background-color: #fff;
  border-radius: 8px;
  padding: 12px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.card-header .title {
  font-size: 15px;
  font-weight: bold;
  color: #323233;
}
.card-body {
  font-size: 13px;
  color: #666;
}
.info-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}
.info-row .label {
  color: #969799;
}
.info-row .value {
  color: #323233;
}
.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}
</style>
