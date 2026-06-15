<template>
  <div class="page">
    <van-nav-bar :title="isEdit ? '编辑客户' : '新增客户'" fixed placeholder left-arrow @click-left="onClickLeft" />
    <div class="form-content">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.code"
            required
            label="客户编码"
            placeholder="请输入客户编码"
            :rules="[{ required: true, message: '请输入客户编码' }]"
          />
          <van-field
            v-model="form.name"
            required
            label="客户名称"
            placeholder="请输入客户名称"
            :rules="[{ required: true, message: '请输入客户名称' }]"
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
            v-model="form.email"
            label="邮箱"
            placeholder="请输入邮箱"
          />
          <van-field
            v-model="form.industry"
            label="所属行业"
            placeholder="请输入所属行业"
          />
          <van-field
            v-model="form.level"
            is-link
            readonly
            label="客户等级"
            placeholder="请选择客户等级"
            @click="showLevelPicker = true"
          />
          <van-field
            v-model.number="form.credit_limit"
            type="number"
            label="信用额度"
            placeholder="请输入信用额度"
          />
          <van-field
            v-model="form.tax_no"
            label="统一社会信用代码"
            placeholder="请输入统一社会信用代码"
          />
          <van-field
            v-model="form.bank_info"
            label="银行信息"
            placeholder="请输入银行信息"
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

    <van-popup v-model:show="showLevelPicker" round position="bottom">
      <van-picker :columns="levelColumns" @cancel="showLevelPicker = false" @confirm="onLevelConfirm" />
    </van-popup>

    <van-popup v-model:show="showStatusPicker" round position="bottom">
      <van-picker :columns="statusColumns" @cancel="showStatusPicker = false" @confirm="onStatusConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { createCustomer, updateCustomer, getCustomerDetail } from '@/api/sales'

const route = useRoute()
const router = useRouter()

const isEdit = ref(false)
const submitting = ref(false)
const customerId = ref(null)

const form = ref({
  code: '',
  name: '',
  contact: '',
  phone: '',
  email: '',
  industry: '',
  level: 'C',
  credit_limit: 0,
  tax_no: '',
  bank_info: '',
  address: '',
  status: '启用',
  is_active: true,
  remark: '',
})

const showLevelPicker = ref(false)
const showStatusPicker = ref(false)

const levelColumns = [
  { text: 'A级-VIP', value: 'A' },
  { text: 'B级-重要', value: 'B' },
  { text: 'C级-普通', value: 'C' },
  { text: 'D级-潜在', value: 'D' },
]

const statusColumns = [
  { text: '启用', value: true },
  { text: '禁用', value: false },
]

onMounted(async () => {
  const id = route.query.id
  if (id) {
    isEdit.value = true
    customerId.value = id
    await loadDetail(id)
  }
})

async function loadDetail(id) {
  try {
    const res = await getCustomerDetail(id)
    const item = res.data
    if (item) {
      form.value = {
        code: item.code || '',
        name: item.name || '',
        contact: item.contact || '',
        phone: item.phone || '',
        email: item.email || '',
        industry: item.industry || '',
        level: item.level || 'C',
        credit_limit: item.credit_limit || 0,
        tax_no: item.tax_no || '',
        bank_info: item.bank_info || '',
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

function onLevelConfirm({ selectedOptions }) {
  form.value.level = selectedOptions[0].value
  showLevelPicker.value = false
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
      await updateCustomer(customerId.value, data)
      showToast('修改成功')
    } else {
      await createCustomer(data)
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
