<template>
  <div class="form-page">
    <van-form @submit="onSubmit" class="form-content">
      <van-cell-group inset>
        <van-field
          v-model="typeLabel"
          required
          is-link
          readonly
          label="类型"
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
          v-model="methodLabel"
          required
          is-link
          readonly
          label="支付方式"
          placeholder="请选择支付方式"
          :rules="[{ required: true, message: '请选择支付方式' }]"
          @click="showMethodPicker = true"
        />
        <van-field
          v-model="form.payment_date"
          required
          is-link
          readonly
          label="日期"
          placeholder="请选择日期"
          :rules="[{ required: true, message: '请选择日期' }]"
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
      <van-date-picker v-model="dateValue" title="选择日期" :min-date="minDate" @cancel="showDatePicker = false" @confirm="onDateConfirm" />
    </van-popup>
    <van-popup v-model:show="showTypePicker" round position="bottom">
      <van-picker :columns="typeOptions" @cancel="showTypePicker = false" @confirm="onTypeConfirm" />
    </van-popup>
    <van-popup v-model:show="showMethodPicker" round position="bottom">
      <van-picker :columns="methodOptions" @cancel="showMethodPicker = false" @confirm="onMethodConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createPayment, updatePayment, getPaymentDetail } from '@/api/finance'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const submitting = ref(false)
const showDatePicker = ref(false)
const showTypePicker = ref(false)
const showMethodPicker = ref(false)
const dateValue = ref(['', '', ''])
const minDate = new Date(2020, 0, 1)
const typeLabel = ref('')
const methodLabel = ref('')

const typeOptions = [
  { text: '收款', value: 'receipt' },
  { text: '付款', value: 'payment' },
]

const methodOptions = [
  { text: '现金', value: 'cash' },
  { text: '银行转账', value: 'bank_transfer' },
  { text: '支票', value: 'check' },
  { text: '微信支付', value: 'wechat' },
  { text: '支付宝', value: 'alipay' },
]

const form = ref({
  doc_type: 'receipt',
  counterparty: '',
  amount: '',
  payment_method: 'cash',
  payment_date: '',
  remark: '',
})

const onDateConfirm = ({ selectedValues }) => {
  form.value.payment_date = selectedValues.join('-')
  showDatePicker.value = false
}
const onTypeConfirm = ({ selectedOptions }) => {
  const opt = selectedOptions[0]
  form.value.doc_type = opt.value
  typeLabel.value = opt.text
  showTypePicker.value = false
}
const onMethodConfirm = ({ selectedOptions }) => {
  const opt = selectedOptions[0]
  form.value.payment_method = opt.value
  methodLabel.value = opt.text
  showMethodPicker.value = false
}

const onSubmit = async () => {
  submitting.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })
  try {
    const data = {
      doc_type: form.value.doc_type,
      counterparty: form.value.counterparty,
      amount: form.value.amount !== '' && form.value.amount != null ? parseFloat(form.value.amount) || 0 : 0,
      payment_method: form.value.payment_method,
      payment_date: form.value.payment_date,
      remark: form.value.remark || null,
    }
    if (isEdit.value) { await updatePayment(route.params.id, data) }
    else { await createPayment(data) }
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
  form.value.payment_date = `${y}-${m}-${d}`
  dateValue.value = [y, m, d]
  const t = typeOptions.find(o => o.value === 'receipt')
  typeLabel.value = t ? t.text : ''
  const mth = methodOptions.find(o => o.value === 'cash')
  methodLabel.value = mth ? mth.text : ''
  if (route.params.id) {
    isEdit.value = true
    try {
      const res = await getPaymentDetail(route.params.id)
      const item = res.data
      form.value.doc_type = item.doc_type || 'receipt'
      form.value.counterparty = item.counterparty || ''
      form.value.amount = item.amount != null ? String(item.amount) : ''
      form.value.payment_method = item.payment_method || 'cash'
      form.value.payment_date = item.payment_date || ''
      form.value.remark = item.remark || ''
      const tp = typeOptions.find(o => o.value === form.value.doc_type)
      typeLabel.value = tp ? tp.text : ''
      const mp = methodOptions.find(o => o.value === form.value.payment_method)
      methodLabel.value = mp ? mp.text : ''
      if (item.payment_date) { const p = item.payment_date.split('-'); if (p.length === 3) dateValue.value = p }
    } catch (e) { showToast('加载数据失败') }
  }
})
</script>

<style scoped>
.form-page { min-height: 100vh; background: #f7f8fa; }
.form-content { padding-top: 12px; }
.form-actions { margin: 20px 16px; }
</style>
