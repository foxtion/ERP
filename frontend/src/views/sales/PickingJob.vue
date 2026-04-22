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
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="location_code" label="库位号" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="warning">{{ row.location_code || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="material_code" label="商品代码" width="120" />
        <el-table-column prop="material_name" label="商品名称" min-width="180" />
        <el-table-column prop="spec" label="规格" width="100" />
        <el-table-column prop="quantity" label="需拿数量" width="90" align="right" />
        <el-table-column prop="picked_qty" label="已拿数量" width="90" align="right">
          <template #default="{ row }">
            <span :class="{ 'text-success': row.picked_qty >= row.quantity }">{{ row.picked_qty }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="shortage_qty" label="缺货数量" width="90" align="right">
          <template #default="{ row }">
            <span v-if="row.shortage_qty > 0" class="text-danger">{{ row.shortage_qty }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'picked' ? 'success' : row.status === 'shortage' ? 'danger' : 'info'">
              {{ {pending:'待拿', picked:'已拿', shortage:'缺货'}[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="['picking','accepted'].includes(picking.status)"
              size="small"
              type="success"
              :disabled="row.status === 'picked'"
              @click="handlePick(row, row.quantity)"
            >已拿</el-button>
            <el-button
              v-if="['picking','accepted'].includes(picking.status)"
              size="small"
              type="danger"
              :disabled="row.status === 'shortage'"
              @click="handlePick(row, 0, row.quantity)"
            >缺货</el-button>
            <el-button
              v-if="['picking','accepted'].includes(picking.status)"
              size="small"
              type="warning"
              @click="handleReport(row)"
            >报告缺货</el-button>
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
  fetchDetail()
})

const handleAccept = async () => {
  try {
    await acceptPicking(pickingId.value)
    ElMessage.success('接单成功')
    await fetchDetail()
  } catch (e) {
    // ignore
  }
}

const handlePick = async (row, picked, shortage = 0) => {
  try {
    await pickItem(pickingId.value, row.id, picked, shortage)
    ElMessage.success('记录成功')
    await fetchDetail()
  } catch (e) {
    // ignore
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
    // ignore
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
