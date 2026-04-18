<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <h3 class="page-title">出库作业</h3>
        <el-button type="primary" @click="fetchData">刷新</el-button>
      </div>

      <div v-if="orderList.length === 0" class="empty-text">
        暂无待出库订单
      </div>

      <div v-for="order in orderList" :key="order.id" class="order-card">
        <el-card shadow="hover">
          <div class="order-header">
            <div class="order-header-left">
              <span class="order-no">{{ order.order_no }}</span>
              <el-tag :type="statusType(order.status)" size="small" class="status-tag">{{ order.status_display }}</el-tag>
              <el-tag
                v-if="order.allow_partial_shipment"
                type="success"
                size="small"
                class="status-tag"
                title="该客户允许部分出货，未出库物料将自动生成新订单"
              >
                允许部分出货
              </el-tag>
              <el-tag
                v-else
                type="danger"
                size="small"
                class="status-tag"
                title="该客户要求全部物料备齐才能出单"
              >
                需整单出库
              </el-tag>
            </div>
            <div class="order-info">
              <span>客户：{{ order.customer_name }}</span>
              <span>下单日期：{{ order.order_date }}</span>
            </div>
          </div>

          <el-table :data="order.items" border size="small" class="item-table">
            <el-table-column prop="material_code" label="物料编码" min-width="120" />
            <el-table-column prop="material_name" label="物料名称" min-width="160" />
            <el-table-column prop="spec" label="规格型号" min-width="120" />
            <el-table-column label="订单数量" width="90" align="right">
              <template #default="{ row }">
                {{ fmtInt(row.quantity) }}
              </template>
            </el-table-column>
            <el-table-column label="已出库" width="80" align="right">
              <template #default="{ row }">
                {{ fmtInt(row.delivered_qty) }}
              </template>
            </el-table-column>
            <el-table-column label="还需" width="80" align="right">
              <template #default="{ row }">
                <el-tag v-if="Number(row.remaining) > 0" type="warning" size="small">{{ fmtInt(row.remaining) }}</el-tag>
                <span v-else>0</span>
              </template>
            </el-table-column>
            <el-table-column label="当前库存" width="90" align="right">
              <template #default="{ row }">
                <el-tag v-if="Number(row.stock_qty) < Number(row.remaining)" type="danger" size="small">{{ fmtInt(row.stock_qty) }}</el-tag>
                <span v-else>{{ fmtInt(row.stock_qty) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="本次出库" width="130" align="center">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.out_qty"
                  :min="0"
                  :max="Math.min(Number(row.remaining), Number(row.stock_qty))"
                  :precision="0"
                  :controls="false"
                  size="small"
                  style="width: 100px"
                  @change="(val) => onOutQtyChange(order, row, val)"
                />
              </template>
            </el-table-column>
          </el-table>

          <div class="order-footer">
            <div class="footer-left">
              <span v-if="!order.allow_partial_shipment" class="hint-text hint-danger">
                <el-icon><Warning /></el-icon>
                该客户要求整单出库，必须所有物料备齐才能提交
              </span>
              <span v-else class="hint-text hint-info">
                <el-icon><Info-Filled /></el-icon>
                允许部分出货，提交后未出库物料将自动生成新订单
              </span>
            </div>
            <div class="footer-right">
              <el-button
                type="primary"
                size="small"
                :loading="submitLoading[order.id]"
                :disabled="!canSubmit(order)"
                @click="handleSubmit(order)"
              >
                提交出库
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning, InfoFilled } from '@element-plus/icons-vue'
import { getPendingOutStockOrders, createOutStock } from '@/api/sales'

const orderList = ref([])
const submitLoading = ref({})

const fetchData = async () => {
  const res = await getPendingOutStockOrders()
  const list = res.data || []
  // 给每个明细初始化本次出库数量
  list.forEach(order => {
    order.items.forEach(item => {
      item.out_qty = 0
    })
  })
  orderList.value = list
}

const statusType = (s) => ({ confirmed: 'primary', partial: 'warning', completed: 'success', cancelled: 'danger', draft: 'info' }[s] || '')

const fmtInt = (val) => {
  if (val === null || val === undefined) return '0'
  const n = Math.round(Number(val))
  return isNaN(n) ? '0' : String(n)
}

/**
 * 本次出库数量变化时的处理
 */
const onOutQtyChange = (order, row, val) => {
  // 自动校验：如果客户不允许部分出货，本次出库数量必须等于还需数量
  if (!order.allow_partial_shipment && val > 0) {
    const remaining = Number(row.remaining)
    if (val !== remaining) {
      // 不强制修改，但在提交时校验
    }
  }
}

/**
 * 判断订单是否可以提交出库
 */
const canSubmit = (order) => {
  const items = order.items.filter(item => (item.out_qty || 0) > 0)
  if (items.length === 0) return false

  if (!order.allow_partial_shipment) {
    // 不允许部分出货：必须所有物料的本次出库 = 还需数量
    for (const item of order.items) {
      const remaining = Number(item.remaining)
      if (remaining > 0) {
        const outQty = Number(item.out_qty || 0)
        if (outQty !== remaining) {
          return false
        }
      }
    }
  }
  return true
}

const handleSubmit = async (order) => {
  const items = order.items.filter(item => (item.out_qty || 0) > 0)
  if (items.length === 0) {
    ElMessage.warning('请至少填写一条出库数量')
    return
  }

  // 检查库存是否充足
  const shortage = items.filter(item => Number(item.out_qty) > Number(item.stock_qty))
  if (shortage.length > 0) {
    ElMessage.error(`库存不足：${shortage[0].material_name}`)
    return
  }

  // 不允许部分出货的客户，二次确认
  if (!order.allow_partial_shipment) {
    const unfulfilled = order.items.filter(item => Number(item.remaining) > 0 && Number(item.out_qty || 0) !== Number(item.remaining))
    if (unfulfilled.length > 0) {
      ElMessage.warning('该客户要求整单出库，请将所有物料的本次出库数量填充满')
      return
    }
  }

  // 允许部分出货的客户，提示会拆单
  let confirmMsg = '确定提交出库吗？'
  if (order.allow_partial_shipment) {
    const hasRemaining = order.items.some(item => {
      const remaining = Number(item.remaining)
      const outQty = Number(item.out_qty || 0)
      return remaining > outQty
    })
    if (hasRemaining) {
      confirmMsg = '该订单还有未出库物料，提交后将自动拆单生成新订单，确定继续吗？'
    }
  }

  try {
    await ElMessageBox.confirm(confirmMsg, '确认出库', { type: 'warning' })
  } catch {
    return
  }

  submitLoading.value[order.id] = true
  try {
    const payload = {
      order: order.id,
      stock_date: new Date().toISOString().slice(0, 10),
      warehouse: '默认仓库',
      remark: '',
      items: items.map(item => ({
        material_name: item.material_name,
        spec: item.spec,
        quantity: item.out_qty,
        unit: item.unit,
        remark: ''
      }))
    }
    await createOutStock(payload)
    ElMessage.success('出库成功')
    await fetchData()
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.message || error?.message || '出库失败'
    ElMessage.error(msg)
  } finally {
    submitLoading.value[order.id] = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.page-title { margin: 0; font-size: 18px; }
.empty-text { text-align: center; color: #909399; padding: 40px; }
.order-card { margin-bottom: 15px; }
.order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.order-header-left { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }
.order-no { font-size: 16px; font-weight: bold; }
.status-tag { margin-left: 0; }
.order-info { color: #606266; font-size: 13px; }
.order-info span { margin-left: 15px; }
.item-table { margin-bottom: 10px; }
.order-footer { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
.footer-left { flex: 1; }
.footer-right { flex-shrink: 0; }
.hint-text { font-size: 13px; display: inline-flex; align-items: center; gap: 4px; }
.hint-danger { color: #F56C6C; }
.hint-info { color: #409EFF; }
</style>
