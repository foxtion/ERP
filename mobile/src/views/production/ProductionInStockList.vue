<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    search-placeholder="搜索入库单号/产品"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('production:instock:add')"
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
          <span class="title">{{ item.instock_no }}</span>
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
            <span class="label">入库数量</span>
            <span class="value">{{ item.quantity }}</span>
          </div>
          <div class="info-row">
            <span class="label">入库日期</span>
            <span class="value">{{ item.instock_date }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="item.status === 'draft' && userStore.hasPermission('production:instock:submit')"
            size="small"
            type="primary"
            plain
            @click.stop="onSubmit(item)"
          >
            提交
          </van-button>
          <van-button
            v-if="item.status === 'submitted' && userStore.hasPermission('production:instock:approve')"
            size="small"
            type="primary"
            plain
            @click.stop="onApprove(item)"
          >
            审核
          </van-button>
          <van-button
            v-if="item.status === 'approved' && userStore.hasPermission('production:instock:confirm')"
            size="small"
            type="success"
            plain
            @click.stop="onConfirm(item)"
          >
            确认入库
          </van-button>
          <van-button
            v-if="['draft', 'submitted'].includes(item.status) && userStore.hasPermission('production:instock:cancel')"
            size="small"
            type="warning"
            plain
            @click.stop="onCancel(item)"
          >
            取消
          </van-button>
          <van-button
            v-if="item.status === 'draft' && userStore.hasPermission('production:instock:edit')"
            size="small"
            type="primary"
            plain
            @click.stop="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="item.status === 'draft' && userStore.hasPermission('production:instock:delete')"
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
  getProductionInStockList,
  submitProductionInStock,
  approveProductionInStock,
  confirmProductionInStock,
  cancelProductionInStock,
  deleteProductionInStock,
} from '@/api/production'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref(null)

const query = ref({ search: '' })

const statusMap = {
  draft: '草稿',
  submitted: '已提交',
  approved: '已审核',
  confirmed: '已入库',
  cancelled: '已取消',
}

const statusTypeMap = {
  draft: 'default',
  submitted: 'primary',
  approved: 'warning',
  confirmed: 'success',
  cancelled: 'danger',
}

const fetchApi = (params) => getProductionInStockList(params)

const onAdd = () => {
  router.push('/production/instock/add')
}

const onDetail = (item) => {
  router.push(`/production/instock/detail/${item.id}`)
}

const onEdit = (item) => {
  router.push(`/production/instock/edit/${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定删除入库单 "${item.instock_no}" 吗？`,
    })
    await deleteProductionInStock(item.id)
    showToast({ type: 'success', message: '删除成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') {
      showToast({ type: 'fail', message: '删除失败' })
    }
  }
}

const onSubmit = async (item) => {
  try {
    await showConfirmDialog({ title: '确认', message: '确定提交该入库单吗？' })
    await submitProductionInStock(item.id)
    showToast({ type: 'success', message: '提交成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') showToast({ type: 'fail', message: '操作失败' })
  }
}

const onApprove = async (item) => {
  try {
    await showConfirmDialog({ title: '确认', message: '确定审核通过吗？' })
    await approveProductionInStock(item.id)
    showToast({ type: 'success', message: '审核成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') showToast({ type: 'fail', message: '操作失败' })
  }
}

const onConfirm = async (item) => {
  try {
    await showConfirmDialog({ title: '确认', message: '确定确认入库吗？' })
    await confirmProductionInStock(item.id)
    showToast({ type: 'success', message: '入库成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') showToast({ type: 'fail', message: '操作失败' })
  }
}

const onCancel = async (item) => {
  try {
    await showConfirmDialog({ title: '确认', message: '确定取消该入库单吗？' })
    await cancelProductionInStock(item.id)
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
