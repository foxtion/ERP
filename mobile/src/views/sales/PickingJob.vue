<template>
  <div class="detail-page">
    <div v-if="picking" class="picking-wrap">
      <!-- 头部信息 -->
      <div class="info-card">
        <div class="picking-header">
          <div class="picking-no">{{ picking.picking_no }}</div>
          <van-tag :type="statusType(picking.status)">{{ statusText(picking.status) }}</van-tag>
        </div>
        <div class="meta-info">
          <div class="meta-item">
            <span class="label">订单：</span>
            <span class="value">{{ picking.order_no }}</span>
          </div>
          <div class="meta-item">
            <span class="label">客户：</span>
            <span class="value">{{ picking.customer_name }}</span>
          </div>
          <div class="meta-item">
            <span class="label">仓库：</span>
            <span class="value">{{ picking.warehouse }}</span>
          </div>
          <div class="meta-item" v-if="picking.assigned_to_name">
            <span class="label">指派员工：</span>
            <span class="value">{{ picking.assigned_to_name }}</span>
          </div>
        </div>
        <div class="header-actions" v-if="picking.status === 'assigned'">
          <van-button type="primary" block round @click="handleAccept">接单</van-button>
        </div>
      </div>

      <!-- 拣货明细列表 -->
      <div class="section-title">拣货明细（{{ picking.items?.length || 0 }}）</div>
      <div class="item-list">
        <div
          v-for="item in picking.items"
          :key="item.id"
          class="item-card"
        >
          <div class="item-header">
            <div class="item-name">{{ item.material_name }}</div>
            <van-tag size="small" :type="itemStatusType(item.status)">
              {{ itemStatusText(item.status) }}
            </van-tag>
          </div>
          <div class="item-body">
            <div class="item-info">
              <span class="label">编码：</span>
              <span>{{ item.material_code || '-' }}</span>
            </div>
            <div class="item-info">
              <span class="label">规格：</span>
              <span>{{ item.spec || '-' }}</span>
            </div>
            <div class="item-info">
              <span class="label">库位：</span>
              <van-tag size="small" type="warning">{{ item.location_code || '-' }}</van-tag>
            </div>
            <div class="qty-row">
              <div class="qty-item">
                <div class="qty-label">需拿</div>
                <div class="qty-value need">{{ fmt(item.quantity) }}</div>
              </div>
              <div class="qty-item">
                <div class="qty-label">已拿</div>
                <div class="qty-value picked">{{ fmt(item.picked_qty) }}</div>
              </div>
              <div class="qty-item">
                <div class="qty-label">缺货</div>
                <div class="qty-value shortage">{{ fmt(item.shortage_qty) }}</div>
              </div>
            </div>
          </div>
          <!-- 操作按钮 -->
          <div class="item-actions" v-if="!['pending','assigned','done','cancelled'].includes(picking.status)">
            <van-button
              size="small"
              type="success"
              :disabled="item.status === 'picked' || item.status === 'refunded'"
              @click="openPickDialog(item, 'pick')"
            >
              已拿
            </van-button>
            <van-button
              size="small"
              type="danger"
              :disabled="item.status !== 'pending'"
              @click="openPickDialog(item, 'shortage')"
            >
              缺货
            </van-button>
            <van-button
              size="small"
              type="warning"
              @click="handleReport(item)"
            >
              报告缺货
            </van-button>
            <van-button
              size="small"
              type="info"
              :disabled="item.status === 'refunded'"
              @click="handleRefund(item)"
            >
              已退款
            </van-button>
          </div>
        </div>
      </div>

      <!-- 底部提交按钮 -->
      <div class="footer-actions" v-if="['picking','complete','shortage'].includes(picking.status)">
        <van-button
          type="success"
          block
          round
          :disabled="!canComplete"
          @click="handleSubmit('complete')"
        >
          齐发提交
        </van-button>
        <van-button
          type="warning"
          block
          round
          :disabled="!canShortage"
          @click="handleSubmit('shortage')"
          style="margin-top: 8px;"
        >
          欠发提交
        </van-button>
      </div>
    </div>

    <!-- 录入数量弹窗 -->
    <van-dialog
      v-model:show="pickVisible"
      :title="pickDialogTitle"
      show-cancel-button
      @confirm="confirmPick"
    >
      <div class="pick-form">
        <div class="pick-item-info">
          <div class="pick-item-name">{{ pickForm.material_name }}</div>
          <div class="pick-item-need">需拿数量：{{ pickForm.need_qty }}</div>
        </div>
        <van-field
          v-model.number="pickForm.picked_qty"
          type="digit"
          label="实际拿到"
          placeholder="请输入数量"
        />
        <van-field
          v-model.number="pickForm.shortage_qty"
          type="digit"
          label="实际缺货"
          placeholder="请输入数量"
        />
        <van-cell v-if="pickForm.picked_qty + pickForm.shortage_qty > pickForm.need_qty" title-class="text-danger">
          <template #title>
            <span class="text-danger">实际拿到+缺货不能超过需拿数量</span>
          </template>
        </van-cell>
      </div>
    </van-dialog>

    <!-- 报告缺货弹窗 -->
    <van-dialog
      v-model:show="reportVisible"
      title="报告缺货"
      show-cancel-button
      @confirm="confirmReport"
    >
      <van-field
        v-model="reportForm.remark"
        type="textarea"
        rows="3"
        label="备注"
        placeholder="请描述缺货情况"
      />
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast, showConfirmDialog } from 'vant'
import { getPickingDetail, acceptPicking, pickItem, reportShortage, submitPicking, refundItem } from '@/api/sales'

const route = useRoute()
const router = useRouter()
const pickingId = route.params.id

const picking = ref(null)
const loading = ref(false)

// 录入弹窗
const pickVisible = ref(false)
const pickDialogTitle = ref('录入数量')
const pickForm = ref({ item_id: null, material_name: '', need_qty: 0, picked_qty: 0, shortage_qty: 0 })

// 报告缺货弹窗
const reportVisible = ref(false)
const reportForm = ref({ item_id: null, remark: '' })

const statusText = (s) => ({
  pending: '待指派', assigned: '已指派', accepted: '已接单',
  picking: '拿货中', complete: '齐发待出库', shortage: '欠发待出库',
  done: '已完成', cancelled: '已取消'
}[s] || s)

const statusType = (s) => ({
  pending: 'default', assigned: 'primary', accepted: 'warning',
  picking: 'warning', complete: 'success', shortage: 'danger',
  done: 'success', cancelled: 'default'
}[s] || 'default')

const itemStatusText = (s) => ({ pending: '待拿', picked: '已拿', shortage: '缺货', refunded: '已退款' }[s] || s)
const itemStatusType = (s) => ({ pending: 'default', picked: 'success', shortage: 'danger', refunded: 'default' }[s] || 'default')

const fmt = (val) => {
  if (val === null || val === undefined) return '0'
  return String(Math.floor(Number(val)))
}

const canComplete = computed(() => {
  if (!picking.value?.items?.length) return false
  return picking.value.items.every(i => {
    if (i.status === 'refunded') return true
    return (i.picked_qty || 0) >= (i.quantity || 0)
  })
})

const canShortage = computed(() => {
  if (!picking.value?.items?.length) return false
  const hasPicked = picking.value.items.some(i => (i.picked_qty || 0) > 0)
  const hasShortage = picking.value.items.some(i => (i.shortage_qty || 0) > 0)
  return hasPicked && hasShortage
})

const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await getPickingDetail(pickingId)
    picking.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (!pickingId) {
    showFailToast('请选择要作业的拣货单')
    router.back()
    return
  }
  fetchDetail()
})

const handleAccept = async () => {
  try {
    await acceptPicking(pickingId)
    showToast('接单成功')
    await fetchDetail()
  } catch (e) {
    showFailToast(e?.response?.data?.message || '接单失败')
  }
}

const openPickDialog = (row, type) => {
  const need = Math.floor(Number(row.quantity || 0))
  const alreadyPicked = Math.floor(Number(row.picked_qty || 0))
  const alreadyShortage = Math.floor(Number(row.shortage_qty || 0))
  pickDialogTitle.value = type === 'pick' ? '录入拿货数量' : '录入缺货数量'
  pickForm.value = {
    item_id: row.id,
    material_name: row.material_name,
    need_qty: need,
    picked_qty: type === 'pick' ? need - alreadyPicked - alreadyShortage : 0,
    shortage_qty: type === 'shortage' ? need - alreadyPicked - alreadyShortage : 0,
  }
  pickVisible.value = true
}

const confirmPick = async () => {
  if (pickForm.value.picked_qty + pickForm.value.shortage_qty > pickForm.value.need_qty) {
    showFailToast('实际拿到+缺货不能超过需拿数量')
    return
  }
  try {
    await pickItem(pickingId, pickForm.value.item_id, pickForm.value.picked_qty, pickForm.value.shortage_qty)
    showToast('记录成功')
    pickVisible.value = false
    await fetchDetail()
  } catch (e) {
    showFailToast(e?.response?.data?.message || '操作失败')
  }
}

const handleReport = (row) => {
  reportForm.value = { item_id: row.id, remark: '' }
  reportVisible.value = true
}

const confirmReport = async () => {
  try {
    await reportShortage(pickingId, reportForm.value.item_id, reportForm.value.remark)
    showToast('缺货上报成功')
    reportVisible.value = false
    await fetchDetail()
  } catch (e) {
    showFailToast(e?.response?.data?.message || '上报失败')
  }
}

const handleRefund = async (row) => {
  try {
    await showConfirmDialog({
      title: '确认退款',
      message: `确定将「${row.material_name}」标记为已退款吗？`,
    })
    await refundItem(pickingId, row.id)
    showToast('标记退款成功')
    await fetchDetail()
  } catch (e) {
    if (e !== 'cancel' && e?.action !== 'cancel') {
      showFailToast(e?.response?.data?.message || '操作失败')
    }
  }
}

const handleSubmit = async (type) => {
  const msg = type === 'complete'
    ? '确定齐发提交吗？系统将生成出库单并扣减库存。'
    : '确定欠发提交吗？系统将出库已拿商品，缺货部分将自动拆单。'
  try {
    await showConfirmDialog({ title: '提示', message: msg })
    await submitPicking(pickingId)
    showToast('提交成功')
    await fetchDetail()
  } catch (e) {
    if (e !== 'cancel' && e?.action !== 'cancel') {
      showFailToast(e?.response?.data?.message || '提交失败')
    }
  }
}
</script>

<style scoped>
.picking-wrap {
  padding-bottom: 20px;
}
.info-card {
  margin: 10px 12px;
  background-color: #fff;
  border-radius: 8px;
  padding: 12px;
}
.picking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.picking-no {
  font-size: 16px;
  font-weight: bold;
  color: #323233;
}
.meta-info {
  font-size: 13px;
}
.meta-item {
  display: flex;
  padding: 4px 0;
}
.meta-item .label {
  color: #969799;
  width: 70px;
}
.header-actions {
  margin-top: 12px;
}
.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #666;
  padding: 12px 12px 8px;
}
.item-list {
  padding: 0 12px;
}
.item-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
}
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.item-name {
  font-size: 15px;
  font-weight: bold;
  color: #323233;
}
.item-body {
  font-size: 13px;
}
.item-info {
  display: flex;
  padding: 3px 0;
}
.item-info .label {
  color: #969799;
  width: 50px;
}
.qty-row {
  display: flex;
  justify-content: space-around;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}
.qty-item {
  text-align: center;
}
.qty-label {
  font-size: 12px;
  color: #969799;
}
.qty-value {
  font-size: 18px;
  font-weight: bold;
  margin-top: 4px;
}
.qty-value.need { color: #323233; }
.qty-value.picked { color: #07c160; }
.qty-value.shortage { color: #ee0a24; }
.item-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
  flex-wrap: wrap;
}
.footer-actions {
  margin: 20px 12px;
}
.pick-form {
  padding: 12px;
}
.pick-item-info {
  text-align: center;
  margin-bottom: 12px;
}
.pick-item-name {
  font-size: 15px;
  font-weight: bold;
}
.pick-item-need {
  font-size: 13px;
  color: #969799;
  margin-top: 4px;
}
.text-danger {
  color: #ee0a24;
}
</style>
