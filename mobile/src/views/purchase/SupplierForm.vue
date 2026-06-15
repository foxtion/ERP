<template>
  <div class="page">
    <van-nav-bar :title="isEdit ? '编辑供应商' : '新增供应商'" fixed placeholder left-arrow @click-left="onClickLeft" />
    <div class="form-content">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.code"
            required
            label="供应商编码"
            placeholder="请输入供应商编码"
            :rules="[{ required: true, message: '请输入供应商编码' }]"
          />
          <van-field
            v-model="form.name"
            required
            label="供应商名称"
            placeholder="请输入供应商名称"
            :rules="[{ required: true, message: '请输入供应商名称' }]"
          />
          <van-field
            v-model="form.contact"
            label="联系人"
            placeholder="请输入联系人"
          />
          <van-field
            v-model="form.phone"
            label="联系电话"
            placeholder="请输入联系电话"
          />
          <van-field
            v-model="form.address"
            label="地址"
            placeholder="请输入地址"
          />
          <van-field
            v-model="form.status"
            is-link
            readonly
            label="状态"
            placeholder="请选择状态"
            @click="showStatusPicker = true"
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

        <div class="submit-btn">
          <van-button round block type="primary" native-type="submit" :loading="submitting">
            {{ isEdit ? '保存' : '提交' }}
          </van-button>
        </div>
      </van-form>
    </div>

    <van-popup v-model:show="showStatusPicker" round position="bottom">
      <van-picker :columns="statusColumns" @cancel="showStatusPicker = false" @confirm="onStatusConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { createSupplier, updateSupplier, getSupplierDetail } from '@/api/purchase'

const route = useRoute()
const router = useRouter()

const isEdit = ref(false)
const submitting = ref(false)
const supplierId = ref(null)

const form = ref({
  code: '',
  name: '',
  contact: '',
  phone: '',
  address: '',
  status: '启用',
  is_active: true,
  remark: '',
})

const showStatusPicker = ref(false)
const statusColumns = [
  { text: '启用', value: true },
  { text: '禁用', value: false },
]

onMounted(async () => {
  const id = route.params.id || route.query.id
  if (id) {
    isEdit.value = true
    supplierId.value = id
    await loadDetail(id)
  }
})

async function loadDetail(id) {
  try {
    const res = await getSupplierDetail(id)
    const item = res.data
    if (item) {
      form.value = {
        code: item.code || '',
        name: item.name || '',
        contact: item.contact || '',
        phone: item.phone || '',
        address: item.address || '',
        status: item.is_active !== false ? '启用' : '禁用',
        is_active: item.is_active !== false,
        remark: item.remark || '',
      }
    }
  } catch (e) {
    showToast('加载详情失败')
  }
}

function onClickLeft() {
  router.back()
}

function onStatusConfirm({ selectedOptions }) {
  form.value.is_active = selectedOptions[0].value
  form.value.status = selectedOptions[0].text
  showStatusPicker.value = false
}

async function onSubmit() {
  submitting.value = true
  try {
    const data = { ...form.value }
    delete data.status
    if (isEdit.value) {
      await updateSupplier(supplierId.value, data)
      showToast('修改成功')
    } else {
      await createSupplier(data)
      showToast('添加成功')
    }
    router.back()
  } catch (e) {
    showFailToast(e?.response?.data?.message || e?.response?.data?.detail || e.message || '操作失败')
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
.submit-btn {
  margin: 24px 16px;
}
</style>
