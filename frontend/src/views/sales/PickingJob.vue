<template>
  <div class="page-container" v-loading="loading">
    <el-card v-if="picking">
      <!-- 头部信息 -->
      <div class="header-info">
        <div class="header-left">
          <h2 class="picking-title">拣货单：{{ picking.picking_no }}</h2>
          <div class="meta">
            <el-tag :type="statusType(picking.status)">{{ statusText(picking.status) }}</el-tag>
            <span>订单：{{ picking.order_no }}</span>
            <span>客户：{{ picking.customer_name }}</span>
            <span>仓库：{{ picking.warehouse }}</span>
          </div>
        </div>
        <div class="header-right">
          <el-button v-if="picking.status === 'assigned'" type="primary" @click="handleAccept">接单</el-button>
        </div>
      </div>

      <!-- 拣货明细表格 -->
      <el-table :data="picking.items" border class="picking-table">
        <el-table-column type="index" label="序号" width="55" align="center" />
        <el-table-column prop="location_code" label="库位号" width="95" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="warning">{{ row.location_code || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="material_code" label="商品代码" width="110" />
        <el-table-column prop="material_name" label="商品名称" min-width="160" />
        <el-table-column prop="spec" label="规格" width="90" />
        <el-table-column label="需拿数量" width="90" align="center">
          <template #default="{ row }">
            <span class="qty-need">{{ fmt(row.quantity) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="已拿数量" width="90" align="center">
          <template #default="{ row }">
            <span :class="pickedClass(row)">{{ fmt(row.picked_qty) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'picked' ? 'success' : row.status === 'shortage' ? 'danger' : 'info'">
              {{ {pending:'待拿', picked:'已拿', shortage:'缺货'}[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-row">
              <el-button
                v-if="!['pending','assigned','done','cancelled'].includes(picking.status)"
                size="small"
                type="success"
                :disabled="row.status === 'picked'"
                @click="openPickDialog(row, 'pick')"
              >已拿</el-button>
              <el-button
                v-if="!['pending','assigned','done','cancelled'].includes(picking.status)"
                size="small"
                type="danger"
                :disabled="row.status !== 'pending'"
                @click="openPickDialog(row, 'shortage')"
              >缺货</el-button>
              <el-button
                v-if="!['pending','assigned','done','cancelled'].includes(picking.status)"
                size="small"
                type="warning"
                @click="handleReport(row)"
              >报告缺货</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 底部操作 -->
      <div class="footer-actions">
        <div class="summary">
          <span>总商品数：{{ picking.items?.length || 0 }}</span>
          <span>已拿：{{ pickedCount }}</span>
          <span>缺货：{{ shortageCount }}</span>
        </div>
        <div class="buttons" v-if="['picking','complete','shortage'].includes(picking.status)">
          <el-button type="success" size="large" :disabled="!canComplete" @click="handleSubmit('complete')">
            齐发提交
          </el-button>
          <el-button type="warning" size="large" :disabled="!canShortage" @click="handleSubmit('shortage')">
            欠发提交
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 录入数量弹窗 -->
    <el-dialog v-model="pickVisible" :title="pickDialogTitle" width="420px" @close="resetPickForm">
      <el-form label-width="100px" :model="pickForm">
        <el-form-item label="商品">
          <el-input v-model="pickForm.material_name" disabled />
        </el-form-item>
        <el-form-item label="需拿数量">
          <el-input v-model="pickForm.need_qty" disabled />
        </el-form-item>
        <el-form-item label="实际拿到">
          <el-input-number v-model="pickForm.picked_qty" :min="0" :max="pickForm.need_qty" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item label="实际缺货">
          <el-input-number v-model="pickForm.shortage_qty" :min="0" :max="pickForm.need_qty" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item>
          <el-alert v-if="pickForm.picked_qty + pickForm.shortage_qty > pickForm.need_qty" type="error" :closable="false" show-icon>
            <template #title>实际拿到 + 缺货不能超过需拿数量 {{ pickForm.need_qty }}</template>
          </el-alert>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pickVisible = false">取消</el-button>
        <el-button type="primary" :disabled="pickForm.picked_qty + pickForm.shortage_qty > pickForm.need_qty" :loading="pickLoading" @click="confirmPick">确定</el-button>
      </template>
    </el-dialog>

    <!-- 报告缺货弹窗 -->
    <el-dialog v-model="reportVisible" title="报告缺货" width="400px">
      <el-form label-width="80px">
        <el-form-item label="商品">
          <el-input v-model="reportForm.material_name" disabled />
        </el-form-item>
        <el-form-item label="库位号">
          <el-input v-model="reportForm.location_code" disabled />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="reportForm.remark" type="textarea" rows="3" placeholder="请描述缺货情况，如：货架为空、数量不足等" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reportVisible = false">取消</el-button>
        <el-button type="primary" :loading="reportLoading" @click="confirmReport">确定上报</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getPickingDetail, acceptPicking, pickItem,
  reportShortage, submitPicking
} from '@/api/sales'

const route = useRoute()
const router = useRouter()
const pickingId = computed(() => route.params.id)

const loading = ref(false)
const picking = ref(null)

// 录入数量弹窗
const pickVisible = ref(false)
const pickLoading = ref(false)
const pickDialogTitle = ref('录入数量')
const pickForm = ref({
  item_id: null,
  material_name: '',
  need_qty: 0,
  picked_qty: 0,
  shortage_qty: 0,
})

// 报告缺货弹窗
const reportVisible = ref(false)
const reportLoading = ref(false)
const reportForm = ref({ item_id: null, material_name: '', location_code: '', remark: '' })

const statusText = (s) => ({
  pending: '待指派', assigned: '已指派', accepted: '已接单',
  picking: '拿货中', complete: '齐发待出库', shortage: '欠发待出库',
  done: '已完成', cancelled: '已取消'
}[s] || s)

const statusType = (s) => ({
  pending: 'info', assigned: 'primary', accepted: 'warning',
  picking: 'warning', complete: 'success', shortage: 'danger',
  done: 'success', cancelled: 'info'
}[s] || '')

// 格式化数量为纯整数（去掉小数）
const fmt = (val) => {
  if (val === null || val === undefined) return '0'
  const num = Math.floor(Number(val))
  return String(num)
}

const pickedClass = (row) => {
  const picked = Number(row.picked_qty || 0)
  const need = Number(row.quantity || 0)
  return picked >= need ? 'text-success' : ''
}

const pickedCount = computed(() => picking.value?.items?.filter(i => i.status === 'picked').length || 0)
const shortageCount = computed(() => picking.value?.items?.filter(i => i.status === 'shortage').length || 0)

const canComplete = computed(() => {
  if (!picking.value?.items?.length) return false
  return picking.value.items.every(i => (i.picked_qty || 0) >= (i.quantity || 0))
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
    const res = await getPickingDetail(pickingId.value)
    picking.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (!pickingId.value || !/^\d+$/.test(String(pickingId.value))) {
    ElMessage.warning('请选择要作业的拣货单')
    router.push('/inventory/picking-list')
    return
  }
  fetchDetail()
})

const handleAccept = async () => {
  try {
    await acceptPicking(pickingId.value)
    ElMessage.success('接单成功')
    await fetchDetail()
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || e?.message || '接单失败')
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

const resetPickForm = () => {
  pickForm.value = { item_id: null, material_name: '', need_qty: 0, picked_qty: 0, shortage_qty: 0 }
}

const confirmPick = async () => {
  if (pickForm.value.picked_qty + pickForm.value.shortage_qty > pickForm.value.need_qty) {
    ElMessage.warning('实际拿到 + 缺货不能超过需拿数量')
    return
  }
  pickLoading.value = true
  try {
    await pickItem(pickingId.value, pickForm.value.item_id, pickForm.value.picked_qty, pickForm.value.shortage_qty)
    ElMessage.success('记录成功')
    pickVisible.value = false
    await fetchDetail()
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || e?.message || '操作失败')
  } finally {
    pickLoading.value = false
  }
}

const handleReport = (row) => {
  reportForm.value = {
    item_id: row.id,
    material_name: row.material_name,
    location_code: row.location_code || '',
    remark: ''
  }
  reportVisible.value = true
}

const confirmReport = async () => {
  reportLoading.value = true
  try {
    await reportShortage(pickingId.value, reportForm.value.item_id, reportForm.value.remark)
    ElMessage.success('缺货上报成功')
    reportVisible.value = false
    await fetchDetail()
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || e?.message || '上报失败')
  } finally {
    reportLoading.value = false
  }
}

const handleSubmit = async (type) => {
  const msg = type === 'complete'
    ? '确定齐发提交吗？系统将生成出库单并扣减库存。'
    : '确定欠发提交吗？系统将出库已拿商品，缺货部分将自动拆单。'
  try {
    await ElMessageBox.confirm(msg, '提示', { type: 'warning' })
    await submitPicking(pickingId.value)
    ElMessage.success('提交成功')
    await fetchDetail()
  } catch (e) {
    if (e !== 'cancel' && e?.action !== 'cancel') {
      ElMessage.error(e?.response?.data?.message || e?.message || '提交失败')
    }
  }
}
</script>

<style scoped>
.page-container { padding: 20px; }
.header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}
.picking-title { margin: 0 0 8px; font-size: 20px; }
.meta { display: flex; gap: 15px; align-items: center; color: #666; font-size: 14px; }
.picking-table { margin-bottom: 20px; }

/* 数量展示 */
.qty-need {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

/* 操作按钮一排显示 */
.action-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #eee;
}
.summary { display: flex; gap: 20px; font-size: 14px; color: #666; }
.buttons { display: flex; gap: 15px; }
.text-success { color: #67c23a; font-weight: bold; }
.text-danger { color: #f56c6c; font-weight: bold; }
</style>
