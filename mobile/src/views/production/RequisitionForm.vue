<template>
  <div class="form-page">
    <van-form @submit="onSubmit" class="form-content">
      <van-cell-group inset>
        <van-field
          v-model="form.requisition_date"
          required
          is-link
          readonly
          label="领料日期"
          placeholder="请选择领料日期"
          :rules="[{ required: true, message: '请选择领料日期' }]"
          @click="showDatePicker = true"
        />
        <van-field
          v-model="form.warehouse"
          name="warehouse"
          label="领料仓库"
          placeholder="请输入仓库名称"
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

      <div class="section-title">
        <span>领料明细</span>
        <van-button size="small" type="primary" plain @click="addItem">+ 添加明细</van-button>
      </div>

      <div v-for="(item, index) in form.items" :key="index" class="item-card">
        <div class="item-header">
          <span class="item-index">明细 {{ index + 1 }}</span>
          <van-button size="mini" type="danger" plain @click="removeItem(index)">删除</van-button>
        </div>
        <van-field v-model="item.material_name" label="物料名称" placeholder="请输入物料名称" :rules="[{ required: true, message: '请输入物料名称' }]" />
        <van-field v-model="item.spec" label="规格型号" placeholder="请输入规格型号" />
        <van-field v-model="item.quantity" label="领料数量" type="number" placeholder="请输入数量" />
        <van-field v-model="item.unit" label="单位" placeholder="请输入单位" />
        <van-field v-model="item.remark" label="备注" type="textarea" rows="1" placeholder="请输入备注" />
      </div>

      <div v-if="form.items.length === 0" class="empty-tip">暂无明细，请点击上方按钮添加</div>

      <div class="form-actions">
        <van-button round block type="primary" native-type="submit" :loading="submitting">
          {{ isEdit ? '保存' : '提交' }}
        </van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showDatePicker" round position="bottom">
      <van-date-picker v-model="dateValue" title="选择领料日期" :min-date="minDate" @cancel="showDatePicker = false" @confirm="onDateConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createRequisition, updateRequisition, getRequisitionDetail } from '@/api/production'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const submitting = ref(false)
const showDatePicker = ref(false)
const dateValue = ref(['', '', ''])
const minDate = new Date(2020, 0, 1)

const form = ref({
  requisition_date: '',
  warehouse: '默认仓库',
  remark: '',
  items: [],
})

const addItem = () => {
  form.value.items.push({ material_name: '', spec: '', quantity: '1', unit: '件', remark: '' })
}
const removeItem = (index) => { form.value.items.splice(index, 1) }

const onDateConfirm = ({ selectedValues }) => {
  form.value.requisition_date = selectedValues.join('-')
  showDatePicker.value = false
}

const onSubmit = async () => {
  if (form.value.items.length === 0) { showToast('请至少添加一条明细'); return }
  submitting.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })
  try {
    const data = {
      requisition_date: form.value.requisition_date,
      warehouse: form.value.warehouse || '默认仓库',
      remark: form.value.remark || null,
      items: form.value.items.map(i => ({
        material_name: i.material_name,
        spec: i.spec || null,
        quantity: i.quantity !== '' ? parseFloat(i.quantity) : 1,
        unit: i.unit || '件',
        remark: i.remark || null,
      })),
    }
    if (isEdit.value) { await updateRequisition(route.params.id, data) }
    else { await createRequisition(data) }
    closeToast()
    showToast(isEdit.value ? '保存成功' : '新增成功')
    router.back()
  } catch (e) {
    closeToast()
    showToast(e?.response?.data?.message || '操作失败')
  } finally { submitting.value = false }
}

onMounted(async () => {
  const today = new Date()
  const y = String(today.getFullYear()), m = String(today.getMonth() + 1).padStart(2, '0'), d = String(today.getDate()).padStart(2, '0')
  form.value.requisition_date = `${y}-${m}-${d}`
  dateValue.value = [y, m, d]
  if (route.params.id) {
    isEdit.value = true
    try {
      const res = await getRequisitionDetail(route.params.id)
      const item = res.data
      form.value.requisition_date = item.requisition_date || ''
      form.value.warehouse = item.warehouse || '默认仓库'
      form.value.remark = item.remark || ''
      form.value.items = (item.items || []).map(i => ({
        material_name: i.material_name || '', spec: i.spec || '', quantity: i.quantity != null ? String(i.quantity) : '1',
        unit: i.unit || '件', remark: i.remark || '',
      }))
      if (item.requisition_date) { const p = item.requisition_date.split('-'); if (p.length === 3) dateValue.value = p }
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
