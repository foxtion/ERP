<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="getCheckList"
    search-placeholder="搜索盘点单号/仓库"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('inventory:check:add')"
    @add="onAdd"
  >
    <template #list="{ list }">
      <div v-for="item in list" :key="item.id" class="card-item">
        <div class="card-header">
          <span class="title">{{ item.check_no }}</span>
          <StatusTag
            :status="item.status"
            :options="statusOptions"
            :type-map="statusTypeMap"
          />
        </div>
        <div class="card-body">
          <div><span class="label">盘点日期：</span>{{ item.check_date || '-' }}</div>
          <div><span class="label">盘点仓库：</span>{{ item.warehouse_name || '-' }}</div>
          <div><span class="label">盘点类型：</span>{{ item.check_type_display || item.check_type || '-' }}</div>
          <div><span class="label">盘点人：</span>{{ item.checker_name || '-' }}</div>
          <div><span class="label">盈亏数量：</span><span :class="item.diff_quantity > 0 ? 'profit' : item.diff_quantity < 0 ? 'loss' : ''">{{ item.diff_quantity || 0 }}</span></div>
          <div><span class="label">备注：</span>{{ item.remark || '-' }}</div>
        </div>
        <div class="card-actions">
          <van-button
            v-if="userStore.hasPermission('inventory:check:edit')"
            size="small"
            type="primary"
            plain
            @click="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('inventory:check:delete')"
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
import { getCheckList, deleteCheck } from '@/api/inventory'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref()

const statusOptions = {
  pending: '待盘点',
  checking: '盘点中',
  completed: '已完成',
  cancelled: '已取消',
}

const statusTypeMap = {
  pending: 'warning',
  checking: 'primary',
  completed: 'success',
  cancelled: 'danger',
}

const onAdd = () => {
  router.push('/inventory/check/add')
}

const onEdit = (item) => {
  router.push(`/inventory/check/edit/${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showDialog({
      title: '确认删除',
      message: `确定删除盘点单「${item.check_no}」吗？`,
    })
    showLoadingToast({ message: '删除中...', forbidClick: true })
    await deleteCheck(item.id)
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
.profit {
  color: #07c160;
  font-weight: 600;
}
.loss {
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
