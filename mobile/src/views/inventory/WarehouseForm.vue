<template>
  <div class="form-page">
    <van-form @submit="onSubmit" class="form-content">
      <van-cell-group inset>
        <van-field
          v-model="form.code"
          name="code"
          label="仓库编码"
          placeholder="请输入仓库编码"
          :rules="[{ required: true, message: '请输入仓库编码' }]"
        />
        <van-field
          v-model="form.name"
          name="name"
          label="仓库名称"
          placeholder="请输入仓库名称"
          :rules="[{ required: true, message: '请输入仓库名称' }]"
        />
        <van-field
          v-model="form.location"
          name="location"
          label="所在位置"
          placeholder="请输入所在位置（可选）"
        />
        <van-field
          v-model="form.manager"
          name="manager"
          label="负责人"
          placeholder="请输入负责人（可选）"
        />
        <van-field name="is_active" label="是否启用">
          <template #input>
            <van-switch v-model="form.is_active" size="20" />
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createWarehouse, updateWarehouse, getWarehouseDetail } from '@/api/inventory'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const submitting = ref(false)

const form = ref({
  code: '',
  name: '',
  location: '',
  manager: '',
  is_active: true,
  remark: '',
})

const onSubmit = async () => {
  submitting.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })
  try {
    const data = {
      code: form.value.code,
      name: form.value.name,
      location: form.value.location || null,
      manager: form.value.manager || null,
      is_active: form.value.is_active,
      remark: form.value.remark || null,
    }
    if (isEdit.value) {
      await updateWarehouse(route.params.id, data)
    } else {
      await createWarehouse(data)
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
      const res = await getWarehouseDetail(route.params.id)
      const item = res.data
      form.value.code = item.code || ''
      form.value.name = item.name || ''
      form.value.location = item.location || ''
      form.value.manager = item.manager || ''
      form.value.is_active = item.is_active !== false
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
