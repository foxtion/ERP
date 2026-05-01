<template>
  <div class="page">
    <van-nav-bar :title="isEdit ? '编辑生产计划' : '新增生产计划'" fixed placeholder left-arrow @click-left="onClickLeft" />
    <div class="form-content">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.plan_no"
            label="计划编号"
            placeholder="留空将自动生成"
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
            v-model="form.product_name"
            required
            label="产品名称"
            placeholder="请输入产品名称"
            :rules="[{ required: true, message: '请输入产品名称' }]"
          />
          <van-field
            v-model="form.product_code"
            required
            label="产品编码"
            placeholder="请输入产品编码"
            :rules="[{ required: true, message: '请输入产品编码' }]"
          />
          <van-field
            v-model="form.quantity"
            required
            label="计划数量"
            placeholder="请输入计划数量"
            type="number"
            :rules="[{ required: true, message: '请输入计划数量' }]"
          />
          <van-field
            v-model="bomName"
            is-link
            readonly
            label="关联BOM"
            placeholder="请选择BOM（可选）"
            @click="showBomPicker = true"
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

    <!-- 日期选择 -->
    <van-popup v-model:show="showDatePicker" round position="bottom">
      <van-date-picker
        v-model="dateValue"
        title="选择计划日期"
        :min-date="minDate"
        @cancel="showDatePicker = false"
        @confirm="onDateConfirm"
      />
    </van-popup>

    <!-- BOM 选择 -->
    <van-popup v-model:show="showBomPicker" round position="bottom">
      <van-picker
        :columns="bomColumns"
        @cancel="showBomPicker = false"
        @confirm="onBomConfirm"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { createPlan, updatePlan, getPlanDetail } from '@/api/production'
import { getBomOptions } from '@/api/production'

const route = useRoute()
const router = useRouter()

const isEdit = ref(false)
const submitting = ref(false)
const planId = ref(null)

const form = ref({
  plan_no: '',
  plan_date: '',
  product_name: '',
  product_code: '',
  quantity: '',
  bom: null,
  remark: '',
})

const bomName = ref('')
const showDatePicker = ref(false)
const showBomPicker = ref(false)
const dateValue = ref(['', '', ''])
const bomColumns = ref([])
const minDate = new Date(2020, 0, 1)

onMounted(async () => {
  const id = route.params.id || route.query.id
  if (id) {
    isEdit.value = true
    planId.value = id
    await loadDetail(id)
  } else {
    // 默认设置为今天
    const today = new Date()
    const y = String(today.getFullYear())
    const m = String(today.getMonth() + 1).padStart(2, '0')
    const d = String(today.getDate()).padStart(2, '0')
    form.value.plan_date = `${y}-${m}-${d}`
    dateValue.value = [y, m, d]
  }

  try {
    const res = await getBomOptions()
    const list = res.data || []
    bomColumns.value = [
      { text: '不选择', value: null },
      ...list.map(item => ({ text: `${item.product_name} (${item.product_code})`, value: item.id })),
    ]
  } catch (e) {
    console.error('加载BOM选项失败', e)
  }
})

async function loadDetail(id) {
  try {
    const res = await getPlanDetail(id)
    const item = res.data
    if (item) {
      form.value = {
        plan_no: item.plan_no || '',
        plan_date: item.plan_date || '',
        product_name: item.product_name || '',
        product_code: item.product_code || '',
        quantity: item.quantity != null ? String(item.quantity) : '',
        bom: item.bom || null,
        remark: item.remark || '',
      }
      if (item.bom_product_name) {
        bomName.value = item.bom_product_name
      } else if (item.bom) {
        // 异步查找BOM名称
        const bomItem = bomColumns.value.find(b => b.value === item.bom)
        if (bomItem) bomName.value = bomItem.text
      }
      if (item.plan_date) {
        const [y, m, d] = item.plan_date.split('-')
        dateValue.value = [y, m, d]
      }
    }
  } catch (e) {
    showToast('加载详情失败')
  }
}

function onClickLeft() {
  router.back()
}

function onDateConfirm({ selectedValues }) {
  form.value.plan_date = selectedValues.join('-')
  showDatePicker.value = false
}

function onBomConfirm({ selectedOptions }) {
  const opt = selectedOptions[0]
  form.value.bom = opt.value
  bomName.value = opt.text === '不选择' ? '' : opt.text
  showBomPicker.value = false
}

async function onSubmit() {
  submitting.value = true
  try {
    const data = { ...form.value }
    // 转换数量
    if (data.quantity) {
      data.quantity = parseFloat(data.quantity)
    }
    // plan_no 为空时后端自动生成
    if (!data.plan_no) {
      delete data.plan_no
    }
    // bom 为 null 时不传
    if (data.bom === null) {
      delete data.bom
    }
    if (isEdit.value) {
      await updatePlan(planId.value, data)
      showToast('修改成功')
    } else {
      await createPlan(data)
      showToast('创建成功')
    }
    router.back()
  } catch (e) {
    showFailToast(e?.response?.data?.message || e.message || '操作失败')
    // eslint-disable-next-line no-alert
    alert(e?.response?.data?.message || e.message || '操作失败')
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
