<template>
  <div class="form-page">
    <van-form @submit="onSubmit" class="form-content">
      <van-cell-group inset>
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
          label="数量"
          type="number"
          placeholder="请输入数量"
        />
        <van-field
          v-model="form.plan_date"
          required
          is-link
          readonly
          label="计划日期"
          placeholder="请选择计划日期"
          :rules="[{ required: true, message: '请选择计划日期' }]"
          @click="showDatePicker = true"
        />
        <van-field
          v-model="priorityLabel"
          required
          is-link
          readonly
          label="优先级"
          placeholder="请选择优先级"
          :rules="[{ required: true, message: '请选择优先级' }]"
          @click="showPriorityPicker = true"
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
      <van-date-picker
        v-model="dateValue"
        title="选择计划日期"
        :min-date="minDate"
        @cancel="showDatePicker = false"
        @confirm="onDateConfirm"
      />
    </van-popup>

    <van-popup v-model:show="showPriorityPicker" round position="bottom">
      <van-picker
        :columns="priorityOptions"
        @cancel="showPriorityPicker = false"
        @confirm="onPriorityConfirm"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createWorkOrder, updateWorkOrder, getWorkOrderDetail } from '@/api/production'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const submitting = ref(false)
const showDatePicker = ref(false)
const showPriorityPicker = ref(false)
const dateValue = ref(['', '', ''])
const minDate = new Date(2020, 0, 1)
const priorityLabel = ref('')

const priorityOptions = [
  { text: '紧急', value: 'urgent' },
  { text: '高', value: 'high' },
  { text: '普通', value: 'normal' },
  { text: '低', value: 'low' },
]

const form = ref({
  product_name: '',
  quantity: '1',
  plan_date: '',
  priority: 'normal',
  remark: '',
})

const onDateConfirm = ({ selectedValues }) => {
  form.value.plan_date = selectedValues.join('-')
  showDatePicker.value = false
}

const onPriorityConfirm = ({ selectedOptions }) => {
  const opt = selectedOptions[0]
  form.value.priority = opt.value
  priorityLabel.value = opt.text
  showPriorityPicker.value = false
}

const onSubmit = async () => {
  submitting.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })
  try {
    const data = {
      product_name: form.value.product_name,
      quantity: form.value.quantity !== '' ? parseFloat(form.value.quantity) : 1,
      plan_date: form.value.plan_date,
      priority: form.value.priority,
      remark: form.value.remark || null,
    }
    if (isEdit.value) {
      await updateWorkOrder(route.params.id, data)
    } else {
      await createWorkOrder(data)
    }
    closeToast()
    showToast(isEdit.value ? '保存成功' : '新增成功')
    router.back()
  } catch (e) {
    closeToast()
    showToast(e?.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const today = new Date()
  const y = String(today.getFullYear())
  const m = String(today.getMonth() + 1).padStart(2, '0')
  const d = String(today.getDate()).padStart(2, '0')
  form.value.plan_date = `${y}-${m}-${d}`
  dateValue.value = [y, m, d]

  if (route.params.id) {
    isEdit.value = true
    try {
      const res = await getWorkOrderDetail(route.params.id)
      const item = res.data
      form.value.product_name = item.product_name || ''
      form.value.quantity = item.quantity != null ? String(item.quantity) : '1'
      form.value.plan_date = item.plan_date || ''
      form.value.priority = item.priority || 'normal'
      form.value.remark = item.remark || ''
      const p = priorityOptions.find(o => o.value === form.value.priority)
      priorityLabel.value = p ? p.text : ''
      if (item.plan_date) {
        const parts = item.plan_date.split('-')
        if (parts.length === 3) dateValue.value = parts
      }
    } catch (e) {
      showToast('加载数据失败')
    }
  } else {
    const p = priorityOptions.find(o => o.value === 'normal')
    priorityLabel.value = p ? p.text : ''
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
.form-actions {
  margin: 20px 16px;
}
</style>
