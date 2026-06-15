<template>
  <div class="form-page">
    <van-form @submit="onSubmit" class="form-content">
      <van-cell-group inset>
        <van-field
          v-model="form.stock_date"
          required
          is-link
          readonly
          label="入库日期"
          placeholder="请选择入库日期"
          :rules="[{ required: true, message: '请选择入库日期' }]"
          @click="showDatePicker = true"
        />
        <van-field
          v-model="form.warehouse"
          name="warehouse"
          label="入库仓库"
          placeholder="请输入仓库名称"
        />
        <van-field
          v-model="form.product_name"
          name="product_name"
          label="产品名称"
          placeholder="请输入产品名称"
          :rules="[{ required: true, message: '请输入产品名称' }]"
        />
        <van-field
          v-model="form.quantity"
          name="quantity"
          label="入库数量"
          type="number"
          placeholder="请输入入库数量"
        />
        <van-field
          v-model="form.remark"
          name="remark"
          label="备注"
          type="textarea"
          rows="2"
          placeholder="请输入备注（可选）"
        />
      </van-cell-group>
      <div class="form-actions">
        <van-button round block type="primary" native-type="submit" :loading="submitting">
          {{ isEdit ? '保存' : '提交' }}
        </van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showDatePicker" round position="bottom">
      <van-date-picker v-model="dateValue" title="选择入库日期" :min-date="minDate" @cancel="showDatePicker = false" @confirm="onDateConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createProductionInStock, updateProductionInStock, getProductionInStockDetail } from '@/api/production'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const submitting = ref(false)
const showDatePicker = ref(false)
const dateValue = ref(['', '', ''])
const minDate = new Date(2020, 0, 1)

const form = ref({
  stock_date: '',
  warehouse: '默认仓库',
  product_name: '',
  quantity: '1',
  remark: '',
})

const onDateConfirm = ({ selectedValues }) => {
  form.value.stock_date = selectedValues.join('-')
  showDatePicker.value = false
}

const onSubmit = async () => {
  submitting.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })
  try {
    const data = {
      stock_date: form.value.stock_date,
      warehouse: form.value.warehouse || '默认仓库',
      product_name: form.value.product_name,
      quantity: form.value.quantity !== '' && form.value.quantity != null ? parseFloat(form.value.quantity) || 1 : 1,
      remark: form.value.remark || null,
    }
    if (isEdit.value) { await updateProductionInStock(route.params.id, data) }
    else { await createProductionInStock(data) }
    closeToast()
    showToast(isEdit.value ? '保存成功' : '新增成功')
    router.back()
  } catch (e) {
    closeToast()
    showToast(e?.response?.data?.message || e?.response?.data?.detail || '操作失败')
  } finally { submitting.value = false }
}

onMounted(async () => {
  const today = new Date()
  const y = String(today.getFullYear()), m = String(today.getMonth() + 1).padStart(2, '0'), d = String(today.getDate()).padStart(2, '0')
  form.value.stock_date = `${y}-${m}-${d}`
  dateValue.value = [y, m, d]
  if (route.params.id) {
    isEdit.value = true
    try {
      const res = await getProductionInStockDetail(route.params.id)
      const item = res.data
      form.value.stock_date = item.stock_date || ''
      form.value.warehouse = item.warehouse || '默认仓库'
      form.value.product_name = item.product_name || ''
      form.value.quantity = item.quantity != null ? String(item.quantity) : '1'
      form.value.remark = item.remark || ''
      if (item.stock_date) { const p = item.stock_date.split('-'); if (p.length === 3) dateValue.value = p }
    } catch (e) { showToast('加载数据失败') }
  }
})
</script>

<style scoped>
.form-page { min-height: 100vh; background: #f7f8fa; }
.form-content { padding-top: 12px; }
.form-actions { margin: 20px 16px; }
</style>
