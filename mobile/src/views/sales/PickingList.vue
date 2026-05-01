<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    show-search
    search-placeholder="搜索拣货单号/关联订单"
    :show-add="false"
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
          <span class="title">{{ item.picking_no }}</span>
          <StatusTag
            :status="item.status"
            :options="statusTextMap"
            :type-map="statusTypeMap"
          />
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">关联订单：</span>
            <span class="value">{{ item.order_no || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">指派员工：</span>
            <span class="value">{{ item.assignee_name || '未指派' }}</span>
          </div>
          <div class="info-row">
            <span class="label">创建时间：</span>
            <span class="value">{{ item.created_at }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="item.status === 'pending' && userStore.hasPermission('sales:picking:assign')"
            size="small"
            type="primary"
            plain
            @click.stop="onAssign(item)"
          >
            指派
          </van-button>
          <van-button
            v-if="item.status === 'assigned' && userStore.hasPermission('sales:picking:accept')"
            size="small"
            type="success"
            plain
            @click.stop="onAccept(item)"
          >
            接单
          </van-button>
          <van-button
            v-if="['accepted', 'picking', 'shortage'].includes(item.status) && userStore.hasPermission('sales:picking:operate')"
            size="small"
            type="info"
            plain
            @click.stop="onGoJob(item)"
          >
            去作业
          </van-button>
        </div>
      </div>
    </template>
  </ListPage>

  <!-- 指派弹窗 -->
  <van-dialog
    v-model:show="assignDialogVisible"
    title="指派拣货员"
    show-cancel-button
    @confirm="confirmAssign"
  >
    <van-field
      v-model="assigneeName"
      label="拣货员"
      placeholder="请输入员工姓名或ID"
      :rules="[{ required: true, message: '请填写拣货员' }]"
    />
  </van-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import { useUserStore } from '@/store/user'
import {
  getPickingList,
  assignPicking,
  acceptPicking,
} from '@/api/sales'
import ListPage from '@/components/ListPage.vue'
import StatusTag from '@/components/StatusTag.vue'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref(null)

const query = ref({ search: '', status: '' })
const fetchApi = getPickingList

const statusTextMap = {
  pending: '待指派',
  assigned: '已指派',
  accepted: '已接单',
  picking: '拿货中',
  complete: '齐发待出库',
  shortage: '欠发待出库',
  done: '已完成',
  cancelled: '已取消',
}

const statusTypeMap = {
  pending: 'default',
  assigned: 'primary',
  accepted: 'success',
  picking: 'warning',
  complete: 'success',
  shortage: 'warning',
  done: 'success',
  cancelled: 'danger',
}

const statusOptions = [
  { text: '全部状态', value: '' },
  { text: '待指派', value: 'pending' },
  { text: '已指派', value: 'assigned' },
  { text: '已接单', value: 'accepted' },
  { text: '拿货中', value: 'picking' },
  { text: '齐发待出库', value: 'complete' },
  { text: '欠发待出库', value: 'shortage' },
  { text: '已完成', value: 'done' },
  { text: '已取消', value: 'cancelled' },
]

const onStatusChange = () => {
  // query变化会自动触发ListPage重新加载
}

const goDetail = (item) => {
  router.push(`/sales/picking-detail/${item.id}`)
}

const assignDialogVisible = ref(false)
const currentItem = ref(null)
const assigneeName = ref('')

const onAssign = (item) => {
  currentItem.value = item
  assigneeName.value = ''
  assignDialogVisible.value = true
}

const confirmAssign = async () => {
  if (!assigneeName.value.trim()) {
    showToast('请填写拣货员')
    return
  }
  try {
    await assignPicking(currentItem.value.id, assigneeName.value.trim())
    showToast('指派成功')
    listPageRef.value?.onRefresh()
  } catch (e) {
    // 失败已由request拦截器处理
  }
}

const onAccept = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认接单',
      message: `确定接单「${item.picking_no}」吗？`,
    })
    await acceptPicking(item.id)
    showToast('接单成功')
    listPageRef.value?.onRefresh()
  } catch (e) {
    // 取消或失败
  }
}

const onGoJob = (item) => {
  router.push(`/sales/picking-job/${item.id}`)
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
