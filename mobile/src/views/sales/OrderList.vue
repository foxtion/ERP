<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    show-search
    search-placeholder="搜索订单编号/客户名称"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('sales:order:add')"
    @add="onAdd"
  >
    <template #filters="{ query: slotQuery }">
      <van-dropdown-menu>
        <van-dropdown-item
          v-model="query.status"
          :options="statusOptions"
          @change="onStatusChange"
        />
      </van-dropdown-menu>
    </template>

    <template #list="{ list }">
      <div
        v-for="item in list"
        :key="item.id"
        class="card"
        @click="goDetail(item)"
      >
        <div class="card-header">
          <span class="title">{{ item.order_no }}</span>
          <StatusTag
            :status="item.status"
            :options="statusTextMap"
            :type-map="statusTypeMap"
          />
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">客户：</span>
            <span class="value">{{ item.customer_name }}</span>
          </div>
          <div class="info-row">
            <span class="label">订单日期：</span>
            <span class="value">{{ item.order_date }}</span>
          </div>
          <div class="info-row">
            <span class="label">总金额：</span>
            <span class="value amount">¥{{ item.total_amount }}</span>
          </div>
        </div>
        <div class="card-footer">
          <template v-if="item.status === 'draft'">
            <van-button
              v-if="userStore.hasPermission('sales:order:edit')"
              size="small"
              type="primary"
              plain
              @click.stop="onEdit(item)"
            >
              编辑
            </van-button>
            <van-button
              v-if="userStore.hasPermission('sales:order:confirm')"
              size="small"
              type="success"
              plain
              @click.stop="onConfirm(item)"
            >
              确认
            </van-button>
          </template>
          <template v-if="['draft', 'confirmed', 'partial'].includes(item.status)">
            <van-button
              v-if="userStore.hasPermission('sales:order:cancel')"
              size="small"
              type="warning"
              plain
              @click.stop="onCancel(item)"
            >
              取消
            </van-button>
          </template>
          <van-button
            v-if="['confirmed', 'partial'].includes(item.status) && userStore.hasPermission('sales:order:create_picking')"
            size="small"
            type="info"
            plain
            @click.stop="onCreatePicking(item)"
          >
            生成拣货单
          </van-button>
          <van-button
            v-if="userStore.hasPermission('sales:order:delete') && item.status === 'draft'"
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
import { showConfirmDialog, showToast, showFailToast } from 'vant'
import { useUserStore } from '@/store/user'
import {
  getSalesOrderList,
  deleteSalesOrder,
  confirmOrder,
  cancelOrder,
  createPickingFromOrder,
} from '@/api/sales'
import ListPage from '@/components/ListPage.vue'
import StatusTag from '@/components/StatusTag.vue'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref(null)

const query = ref({ search: '', status: '' })
const fetchApi = getSalesOrderList

const statusTextMap = {
  draft: '草稿',
  confirmed: '已确认',
  partial: '部分出库',
  completed: '已完成',
  cancelled: '已取消',
}

const statusTypeMap = {
  draft: 'default',
  confirmed: 'primary',
  partial: 'warning',
  completed: 'success',
  cancelled: 'danger',
}

const statusOptions = [
  { text: '全部状态', value: '' },
  { text: '草稿', value: 'draft' },
  { text: '已确认', value: 'confirmed' },
  { text: '部分出库', value: 'partial' },
  { text: '已完成', value: 'completed' },
  { text: '已取消', value: 'cancelled' },
]

const onStatusChange = () => {
  // query变化会自动触发ListPage重新加载
}

const onAdd = () => {
  router.push('/sales/order-form')
}

const goDetail = (item) => {
  router.push(`/sales/order-detail/${item.id}`)
}

const onEdit = (item) => {
  router.push(`/sales/order-form?id=${item.id}`)
}

const onConfirm = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认订单',
      message: `确定确认订单「${item.order_no}」吗？`,
    })
    await confirmOrder(item.id)
    showToast('确认成功')
    listPageRef.value?.onRefresh()
  } catch (e) {
    // 取消或失败
  }
}

const onCancel = async (item) => {
  try {
    await showConfirmDialog({
      title: '取消订单',
      message: `确定取消订单「${item.order_no}」吗？`,
    })
    await cancelOrder(item.id)
    showToast('取消成功')
    listPageRef.value?.onRefresh()
  } catch (e) {
    // 取消或失败
  }
}

const onCreatePicking = async (item) => {
  try {
    await showConfirmDialog({
      title: '生成拣货单',
      message: `确定为订单「${item.order_no}」生成拣货单吗？`,
    })
    await createPickingFromOrder(item.id)
    showToast('生成成功')
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e?.response?.status === 400) {
      const msg = e.response.data?.message || '生成拣货单失败，请检查订单状态或是否已有未完成拣货单'
      showFailToast(msg)
      // eslint-disable-next-line no-alert
      alert(msg)
    }
    console.error('生成拣货单失败:', e)
  }
}

const onDelete = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定删除订单「${item.order_no}」吗？`,
    })
    await deleteSalesOrder(item.id)
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
  flex-wrap: wrap;
}
</style>
