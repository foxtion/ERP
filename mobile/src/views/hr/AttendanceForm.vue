<template>
  <div class="page">
    <van-nav-bar title="考勤记录" fixed placeholder left-arrow @click-left="onClickLeft" />
    <div class="form-content">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.employee_name"
            is-link
            readonly
            required
            label="员工"
            placeholder="请选择员工"
            :rules="[{ required: true, message: '请选择员工' }]"
            @click="showEmployeePicker = true"
          />
          <van-field
            v-model="form.date"
            is-link
            readonly
            required
            label="日期"
            placeholder="请选择日期"
            :rules="[{ required: true, message: '请选择日期' }]"
            @click="showDatePicker = true"
          />
          <van-field
            v-model="form.check_in"
            is-link
            readonly
            label="签到时间"
            placeholder="请选择签到时间"
            @click="openTimePicker('check_in')"
          />
          <van-field
            v-model="form.check_out"
            is-link
            readonly
            label="签退时间"
            placeholder="请选择签退时间"
            @click="openTimePicker('check_out')"
          />
          <van-field
            v-model="form.status"
            is-link
            readonly
            required
            label="考勤状态"
            placeholder="请选择状态"
            :rules="[{ required: true, message: '请选择状态' }]"
            @click="showStatusPicker = true"
          />
          <van-field
            v-model="form.remark"
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

    <!-- 员工选择 -->
    <van-popup v-model:show="showEmployeePicker" round position="bottom">
      <van-picker
        :columns="employeeColumns"
        @cancel="showEmployeePicker = false"
        @confirm="onEmployeeConfirm"
      />
    </van-popup>

    <!-- 日期选择 -->
    <van-popup v-model:show="showDatePicker" round position="bottom">
      <van-date-picker
        v-model="datePickerValue"
        title="选择日期"
        @cancel="showDatePicker = false"
        @confirm="onDateConfirm"
      />
    </van-popup>

    <!-- 时间选择 -->
    <van-popup v-model:show="showTimePicker" round position="bottom">
      <van-time-picker
        v-model="timePickerValue"
        title="选择时间"
        @cancel="showTimePicker = false"
        @confirm="onTimeConfirm"
      />
    </van-popup>

    <!-- 状态选择 -->
    <van-popup v-model:show="showStatusPicker" round position="bottom">
      <van-picker
        :columns="statusColumns"
        @cancel="showStatusPicker = false"
        @confirm="onStatusConfirm"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import { createAttendance, updateAttendance, getAttendanceDetail } from '@/api/hr'
import { getEmployeeOptions } from '@/api/hr'

const route = useRoute()
const router = useRouter()

const isEdit = ref(false)
const submitting = ref(false)
const recordId = ref(null)

const form = ref({
  employee: '',
  employee_name: '',
  date: '',
  check_in: '',
  check_out: '',
  status: '',
  remark: '',
})

const showEmployeePicker = ref(false)
const showDatePicker = ref(false)
const showTimePicker = ref(false)
const showStatusPicker = ref(false)

const datePickerValue = ref(['', '', ''])
const timePickerValue = ref(['09', '00'])
const currentTimeField = ref('')

const employeeColumns = ref([])

const statusColumns = [
  { text: '正常', value: 'normal' },
  { text: '迟到', value: 'late' },
  { text: '早退', value: 'early' },
  { text: '缺勤', value: 'absent' },
  { text: '请假', value: 'leave' },
]

onMounted(async () => {
  const id = route.query.id
  if (id) {
    isEdit.value = true
    recordId.value = id
    await loadDetail(id)
  } else {
    // 默认今天
    const today = new Date()
    form.value.date = formatDate(today)
    datePickerValue.value = [String(today.getFullYear()), String(today.getMonth() + 1).padStart(2, '0'), String(today.getDate()).padStart(2, '0')]
  }

  // 加载员工选项
  try {
    const res = await getEmployeeOptions()
    const list = res.data || res || []
    employeeColumns.value = list.map(item => ({ text: item.name || item.label || item, value: item.id || item.value || item }))
  } catch (e) {
    console.error('加载员工列表失败', e)
  }
})

async function loadDetail(id) {
  try {
    const res = await getAttendanceDetail(id)
    const item = res.data
    if (item) {
      form.value = {
        employee: item.employee || '',
        employee_name: item.employee_name || item.employee || '',
        date: item.date || '',
        check_in: item.check_in || '',
        check_out: item.check_out || '',
        status: item.status || '',
        remark: item.remark || '',
      }
      if (item.date) {
        const [y, m, d] = item.date.split('-')
        datePickerValue.value = [y, m, d]
      }
    }
  } catch (e) {
    showToast('加载详情失败')
  }
}

function onClickLeft() {
  router.back()
}

function onEmployeeConfirm({ selectedOptions }) {
  form.value.employee = selectedOptions[0].value
  form.value.employee_name = selectedOptions[0].text
  showEmployeePicker.value = false
}

function onDateConfirm({ selectedValues }) {
  form.value.date = selectedValues.join('-')
  showDatePicker.value = false
}

function openTimePicker(field) {
  currentTimeField.value = field
  const val = form.value[field]
  if (val) {
    const [h, m] = val.split(':')
    timePickerValue.value = [h || '09', m || '00']
  } else {
    timePickerValue.value = ['09', '00']
  }
  showTimePicker.value = true
}

function onTimeConfirm({ selectedValues }) {
  form.value[currentTimeField.value] = selectedValues.join(':')
  showTimePicker.value = false
}

function onStatusConfirm({ selectedOptions }) {
  form.value.status = selectedOptions[0].value
  showStatusPicker.value = false
}

function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

async function onSubmit() {
  submitting.value = true
  try {
    const data = { ...form.value }
    delete data.employee_name

    if (isEdit.value) {
      await updateAttendance(recordId.value, data)
      showToast('修改成功')
    } else {
      await createAttendance(data)
      showToast('添加成功')
    }
    router.back()
  } catch (e) {
    showToast(e.response?.data?.detail || e.message || '操作失败')
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
