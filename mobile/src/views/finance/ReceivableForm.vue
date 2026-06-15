<template>
  <div class="form-page">
    <van-form @submit="onSubmit" class="form-content">
      <van-cell-group inset>
        <van-field
          v-model="typeLabel"
          required
          is-link
          readonly
          label="单据类型"
          placeholder="请选择类型"
          :rules="[{ required: true, message: '请选择类型' }]"
          @click="showTypePicker = true"
        />
        <van-field
          v-model="form.counterparty"
          name="counterparty"
          label="往来单位"
          placeholder="请输入往来单位"
          :rules="[{ required: true, message: '请输入往来单位' }]"
        />
        <van-field
          v-model="form.amount"
          name="amount"
          label="金额"
          type="number"
          placeholder="请输入金额"
          :rules="[{ required: true, message: '请输入金额' }]"
        />
        <van-field
          v-model="form.bill_date"
          required
          is-link
          readonly
          label="业务日期"
          placeholder="请选择业务日期"
          :rules="[{ required: true, message: '请选择业务日期' }]"
          @click="showDatePicker = true"
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
      <van-date-picker v-model="dateValue" title="选择业务日期" :min-date="minDate" @cancel="showDatePicker = false" @confirm="onDateConfirm" />
    </van-popup>
    <van-popup v-model:show="showTypePicker" round position="bottom">
      <van-picker :columns="typeOptions" @cancel="showTypePicker = false" @confirm="onTypeConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createReceivable, updateReceivable, getReceivableDetail } from '@/api/finance'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const submitting = ref(false)
const showDatePicker = ref(false)
const showTypePicker = ref(false)
const dateValue = ref(['', '', ''])
const minDate = new Date(2020, 0, 1)
const typeLabel = ref('')

const typeOptions = [
  { text: '应收', value: 'receivable' },
  { text: '应付', value: 'payable' },
]

const form = ref({
  doc_type: 'receivable',
  counterparty: '',
  amount: '',
  bill_date: '',
  remark: '',
})

const onDateConfirm = ({ selectedValues }) => {
  form.value.bill_date = selectedValues.join('-')
  showDatePicker.value = false
}
const onTypeConfirm = ({ selectedOptions }) => {
  const opt = selectedOptions[0]
  form.value.doc_type = opt.value
  typeLabel.value = opt.text
  showTypePicker.value = false
}

const onSubmit = async () => {
  submitting.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })
  try {
    const data = {
      doc_type: form.value.doc_type,
      counterparty: form.value.counterparty,
      amount: form.value.amount !== '' && form.value.amount != null ? parseFloat(form.value.amount) || 0 : 0,
      bill_date: form.value.bill_date,
      remark: form.value.remark || null,
    }
    if (isEdit.value) { await updateReceivable(route.params.id, data) }
    else { await createReceivable(data) }
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
  form.value.bill_date = `${y}-${m}-${d}`
  dateValue.value = [y, m, d]
  const t = typeOptions.find(o => o.value === 'receivable')
  typeLabel.value = t ? t.text : ''
  if (route.params.id) {
    isEdit.value = true
    try {
      const res = await getReceivableDetail(route.params.id)
      const item = res.data
      form.value.doc_type = item.doc_type || 'receivable'
      form.value.counterparty = item.counterparty || ''
      form.value.amount = item.amount != null ? String(item.amount) : ''
      form.value.bill_date = item.bill_date || ''
      form.value.remark = item.remark || ''
      const tp = typeOptions.find(o => o.value === form.value.doc_type)
      typeLabel.value = tp ? tp.text : ''
      if (item.bill_date) { const p = item.bill_date.split('-'); if (p.length === 3) dateValue.value = p }
    } catch (e) { showToast('加载数据失败') }
  }
})
</script>

<style scoped>
.form-page { min-height: 100vh; background: #f7f8fa; }
.form-content { padding-top: 12px; }
.form-actions { margin: 20px 16px; }
</style>
