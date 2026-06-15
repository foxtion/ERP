<template>
  <div class="form-page">
    <van-form @submit="onSubmit" class="form-content">
      <van-cell-group inset>
        <van-field
          v-model="form.voucher_no"
          name="voucher_no"
          label="凭证号"
          placeholder="留空将自动生成"
        />
        <van-field
          v-model="form.voucher_date"
          required
          is-link
          readonly
          label="凭证日期"
          placeholder="请选择凭证日期"
          :rules="[{ required: true, message: '请选择凭证日期' }]"
          @click="showDatePicker = true"
        />
        <van-field
          v-model="form.summary"
          name="summary"
          label="摘要"
          placeholder="请输入摘要"
        />
      </van-cell-group>

      <div class="section-title">
        <span>凭证明细</span>
        <van-button size="small" type="primary" plain @click="addItem">+ 添加明细</van-button>
      </div>

      <div v-for="(item, index) in form.items" :key="index" class="item-card">
        <div class="item-header">
          <span class="item-index">明细 {{ index + 1 }}</span>
          <van-button size="mini" type="danger" plain @click="removeItem(index)">删除</van-button>
        </div>
        <van-field v-model="item.summary" label="摘要" placeholder="请输入摘要" />
        <van-field v-model="item.debit" label="借方金额" type="number" placeholder="请输入借方金额" />
        <van-field v-model="item.credit" label="贷方金额" type="number" placeholder="请输入贷方金额" />
      </div>

      <div v-if="form.items.length === 0" class="empty-tip">暂无明细，请点击上方按钮添加</div>

      <div class="form-actions">
        <van-button round block type="primary" native-type="submit" :loading="submitting">
          {{ isEdit ? '保存' : '提交' }}
        </van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showDatePicker" round position="bottom">
      <van-date-picker v-model="dateValue" title="选择凭证日期" :min-date="minDate" @cancel="showDatePicker = false" @confirm="onDateConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createVoucher, updateVoucher, getVoucherDetail } from '@/api/finance'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const submitting = ref(false)
const showDatePicker = ref(false)
const dateValue = ref(['', '', ''])
const minDate = new Date(2020, 0, 1)

const form = ref({
  voucher_no: '',
  voucher_date: '',
  summary: '',
  items: [],
})

const addItem = () => { form.value.items.push({ summary: '', debit: '0', credit: '0' }) }
const removeItem = (index) => { form.value.items.splice(index, 1) }

const onDateConfirm = ({ selectedValues }) => {
  form.value.voucher_date = selectedValues.join('-')
  showDatePicker.value = false
}

const onSubmit = async () => {
  if (form.value.items.length === 0) { showToast('请至少添加一条明细'); return }
  submitting.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })
  try {
    const data = {
      voucher_no: form.value.voucher_no || null,
      voucher_date: form.value.voucher_date,
      summary: form.value.summary || null,
      items: form.value.items.map(i => ({
        summary: i.summary || '',
        debit: i.debit !== '' && i.debit != null ? parseFloat(i.debit) || 0 : 0,
        credit: i.credit !== '' && i.credit != null ? parseFloat(i.credit) || 0 : 0,
      })),
    }
    if (isEdit.value) { await updateVoucher(route.params.id, data) }
    else { await createVoucher(data) }
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
  form.value.voucher_date = `${y}-${m}-${d}`
  dateValue.value = [y, m, d]
  if (route.params.id) {
    isEdit.value = true
    try {
      const res = await getVoucherDetail(route.params.id)
      const item = res.data
      form.value.voucher_no = item.voucher_no || ''
      form.value.voucher_date = item.voucher_date || ''
      form.value.summary = item.summary || ''
      form.value.items = (item.items || []).map(i => ({
        summary: i.summary || '', debit: i.debit != null ? String(i.debit) : '0', credit: i.credit != null ? String(i.credit) : '0',
      }))
      if (item.voucher_date) { const p = item.voucher_date.split('-'); if (p.length === 3) dateValue.value = p }
    } catch (e) { showToast('加载数据失败') }
  }
})
</script>

<style scoped>
.form-page { min-height: 100vh; background: #f7f8fa; }
.form-content { padding-top: 12px; }
.section-title { display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: bold; color: #666; padding: 16px 12px 8px; }
.item-card { margin: 0 12px 10px; background: #fff; border-radius: 8px; padding: 12px; }
.item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.item-index { font-size: 14px; font-weight: 600; color: #323233; }
.empty-tip { text-align: center; font-size: 13px; color: #969799; padding: 20px; }
.form-actions { margin: 20px 16px 40px; }
</style>
