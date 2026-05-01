<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="getRequestList"
    search-placeholder="搜索申请单号"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('purchase:request:add')"
    @add="onAdd"
  >
    <template #list="{ list }">
      <div v-for="item in list" :key="item.id" class="card-item">
        <div class="card-header">
          <span class="title">{{ item.request_no }}</span>
          <StatusTag
            :status="item.status"
            :options="statusOptions"
            :type-map="statusTypeMap"
          />
        </div>
        <div class="card-body">
          <div><span class="label">申请日期：</span>{{ item.request_date || '-' }}</div>
          <div><span class="label">申请人：</span>{{ item.requester_name || '-' }}</div>
          <div><span class="label">总金额：</span><span class="amount">¥{{ Number(item.total_amount || 0).toFixed(2) }}</span></div>
          <div><span class="label">备注：</span>{{ item.remark || '-' }}</div>
        </div>
        <div class="card-actions">
          <van-button
            v-if="userStore.hasPermission('purchase:request:operate') && item.status === 'pending'"
            size="small"
            type="primary"
            plain
            @click="onConvert(item)"
          >
            转订单
          </van-button>
          <van-button
            v-if="userStore.hasPermission('purchase:request:edit')"
            size="small"
            type="primary"
            plain
            @click="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('purchase:request:delete')"
            size="small"
            type="danger"
            plain
            @click="onDelete(item)"
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
import { showDialog, showToast, showLoadingToast, closeToast } from 'vant'
import ListPage from '@/components/ListPage.vue'
import StatusTag from '@/components/StatusTag.vue'
import { useUserStore } from '@/store/user'
import { getRequestList, deleteRequest, convertRequestToOrder } from '@/api/purchase'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref()

const statusOptions = {
  pending: '待审批',
  approved: '已审批',
  rejected: '已驳回',
  converted: '已转单',
}

const statusTypeMap = {
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  converted: 'primary',
}

const onAdd = () => {
  router.push('/purchase/request/add')
}

const onEdit = (item) => {
  router.push(`/purchase/request/edit/${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showDialog({
      title: '确认删除',
      message: `确定删除申请单「${item.request_no}」吗？`,
    })
    showLoadingToast({ message: '删除中...', forbidClick: true })
    await deleteRequest(item.id)
    closeToast()
    showToast('删除成功')
    listPageRef.value?.onRefresh()
  } catch (error) {
    closeToast()
    if (error !== 'cancel') {
      showToast(error.message || '删除失败')
    }
  }
}

const onConvert = async (item) => {
  try {
    await showDialog({
      title: '确认转单',
      message: `确定将申请单「${item.request_no}」转为采购订单吗？`,
    })
    showLoadingToast({ message: '处理中...', forbidClick: true })
    await convertRequestToOrder(item.id)
    closeToast()
    showToast('转单成功')
    listPageRef.value?.onRefresh()
  } catch (error) {
    closeToast()
    if (error !== 'cancel') {
      showToast(error.message || '转单失败')
    }
  }
}
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
.card-body {
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}
.label {
  color: #999;
}
.amount {
  color: #ee0a24;
  font-weight: 600;
}
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}
</style>
