<template>
  <div class="form-page">
    <van-form @submit="onSubmit" class="form-content">
      <van-cell-group inset>
        <van-field
          v-model="form.warehouse"
          name="warehouse"
          label="所属仓库"
          placeholder="请选择所属仓库"
          readonly
          is-link
          @click="showWarehousePicker = true"
          :rules="[{ required: true, message: '请选择所属仓库' }]"
        />
        <van-field
          v-model="form.location_code"
          name="location_code"
          label="库位编码"
          placeholder="请输入库位编码"
          :rules="[{ required: true, message: '请输入库位编码' }]"
        />
        <van-field
          v-model="form.barcode"
          name="barcode"
          label="条码"
          placeholder="请输入条码（可选）"
        />
        <van-field
          name="size"
          label="库位大小"
          :rules="[{ required: true, message: '请选择库位大小' }]"
        >
          <template #input>
            <van-radio-group v-model="form.size" direction="horizontal">
              <van-radio name="小">小</van-radio>
              <van-radio name="中">中</van-radio>
              <van-radio name="大">大</van-radio>
            </van-radio-group>
          </template>
        </van-field>
        <van-field name="is_empty" label="是否空位">
          <template #input>
            <van-switch v-model="form.is_empty" size="20" />
          </template>
        </van-field>
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

    <van-popup v-model:show="showWarehousePicker" round position="bottom">
      <van-picker
        :columns="warehouseOptions"
        @confirm="onWarehouseConfirm"
        @cancel="showWarehousePicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createLocation, updateLocation, getLocationDetail } from '@/api/inventory'
import { getWarehouseList } from '@/api/inventory'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const submitting = ref(false)
const showWarehousePicker = ref(false)
const warehouseOptions = ref([])

const form = ref({
  warehouse: '',
  warehouse_id: null,
  location_code: '',
  barcode: '',
  size: '小',
  is_empty: true,
  remark: '',
})

const loadWarehouses = async () => {
  try {
    const res = await getWarehouseList({ size: 999 })
    const list = res.data?.list || res.data || []
    warehouseOptions.value = list.map((item) => ({
      text: item.name,
      value: item.id,
    }))
  } catch (e) {
    console.error('加载仓库失败', e)
  }
}

const onWarehouseConfirm = ({ selectedOptions }) => {
  const option = selectedOptions[0]
  form.value.warehouse = option.text
  form.value.warehouse_id = option.value
  showWarehousePicker.value = false
}

const onSubmit = async () => {
  submitting.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })
  try {
    const data = {
      warehouse: form.value.warehouse_id,
      location_code: form.value.location_code,
      barcode: form.value.barcode,
      size: form.value.size,
      is_empty: form.value.is_empty,
      remark: form.value.remark,
    }
    if (isEdit.value) {
      await updateLocation(route.params.id, data)
    } else {
      await createLocation(data)
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
  await loadWarehouses()
  if (route.params.id) {
    isEdit.value = true
    try {
      const res = await getLocationDetail(route.params.id)
      const item = res.data
      form.value.warehouse_id = item.warehouse
      form.value.warehouse = item.warehouse_name
      form.value.location_code = item.location_code
      form.value.barcode = item.barcode || ''
      form.value.size = item.size
      form.value.is_empty = item.is_empty
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
