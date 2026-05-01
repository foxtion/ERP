<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    search-placeholder="搜索单据号/往来单位"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('finance:receivable:add')"
    @add="onAdd"
  >
    <template #list="{ list }">
      <div
        v-for="item in list"
        :key="item.id"
        class="card"
        @click="onDetail(item)"
      >
        <div class="card-header">
          <span class="title">{{ item.bill_no }}</span>
          <van-tag :type="typeTypeMap[item.bill_type] || 'default'">
            {{ typeMap[item.bill_type] || item.bill_type }}
          </van-tag>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">往来单位</span>
            <span class="value">{{ item.counterparty_name }}</span>
          </div>
          <div class="info-row">
            <span class="label">金额</span>
            <span class="value amount">¥ {{ Number(item.amount || 0).toFixed(2) }}</span>
          </div>
          <div class="info-row">
            <span class="label">业务日期</span>
            <span class="value">{{ item.bill_date }}</span>
          </div>
          <div class="info-row">
            <span class="label">状态</span>
            <van-tag :type="statusTypeMap[item.status] || 'default'" size="small">
              {{ statusMap[item.status] || item.status }}
            </van-tag>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="userStore.hasPermission('finance:receivable:edit')"
            size="small"
            type="primary"
            plain
            @click.stop="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('finance:receivable:delete')"
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
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import ListPage from '@/components/ListPage.vue'
import { getReceivableList, deleteReceivable } from '@/api/finance'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref(null)

const query = ref({ search: '' })

const typeMap = {
  receivable: '应收',
  payable: '应付',
}

const typeTypeMap = {
  receivable: 'primary',
  payable: 'warning',
}

const statusMap = {
  unsettled: '未结算',
  partial: '部分结算',
  settled: '已结清',
}

const statusTypeMap = {
  unsettled: 'danger',
  partial: 'warning',
  settled: 'success',
}

const fetchApi = (params) => getReceivableList(params)

const onAdd = () => {
  router.push('/finance/receivable/add')
}

const onDetail = (item) => {
  router.push(`/finance/receivable/detail/${item.id}`)
}

const onEdit = (item) => {
  router.push(`/finance/receivable/edit/${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定删除单据 "${item.bill_no}" 吗？`,
    })
    await deleteReceivable(item.id)
    showToast({ type: 'success', message: '删除成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') {
      showToast({ type: 'fail', message: '删除失败' })
    }
  }
}
</script>

<style scoped>
.card {
  margin: 10px 12px;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
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
  color: #323233;
}
.card-body {
  margin-bottom: 10px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
}
.label {
  color: #969799;
}
.value {
  color: #323233;
}
.amount {
  color: #ee0a24;
  font-weight: 600;
}
.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #f5f5f5;
}
</style>
