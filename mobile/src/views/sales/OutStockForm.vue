<template>
  <div class="form-page">
    <van-form @submit="onSubmit" class="form-content">
      <van-cell-group inset>
        <!-- 选择订单 -->
        <van-field
          v-model="orderDisplay"
          required
          is-link
          readonly
          label="关联订单"
          placeholder="请选择销售订单"
          :rules="[{ required: true, message: '请选择销售订单' }]"
          @click="showOrderPicker = true"
        />
        <!-- 出库日期 -->
        <van-field
          v-model="form.stock_date"
          required
          is-link
          readonly
          label="出库日期"
          placeholder="请选择出库日期"
          :rules="[{ required: true, message: '请选择出库日期' }]"
          @click="showDatePicker = true"
        />
        <!-- 仓库 -->
        <van-field
          v-model="form.warehouse"
          label="出库仓库"
          placeholder="请输入仓库名称"
        />
        <!-- 备注 -->
        <van-field
          v-model="form.remark"
          label="备注"
          type="textarea"
          rows="2"
          placeholder="请输入备注（可选）"
        />
      </van-cell-group>

      <!-- 物料明细 -->
      <div v-if="form.items.length > 0" class="section-title">出库明细</div>
      <div v-for="(item, index) in form.items" :key="index" class="item-card">
        <div class="item-header">
          <span class="item-name">{{ item.material_name }}</span>
          <span class="item-meta">待出: {{ item.remaining }} / 库存: {{ item.stock_qty }}</span>
        </div>
        <div class="item-body">
          <div class="item-info">规格：{{ item.spec || '-' }} &nbsp; 单位：{{ item.unit }}</div>
          <van-field
            v-model="item.quantity"
            label="本次出库"
            type="number"
            placeholder="请输入数量"
          />
        </div>
      </div>

      <div class="form-actions">
        <van-button round block type="primary" native-type="submit" :loading="submitting">
          {{ isEdit ? '保存' : '提交' }}
        </van-button>
      </div>
    </van-form>

    <!-- 订单选择 -->
    <van-popup v-model:show="showOrderPicker" round position="bottom">
      <van-picker
        :columns="orderColumns"
        @cancel="showOrderPicker = false"
        @confirm="onOrderConfirm"
      />
    </van-popup>

    <!-- 日期选择 -->
    <van-popup v-model:show="showDatePicker" round position="bottom">
      <van-date-picker
        v-model="dateValue"
        title="选择出库日期"
        :min-date="minDate"
        @cancel="showDatePicker = false"
        @confirm="onDateConfirm"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createOutStock, updateOutStock, getOutStockDetail, getPendingOutStockOrders, getOrderOutStockItems } from '@/api/sales'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const submitting = ref(false)
const showOrderPicker = ref(false)
const showDatePicker = ref(false)
const orderDisplay = ref('')
const orderColumns = ref([])
const dateValue = ref(['', '', ''])
const minDate = new Date(2020, 0, 1)

const form = ref({
  order: null,
  stock_date: '',
  warehouse: '默认仓库',
  remark: '',
  items: [],
})

const loadPendingOrders = async () => {
  try {
    const res = await getPendingOutStockOrders()
    const list = res.data || []
    orderColumns.value = list.map(o => ({
      text: `${o.order_no} (${o.customer_name})`,
      value: o.id,
      raw: o,
    }))
  } catch (e) {
    console.error('加载订单失败', e)
  }
}

const onOrderConfirm = async ({ selectedOptions }) => {
  const opt = selectedOptions[0]
  form.value.order = opt.value
  orderDisplay.value = opt.text
  showOrderPicker.value = false

  // 加载订单可出库物料
  try {
    showLoadingToast({ message: '加载物料...', forbidClick: true })
    const res = await getOrderOutStockItems(opt.value)
    closeToast()
    const data = res.data || {}
    form.value.items = (data.items || []).map(item => ({
      ...item,
      quantity: '',
    }))
  } catch (e) {
    closeToast()
    showToast('加载物料失败')
  }
}

const onDateConfirm = ({ selectedValues }) => {
  form.value.stock_date = selectedValues.join('-')
  showDatePicker.value = false
}

const onSubmit = async () => {
  // 校验至少有一行物料有数量
  const validItems = form.value.items
    .filter(i => i.quantity !== '' && Number(i.quantity) > 0)
    .map(i => ({
      material_name: i.material_name,
      spec: i.spec || null,
      quantity: Number(i.quantity),
      unit: i.unit,
      remark: null,
    }))

  if (validItems.length === 0) {
    showToast('请至少填写一行出库数量')
    return
  }

  submitting.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })
  try {
    const data = {
      order: form.value.order,
      stock_date: form.value.stock_date,
      warehouse: form.value.warehouse || '默认仓库',
      remark: form.value.remark || null,
      items: validItems,
    }
    if (isEdit.value) {
      await updateOutStock(route.params.id || route.query.id, data)
    } else {
      await createOutStock(data)
    }
    closeToast()
    showToast(isEdit.value ? '保存成功' : '新增成功')
    router.back()
  } catch (e) {
    closeToast()
    showToast(e?.response?.data?.message || e?.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await loadPendingOrders()

  // 默认今天
  const today = new Date()
  const y = String(today.getFullYear())
  const m = String(today.getMonth() + 1).padStart(2, '0')
  const d = String(today.getDate()).padStart(2, '0')
  form.value.stock_date = `${y}-${m}-${d}`
  dateValue.value = [y, m, d]

  const id = route.query.id || route.params.id
  if (id) {
    isEdit.value = true
    try {
      const res = await getOutStockDetail(id)
      const item = res.data
      form.value.order = item.order
      form.value.stock_date = item.stock_date || ''
      form.value.warehouse = item.warehouse || '默认仓库'
      form.value.remark = item.remark || ''
      orderDisplay.value = item.order_no || ''

      // 尝试从订单重新加载物料，并回填数量
      try {
        const orderRes = await getOrderOutStockItems(item.order)
        const data = orderRes.data || {}
        const orderItems = data.items || []
        const savedItems = item.items || []
        form.value.items = orderItems.map(oi => {
          const saved = savedItems.find(si => si.material_name === oi.material_name && (si.spec || '') === (oi.spec || ''))
          return {
            ...oi,
            quantity: saved ? String(saved.quantity) : '',
          }
        })
      } catch (e) {
        // 回退：直接显示已保存的明细
        form.value.items = (item.items || []).map(i => ({
          material_name: i.material_name,
          spec: i.spec,
          quantity: String(i.quantity),
          unit: i.unit,
          stock_qty: '-',
          remaining: '-',
        }))
      }

      if (item.stock_date) {
        const parts = item.stock_date.split('-')
        if (parts.length === 3) dateValue.value = parts
      }
    } catch (e) {
      showToast('加载数据失败')
    }
  }
})
</script>

<style scoped>
.form-page {
  min-height: 100vh;
  background: #f7f8fa;
}
.form-content {
  padding-top: 12px;
}
.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #666;
  padding: 16px 12px 8px;
}
.item-card {
  margin: 0 12px 10px;
  background: #fff;
  border-radius: 8px;
  padding: 12px;
}
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.item-name {
  font-size: 15px;
  font-weight: 600;
  color: #323233;
}
.item-meta {
  font-size: 12px;
  color: #969799;
}
.item-body {
  font-size: 13px;
  color: #666;
}
.item-info {
  margin-bottom: 8px;
}
.form-actions {
  margin: 20px 16px;
}
</style>
