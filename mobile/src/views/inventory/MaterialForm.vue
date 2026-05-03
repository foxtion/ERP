<template>
  <div class="form-page">
    <van-form @submit="onSubmit" class="form-content">
      <van-cell-group inset>
        <van-field
          v-model="form.code"
          name="code"
          label="物料编码"
          placeholder="请输入物料编码"
          :rules="[{ required: true, message: '请输入物料编码' }]"
        />
        <van-field
          v-model="form.name"
          name="name"
          label="物料名称"
          placeholder="请输入物料名称"
          :rules="[{ required: true, message: '请输入物料名称' }]"
        />
        <van-field
          v-model="form.spec"
          name="spec"
          label="规格型号"
          placeholder="请输入规格型号（可选）"
        />
        <van-field
          v-model="form.category"
          name="category"
          label="分类"
          placeholder="请输入分类（可选）"
        />
        <van-field
          v-model="form.unit"
          name="unit"
          label="单位"
          placeholder="请输入单位"
        />
        <van-field
          v-model="form.barcode"
          name="barcode"
          label="条码"
          placeholder="请输入条码（可选）"
        />
        <van-field
          v-model="form.qty"
          name="qty"
          label="库存数量"
          type="number"
          placeholder="请输入库存数量"
        />
        <van-field
          v-model="form.warning_threshold"
          name="warning_threshold"
          label="预警阈值"
          type="number"
          placeholder="请输入预警阈值"
        />
        <van-field name="status" label="状态">
          <template #input>
            <van-switch v-model="statusActive" size="20" />
          </template>
        </van-field>
        <van-field
          v-model="form.large_location"
          name="large_location"
          label="大库位"
          placeholder="请输入大库位编码（可选）"
        />
        <van-field
          v-model="form.small_location"
          name="small_location"
          label="小库位"
          placeholder="请输入小库位编码（可选）"
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createMaterial, updateMaterial, getMaterialDetail } from '@/api/inventory'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const submitting = ref(false)

const statusActive = ref(true)

const form = ref({
  code: '',
  name: '',
  spec: '',
  category: '',
  unit: '件',
  barcode: '',
  qty: '0',
  warning_threshold: '50',
  status: 'active',
  large_location: '',
  small_location: '',
  remark: '',
})

const onSubmit = async () => {
  submitting.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })
  try {
    const data = {
      code: form.value.code,
      name: form.value.name,
      spec: form.value.spec || null,
      category: form.value.category || null,
      unit: form.value.unit || '件',
      barcode: form.value.barcode || null,
      qty: form.value.qty !== '' ? parseFloat(form.value.qty) : 0,
      warning_threshold: form.value.warning_threshold !== '' ? parseFloat(form.value.warning_threshold) : 50,
      status: statusActive.value ? 'active' : 'disabled',
      large_location: form.value.large_location || null,
      small_location: form.value.small_location || null,
      remark: form.value.remark || null,
    }
    if (isEdit.value) {
      await updateMaterial(route.params.id, data)
    } else {
      await createMaterial(data)
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
  if (route.params.id) {
    isEdit.value = true
    try {
      const res = await getMaterialDetail(route.params.id)
      const item = res.data
      form.value.code = item.code || ''
      form.value.name = item.name || ''
      form.value.spec = item.spec || ''
      form.value.category = item.category || ''
      form.value.unit = item.unit || '件'
      form.value.barcode = item.barcode || ''
      form.value.qty = item.qty != null ? String(item.qty) : '0'
      form.value.warning_threshold = item.warning_threshold != null ? String(item.warning_threshold) : '50'
      statusActive.value = item.status === 'active'
      form.value.large_location = item.large_location || ''
      form.value.small_location = item.small_location || ''
      form.value.remark = item.remark || ''
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
.form-actions {
  margin: 20px 16px;
}
</style>
