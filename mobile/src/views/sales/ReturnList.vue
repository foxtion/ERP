<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    show-search
    search-placeholder="搜索退货单号/客户名称"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('sales:return:add')"
    @add="onAdd"
  >
    <template #list="{ list }">
      <div
        v-for="item in list"
        :key="item.id"
        class="card"
        @click="goDetail(item)"
      >
        <div class="card-header">
          <span class="title">{{ item.return_no }}</span>
          <StatusTag
            :status="item.status"
            :options="{ pending: '待处理', approved: '已审批', rejected: '已驳回', completed: '已完成' }"
            :type-map="{ pending: 'warning', approved: 'primary', rejected: 'danger', completed: 'success' }"
          />
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">客户：</span>
            <span class="value">{{ item.customer_name }}</span>
          </div>
          <div class="info-row">
            <span class="label">退货日期：</span>
            <span class="value">{{ item.return_date }}</span>
          </div>
          <div class="info-row">
            <span class="label">总金额：</span>
            <span class="value amount">¥{{ item.total_amount }}</span>
          </div>
          <div class="info-row">
            <span class="label">退货原因：</span>
            <span class="value">{{ item.reason || '-' }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="userStore.hasPermission('sales:return:edit') && item.status === 'pending'"
            size="small"
            type="primary"
            plain
            @click.stop="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('sales:return:delete')"
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
import { useUserStore } from '@/store/user'
import { getReturnList, deleteReturn } from '@/api/sales'
import ListPage from '@/components/ListPage.vue'
import StatusTag from '@/components/StatusTag.vue'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref(null)

const query = ref({ search: '' })
const fetchApi = getReturnList

const onAdd = () => {
  router.push('/sales/return-form')
}

const goDetail = (item) => {
  router.push(`/sales/return-detail/${item.id}`)
}

const onEdit = (item) => {
  router.push(`/sales/return-form?id=${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定删除退货单「${item.return_no}」吗？`,
    })
    await deleteReturn(item.id)
    showToast('删除成功')
    listPageRef.value?.onRefresh()
  } catch (e) {
    // 取消或失败
  }
}
</script>

<style scoped>
.card {
  margin: 10px 12px;
  padding: 12px;
  background-color: #fff;
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
  margin-bottom: 4px;
  font-size: 13px;
  color: #666;
}
.label {
  color: #969799;
  min-width: 70px;
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
}
</style>
