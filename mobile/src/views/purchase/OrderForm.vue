<template>
  <div class="page">
    <van-nav-bar :title="isEdit ? '编辑采购订单' : '新增采购订单'" fixed placeholder left-arrow @click-left="onClickLeft" />
    <div class="form-content">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.order_no"
            required
            label="订单编号"
            placeholder="请输入订单编号"
            :rules="[{ required: true, message: '请输入订单编号' }]"
          />
          <van-field
            v-model="form.supplier_name"
            is-link
            readonly
            required
            label="供应商"
            placeholder="请选择供应商"
            :rules="[{ required: true, message: '请选择供应商' }]"
            @click="showSupplierPicker = true"
          />
          <van-field
            v-model="form.order_date"
            is-link
            readonly
            required
            label="订单日期"
            placeholder="请选择订单日期"
            :rules="[{ required: true, message: '请选择订单日期' }]"
            @click="showDatePicker = true"
          />
          <van-field
            v-model="form.delivery_date"
            is-link
            readonly
            label="交货日期"
            placeholder="请选择交货日期"
            @click="showDeliveryDatePicker = true"
          />
          <van-field
            v-model="form.remark"
            rows="2"
            autosize
            type="textarea"
            label="备注"
            placeholder="请输入备注"
          />
        </van-cell-group>

        <!-- 明细列表 -->
        <div class="section-title">订单明细</div>
        <div v-for="(item, index) in form.items" :key="index" class="item-card">
          <div class="item-header">
            <span>明细 {{ index + 1 }}</span>
            <van-button size="mini" type="danger" plain @click="removeItem(index)">删除</van-button>
          </div>
          <van-field v-model="item.material_name" required label="物料名称" placeholder="请输入物料名称" />
          <van-field v-model="item.spec" label="规格型号" placeholder="请输入规格" />
          <van-field v-model.number="item.quantity" required type="digit" label="数量" placeholder="请输入数量" />
          <van-field v-model.number="item.price" required type="number" label="单价" placeholder="请输入单价" />
          <van-field v-model="item.unit" label="单位" placeholder="请输入单位" />
          <van-field v-model="item.remark" label="备注" placeholder="请输入备注" />
        </div>
        <div class="add-item-btn">
          <van-button size="small" type="primary" plain icon="plus" @click="addItem">添加明细</van-button>
        </div>

        <div class="submit-btn">
          <van-button round block type="primary" native-type="submit" :loading="submitting">
            {{ isEdit ? '保存' : '提交' }}
          </van-button>
        </div>
      </van-form>
    </div>

    <!-- 供应商选择 -->
    <van-popup v-model:show="showSupplierPicker" round position="bottom">
      <van-picker :columns="supplierColumns" @cancel="showSupplierPicker = false" @confirm="onSupplierConfirm" />
    </van-popup>

    <!-- 日期选择 -->
    <van-popup v-model:show="showDatePicker" round position="bottom">
      <van-date-picker v-model="datePickerValue" title="选择订单日期" @cancel="showDatePicker = false" @confirm="onDateConfirm" />
    </van-popup>

    <!-- 交货日期选择 -->
    <van-popup v-model:show="showDeliveryDatePicker" round position="bottom">
      <van-date-picker v-model="deliveryDatePickerValue" title="选择交货日期" @cancel="showDeliveryDatePicker = false" @confirm="onDeliveryDateConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { createPurchaseOrder, updatePurchaseOrder, getPurchaseOrderDetail } from '@/api/purchase'
import { getSupplierOptions } from '@/api/purchase'

const route = useRoute()
const router = useRouter()

const isEdit = ref(false)
const submitting = ref(false)
const orderId = ref(null)

const form = ref({
  order_no: '',
  supplier: '',
  supplier_name: '',
  order_date: '',
  delivery_date: '',
  remark: '',
  items: [],
})

const showSupplierPicker = ref(false)
const showDatePicker = ref(false)
const showDeliveryDatePicker = ref(false)

const datePickerValue = ref(['', '', ''])
const deliveryDatePickerValue = ref(['', '', ''])

const supplierColumns = ref([])

onMounted(async () => {
  const id = route.query.id
  if (id) {
    isEdit.value = true
    orderId.value = id
    await loadDetail(id)
  } else {
    const today = new Date()
    const y = String(today.getFullYear())
    const m = String(today.getMonth() + 1).padStart(2, '0')
    const d = String(today.getDate()).padStart(2, '0')
    form.value.order_date = `${y}-${m}-${d}`
    datePickerValue.value = [y, m, d]
  }

  try {
    const res = await getSupplierOptions()
    const list = res.data?.results || res.data?.list || res.results || []
    supplierColumns.value = list.map(item => ({ text: item.name || item.label || item, value: item.id || item.value || item }))
  } catch (e) {
    console.error('加载供应商列表失败', e)
  }
})

async function loadDetail(id) {
  try {
    const res = await getPurchaseOrderDetail(id)
    const item = res.data
    if (item) {
      form.value = {
        order_no: item.order_no || '',
        supplier: item.supplier || '',
        supplier_name: item.supplier_name || '',
        order_date: item.order_date || '',
        delivery_date: item.delivery_date || '',
        remark: item.remark || '',
        items: (item.items || []).map(i => ({
          material_name: i.material_name || '',
          spec: i.spec || '',
          quantity: i.quantity || 0,
          price: i.price || 0,
          unit: i.unit || '件',
          remark: i.remark || '',
        })),
      }
      if (item.order_date) {
        const [y, m, d] = item.order_date.split('-')
        datePickerValue.value = [y, m, d]
      }
      if (item.delivery_date) {
        const [y, m, d] = item.delivery_date.split('-')
        deliveryDatePickerValue.value = [y, m, d]
      }
    }
  } catch (e) {
    showToast('加载详情失败')
  }
}

function onClickLeft() {
  router.back()
}

function onSupplierConfirm({ selectedOptions }) {
  form.value.supplier = selectedOptions[0].value
  form.value.supplier_name = selectedOptions[0].text
  showSupplierPicker.value = false
}

function onDateConfirm({ selectedValues }) {
  form.value.order_date = selectedValues.join('-')
  showDatePicker.value = false
}

function onDeliveryDateConfirm({ selectedValues }) {
  form.value.delivery_date = selectedValues.join('-')
  showDeliveryDatePicker.value = false
}

function addItem() {
  form.value.items.push({ material_name: '', spec: '', quantity: 1, price: 0, unit: '件', remark: '' })
}

function removeItem(index) {
  form.value.items.splice(index, 1)
}

async function onSubmit() {
  if (form.value.items.length === 0) {
    showFailToast('请至少添加一条明细')
    return
  }
  submitting.value = true
  try {
    const data = { ...form.value }
    delete data.supplier_name
    if (isEdit.value) {
      await updatePurchaseOrder(orderId.value, data)
      showToast('修改成功')
    } else {
      await createPurchaseOrder(data)
      showToast('添加成功')
    }
    router.back()
  } catch (e) {
    showFailToast(e?.response?.data?.message || e.message || '操作失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f5f5f5;
}
.form-content {
  padding-top: 12px;
}
.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #666;
  padding: 16px 16px 8px;
}
.item-card {
  margin: 0 12px 10px;
  background-color: #fff;
  border-radius: 8px;
  padding: 12px;
}
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: bold;
  color: #323233;
}
.add-item-btn {
  text-align: center;
  margin: 12px;
}
.submit-btn {
  margin: 24px 16px;
}
</style>
