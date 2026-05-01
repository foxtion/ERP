<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="getTransferList"
    search-placeholder="搜索调拨单号"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('inventory:transfer:add')"
    @add="onAdd"
  >
    <template #list="{ list }">
      <div v-for="item in list" :key="item.id" class="card-item">
        <div class="card-header">
          <span class="title">{{ item.transfer_no }}</span>
          <StatusTag
            :status="item.status"
            :options="statusOptions"
            :type-map="statusTypeMap"
          />
        </div>
        <div class="card-body">
          <div><span class="label">调拨日期：</span>{{ item.transfer_date || '-' }}</div>
          <div><span class="label">调出仓库：</span>{{ item.from_warehouse_name || '-' }}</div>
          <div><span class="label">调入仓库：</span>{{ item.to_warehouse_name || '-' }}</div>
          <div><span class="label">物料：</span>{{ item.material_name || '-' }}</div>
          <div><span class="label">调拨数量：</span>{{ item.quantity || 0 }}</div>
          <div><span class="label">经办人：</span>{{ item.operator_name || '-' }}</div>
        </div>
        <div class="card-actions">
          <van-button
            v-if="userStore.hasPermission('inventory:transfer:edit')"
            size="small"
            type="primary"
            plain
            @click="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('inventory:transfer:delete')"
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
import { getTransferList, deleteTransfer } from '@/api/inventory'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref()

const statusOptions = {
  pending: '待审核',
  approved: '已审核',
  completed: '已完成',
  cancelled: '已取消',
}

const statusTypeMap = {
  pending: 'warning',
  approved: 'primary',
  completed: 'success',
  cancelled: 'danger',
}

const onAdd = () => {
  router.push('/inventory/transfer/add')
}

const onEdit = (item) => {
  router.push(`/inventory/transfer/edit/${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showDialog({
      title: '确认删除',
      message: `确定删除调拨单「${item.transfer_no}」吗？`,
    })
    showLoadingToast({ message: '删除中...', forbidClick: true })
    await deleteTransfer(item.id)
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
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}
</style>
