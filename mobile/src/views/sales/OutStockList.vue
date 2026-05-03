<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    show-search
    search-placeholder="搜索出库单号/关联订单"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('sales:outstock:add')"
    @add="onAdd"
  >
    <template #filters="{ query: slotQuery }">
      <van-dropdown-menu>
        <van-dropdown-item
          v-model="query.warehouse_id"
          :options="warehouseOptions"
          @change="onFilterChange"
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
          <span class="title">{{ item.stock_no }}</span>
          <van-tag type="success" size="medium">已出库</van-tag>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">关联订单：</span>
            <span class="value">{{ item.order_no || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">出库日期：</span>
            <span class="value">{{ item.stock_date }}</span>
          </div>
          <div class="info-row">
            <span class="label">仓库：</span>
            <span class="value">{{ item.warehouse || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">出库数量：</span>
            <span class="value">{{ item.items?.reduce((sum, i) => sum + (Number(i.quantity) || 0), 0) || 0 }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="userStore.hasPermission('sales:outstock:edit')"
            size="small"
            type="primary"
            plain
            @click.stop="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('sales:outstock:delete')"
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
import { getOutStockList, deleteOutStock } from '@/api/sales'
import ListPage from '@/components/ListPage.vue'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref(null)

const query = ref({ search: '', warehouse_id: '' })
const fetchApi = getOutStockList

const warehouseOptions = ref([
  { text: '全部仓库', value: '' },
])

const onFilterChange = () => {
  // query变化会自动触发ListPage重新加载
}

const onAdd = () => {
  router.push('/sales/outstock-form')
}

const goDetail = (item) => {
  router.push(`/sales/outstock-detail/${item.id}`)
}

const onEdit = (item) => {
  router.push(`/sales/outstock-form?id=${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定删除出库单「${item.stock_no}」吗？`,
    })
    await deleteOutStock(item.id)
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
.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
