<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    search-placeholder="搜索工单编号/产品"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('production:workorder:add')"
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
          <span class="title">{{ item.order_no }}</span>
          <van-tag :type="statusTypeMap[item.status] || 'default'">
            {{ statusMap[item.status] || item.status }}
          </van-tag>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">产品</span>
            <span class="value">{{ item.product_name }}</span>
          </div>
          <div class="info-row">
            <span class="label">数量</span>
            <span class="value">{{ item.quantity }}</span>
          </div>
          <div class="info-row">
            <span class="label">计划日期</span>
            <span class="value">{{ item.plan_date }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="item.status === 'draft' && userStore.hasPermission('production:workorder:release')"
            size="small"
            type="primary"
            plain
            @click.stop="onRelease(item)"
          >
            下达
          </van-button>
          <van-button
            v-if="item.status === 'released' && userStore.hasPermission('production:workorder:start')"
            size="small"
            type="primary"
            plain
            @click.stop="onStart(item)"
          >
            开工
          </van-button>
          <van-button
            v-if="item.status === 'processing' && userStore.hasPermission('production:workorder:complete')"
            size="small"
            type="success"
            plain
            @click.stop="onComplete(item)"
          >
            完工
          </van-button>
          <van-button
            v-if="['draft', 'released'].includes(item.status) && userStore.hasPermission('production:workorder:cancel')"
            size="small"
            type="warning"
            plain
            @click.stop="onCancel(item)"
          >
            取消
          </van-button>
          <van-button
            v-if="item.status === 'draft' && userStore.hasPermission('production:workorder:edit')"
            size="small"
            type="primary"
            plain
            @click.stop="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="item.status === 'draft' && userStore.hasPermission('production:workorder:delete')"
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
import {
  getWorkOrderList,
  releaseWorkOrder,
  startWorkOrder,
  completeWorkOrder,
  cancelWorkOrder,
  deleteWorkOrder,
} from '@/api/production'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref(null)

const query = ref({ search: '' })

const statusMap = {
  draft: '草稿',
  released: '已下达',
  processing: '生产中',
  completed: '已完成',
  cancelled: '已取消',
}

const statusTypeMap = {
  draft: 'default',
  released: 'primary',
  processing: 'warning',
  completed: 'success',
  cancelled: 'danger',
}

const fetchApi = (params) => getWorkOrderList(params)

const onAdd = () => {
  router.push('/production/workorder/add')
}

const onDetail = (item) => {
  router.push(`/production/workorder/detail/${item.id}`)
}

const onEdit = (item) => {
  router.push(`/production/workorder/edit/${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定删除工单 "${item.order_no}" 吗？`,
    })
    await deleteWorkOrder(item.id)
    showToast({ type: 'success', message: '删除成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') {
      showToast({ type: 'fail', message: '删除失败' })
    }
  }
}

const onRelease = async (item) => {
  try {
    await showConfirmDialog({ title: '确认', message: '确定下达该工单吗？' })
    await releaseWorkOrder(item.id)
    showToast({ type: 'success', message: '下达成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') showToast({ type: 'fail', message: '操作失败' })
  }
}

const onStart = async (item) => {
  try {
    await showConfirmDialog({ title: '确认', message: '确定开工吗？' })
    await startWorkOrder(item.id)
    showToast({ type: 'success', message: '开工成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') showToast({ type: 'fail', message: '操作失败' })
  }
}

const onComplete = async (item) => {
  try {
    await showConfirmDialog({ title: '确认', message: '确定完工吗？' })
    await completeWorkOrder(item.id)
    showToast({ type: 'success', message: '完工成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') showToast({ type: 'fail', message: '操作失败' })
  }
}

const onCancel = async (item) => {
  try {
    await showConfirmDialog({ title: '确认', message: '确定取消该工单吗？' })
    await cancelWorkOrder(item.id)
    showToast({ type: 'success', message: '取消成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') showToast({ type: 'fail', message: '操作失败' })
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
.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #f5f5f5;
  flex-wrap: wrap;
}
</style>
