<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="getPurchaseOrderList"
    search-placeholder="搜索订单编号/供应商"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('purchase:order:add')"
    @add="onAdd"
  >
    <template #list="{ list }">
      <div v-for="item in list" :key="item.id" class="card-item">
        <div class="card-header">
          <span class="title">{{ item.order_no }}</span>
          <StatusTag
            :status="item.status"
            :options="statusOptions"
            :type-map="statusTypeMap"
          />
        </div>
        <div class="card-body">
          <div><span class="label">供应商：</span>{{ item.supplier_name || '-' }}</div>
          <div><span class="label">订单日期：</span>{{ item.order_date || '-' }}</div>
          <div><span class="label">交货日期：</span>{{ item.delivery_date || '-' }}</div>
          <div><span class="label">总金额：</span><span class="amount">¥{{ Number(item.total_amount || 0).toFixed(2) }}</span></div>
        </div>
        <div class="card-actions">
          <van-button
            v-if="userStore.hasPermission('purchase:order:operate') && item.status === 'draft'"
            size="small"
            type="primary"
            @click="onConfirm(item)"
          >
            确认
          </van-button>
          <van-button
            v-if="userStore.hasPermission('purchase:order:operate') && ['draft', 'confirmed'].includes(item.status)"
            size="small"
            type="warning"
            plain
            @click="onCancel(item)"
          >
            取消
          </van-button>
          <van-button
            v-if="userStore.hasPermission('purchase:order:operate') && item.status === 'confirmed'"
            size="small"
            type="success"
            @click="onComplete(item)"
          >
            完成
          </van-button>
          <van-button
            v-if="userStore.hasPermission('purchase:order:edit')"
            size="small"
            type="primary"
            plain
            @click="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('purchase:order:delete')"
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
import {
  getPurchaseOrderList,
  deletePurchaseOrder,
  confirmPurchaseOrder,
  cancelPurchaseOrder,
  completePurchaseOrder,
} from '@/api/purchase'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref()

const statusOptions = {
  draft: '草稿',
  confirmed: '已确认',
  cancelled: '已取消',
  completed: '已完成',
}

const statusTypeMap = {
  draft: 'default',
  confirmed: 'primary',
  cancelled: 'danger',
  completed: 'success',
}

const onAdd = () => {
  router.push('/purchase/order-form')
}

const onEdit = (item) => {
  router.push(`/purchase/order-form?id=${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showDialog({
      title: '确认删除',
      message: `确定删除订单「${item.order_no}」吗？`,
    })
    showLoadingToast({ message: '删除中...', forbidClick: true })
    await deletePurchaseOrder(item.id)
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

const onConfirm = async (item) => {
  try {
    await showDialog({
      title: '确认订单',
      message: `确定确认订单「${item.order_no}」吗？`,
    })
    showLoadingToast({ message: '处理中...', forbidClick: true })
    await confirmPurchaseOrder(item.id)
    closeToast()
    showToast('确认成功')
    listPageRef.value?.onRefresh()
  } catch (error) {
    closeToast()
    if (error !== 'cancel') {
      showToast(error.message || '确认失败')
    }
  }
}

const onCancel = async (item) => {
  try {
    await showDialog({
      title: '取消订单',
      message: `确定取消订单「${item.order_no}」吗？`,
    })
    showLoadingToast({ message: '处理中...', forbidClick: true })
    await cancelPurchaseOrder(item.id)
    closeToast()
    showToast('取消成功')
    listPageRef.value?.onRefresh()
  } catch (error) {
    closeToast()
    if (error !== 'cancel') {
      showToast(error.message || '取消失败')
    }
  }
}

const onComplete = async (item) => {
  try {
    await showDialog({
      title: '完成订单',
      message: `确定完成订单「${item.order_no}」吗？`,
    })
    showLoadingToast({ message: '处理中...', forbidClick: true })
    await completePurchaseOrder(item.id)
    closeToast()
    showToast('已完成')
    listPageRef.value?.onRefresh()
  } catch (error) {
    closeToast()
    if (error !== 'cancel') {
      showToast(error.message || '操作失败')
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
  flex-wrap: wrap;
}
</style>
