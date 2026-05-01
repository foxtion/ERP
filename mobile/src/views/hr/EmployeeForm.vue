<template>
  <div class="page">
    <van-nav-bar :title="isEdit ? '编辑员工' : '新增员工'" fixed placeholder left-arrow @click-left="onClickLeft" />
    <div class="form-content">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.employee_no"
            required
            label="工号"
            placeholder="请输入工号"
            :rules="[{ required: true, message: '请输入工号' }]"
          >
            <template #button>
              <van-button size="small" type="primary" plain @click="generateNo">自动生成</van-button>
            </template>
          </van-field>
          <van-field
            v-model="form.name"
            required
            label="姓名"
            placeholder="请输入姓名"
            :rules="[{ required: true, message: '请输入姓名' }]"
          />
          <van-field
            v-model="form.gender"
            is-link
            readonly
            label="性别"
            placeholder="请选择性别"
            @click="showGenderPicker = true"
          />
          <van-field
            v-model="form.phone"
            label="手机号"
            placeholder="请输入手机号"
          />
          <van-field
            v-model="form.email"
            label="邮箱"
            placeholder="请输入邮箱"
          />
          <van-field
            v-model="form.department_name"
            is-link
            readonly
            label="部门"
            placeholder="请选择部门"
            @click="showDeptPicker = true"
          />
          <van-field
            v-model="form.position_name"
            is-link
            readonly
            label="职位"
            placeholder="请选择职位"
            @click="showPositionPicker = true"
          />
          <van-field
            v-model="form.education"
            is-link
            readonly
            label="学历"
            placeholder="请选择学历"
            @click="showEducationPicker = true"
          />
          <van-field
            v-model="form.entry_date"
            is-link
            readonly
            label="入职日期"
            placeholder="请选择入职日期"
            @click="showEntryDatePicker = true"
          />
          <van-field
            v-model="form.probation_end_date"
            is-link
            readonly
            label="试用期结束日"
            placeholder="请选择试用期结束日"
            @click="showProbationDatePicker = true"
          />
          <van-field
            v-model="form.contract_end_date"
            is-link
            readonly
            label="合同到期日"
            placeholder="请选择合同到期日"
            @click="showContractDatePicker = true"
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
            v-model="form.address"
            label="地址"
            placeholder="请输入地址"
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

    <!-- 性别选择 -->
    <van-popup v-model:show="showGenderPicker" round position="bottom">
      <van-picker :columns="genderColumns" @cancel="showGenderPicker = false" @confirm="onGenderConfirm" />
    </van-popup>

    <!-- 部门选择 -->
    <van-popup v-model:show="showDeptPicker" round position="bottom">
      <van-picker :columns="deptColumns" @cancel="showDeptPicker = false" @confirm="onDeptConfirm" />
    </van-popup>

    <!-- 职位选择 -->
    <van-popup v-model:show="showPositionPicker" round position="bottom">
      <van-picker :columns="positionColumns" @cancel="showPositionPicker = false" @confirm="onPositionConfirm" />
    </van-popup>

    <!-- 学历选择 -->
    <van-popup v-model:show="showEducationPicker" round position="bottom">
      <van-picker :columns="educationColumns" @cancel="showEducationPicker = false" @confirm="onEducationConfirm" />
    </van-popup>

    <!-- 状态选择 -->
    <van-popup v-model:show="showStatusPicker" round position="bottom">
      <van-picker :columns="statusColumns" @cancel="showStatusPicker = false" @confirm="onStatusConfirm" />
    </van-popup>

    <!-- 日期选择 -->
    <van-popup v-model:show="showEntryDatePicker" round position="bottom">
      <van-date-picker v-model="entryDateValue" title="选择入职日期" @cancel="showEntryDatePicker = false" @confirm="onEntryDateConfirm" />
    </van-popup>
    <van-popup v-model:show="showProbationDatePicker" round position="bottom">
      <van-date-picker v-model="probationDateValue" title="选择试用期结束日" @cancel="showProbationDatePicker = false" @confirm="onProbationDateConfirm" />
    </van-popup>
    <van-popup v-model:show="showContractDatePicker" round position="bottom">
      <van-date-picker v-model="contractDateValue" title="选择合同到期日" @cancel="showContractDatePicker = false" @confirm="onContractDateConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { createEmployee, updateEmployee, getEmployeeDetail, generateEmployeeNo } from '@/api/hr'
import { getDeptTree } from '@/api/system'
import { getPositionsByDepartment } from '@/api/hr'

const route = useRoute()
const router = useRouter()

const isEdit = ref(false)
const submitting = ref(false)
const employeeId = ref(null)

const form = ref({
  employee_no: '',
  name: '',
  gender: 'male',
  phone: '',
  email: '',
  department: '',
  department_name: '',
  position: '',
  position_name: '',
  education: '',
  entry_date: '',
  probation_end_date: '',
  contract_end_date: '',
  status: 'active',
  address: '',
  remark: '',
})

const showGenderPicker = ref(false)
const showDeptPicker = ref(false)
const showPositionPicker = ref(false)
const showEducationPicker = ref(false)
const showStatusPicker = ref(false)
const showEntryDatePicker = ref(false)
const showProbationDatePicker = ref(false)
const showContractDatePicker = ref(false)

const entryDateValue = ref(['', '', ''])
const probationDateValue = ref(['', '', ''])
const contractDateValue = ref(['', '', ''])

const genderColumns = [
  { text: '男', value: 'male' },
  { text: '女', value: 'female' },
]

const educationColumns = [
  { text: '高中', value: 'high_school' },
  { text: '大专', value: 'college' },
  { text: '本科', value: 'bachelor' },
  { text: '硕士', value: 'master' },
  { text: '博士', value: 'doctor' },
]

const statusColumns = [
  { text: '在职', value: 'active' },
  { text: '试用期', value: 'probation' },
  { text: '离职', value: 'resigned' },
]

const deptColumns = ref([])
const positionColumns = ref([])

onMounted(async () => {
  const id = route.query.id
  if (id) {
    isEdit.value = true
    employeeId.value = id
    await loadDetail(id)
  }

  try {
    const res = await getDeptTree()
    const list = res.data || []
    deptColumns.value = flattenDept(list)
  } catch (e) {
    console.error('加载部门失败', e)
  }
})

function flattenDept(list, prefix = '') {
  const result = []
  for (const item of list) {
    result.push({ text: prefix + item.name, value: item.id })
    if (item.children && item.children.length > 0) {
      result.push(...flattenDept(item.children, prefix + '  '))
    }
  }
  return result
}

async function loadPositions(deptId) {
  if (!deptId) {
    positionColumns.value = []
    return
  }
  try {
    const res = await getPositionsByDepartment(deptId)
    const list = res.data || []
    positionColumns.value = list.map(item => ({ text: item.name || item.label || item, value: item.id || item.value || item }))
  } catch (e) {
    console.error('加载职位失败', e)
  }
}

async function loadDetail(id) {
  try {
    const res = await getEmployeeDetail(id)
    const item = res.data
    if (item) {
      form.value = {
        employee_no: item.employee_no || '',
        name: item.name || '',
        gender: item.gender || 'male',
        phone: item.phone || '',
        email: item.email || '',
        department: item.department || '',
        department_name: item.department_name || '',
        position: item.position || '',
        position_name: item.position_name || '',
        education: item.education || '',
        entry_date: item.entry_date || '',
        probation_end_date: item.probation_end_date || '',
        contract_end_date: item.contract_end_date || '',
        status: item.status || 'active',
        address: item.address || '',
        remark: item.remark || '',
      }
      if (item.department) {
        await loadPositions(item.department)
      }
      setDateValues()
    }
  } catch (e) {
    showToast('加载详情失败')
  }
}

function setDateValues() {
  if (form.value.entry_date) {
    const [y, m, d] = form.value.entry_date.split('-')
    entryDateValue.value = [y, m, d]
  }
  if (form.value.probation_end_date) {
    const [y, m, d] = form.value.probation_end_date.split('-')
    probationDateValue.value = [y, m, d]
  }
  if (form.value.contract_end_date) {
    const [y, m, d] = form.value.contract_end_date.split('-')
    contractDateValue.value = [y, m, d]
  }
}

function onClickLeft() {
  router.back()
}

async function generateNo() {
  try {
    const res = await generateEmployeeNo()
    form.value.employee_no = res.data?.employee_no || res.data || ''
  } catch (e) {
    showToast('生成工号失败')
  }
}

function onGenderConfirm({ selectedOptions }) {
  form.value.gender = selectedOptions[0].value
  showGenderPicker.value = false
}

function onDeptConfirm({ selectedOptions }) {
  form.value.department = selectedOptions[0].value
  form.value.department_name = selectedOptions[0].text.trim()
  form.value.position = ''
  form.value.position_name = ''
  showDeptPicker.value = false
  loadPositions(selectedOptions[0].value)
}

function onPositionConfirm({ selectedOptions }) {
  form.value.position = selectedOptions[0].value
  form.value.position_name = selectedOptions[0].text
  showPositionPicker.value = false
}

function onEducationConfirm({ selectedOptions }) {
  form.value.education = selectedOptions[0].value
  showEducationPicker.value = false
}

function onStatusConfirm({ selectedOptions }) {
  form.value.status = selectedOptions[0].value
  showStatusPicker.value = false
}

function onEntryDateConfirm({ selectedValues }) {
  form.value.entry_date = selectedValues.join('-')
  showEntryDatePicker.value = false
}

function onProbationDateConfirm({ selectedValues }) {
  form.value.probation_end_date = selectedValues.join('-')
  showProbationDatePicker.value = false
}

function onContractDateConfirm({ selectedValues }) {
  form.value.contract_end_date = selectedValues.join('-')
  showContractDatePicker.value = false
}

async function onSubmit() {
  submitting.value = true
  try {
    const data = { ...form.value }
    delete data.department_name
    delete data.position_name
    if (isEdit.value) {
      await updateEmployee(employeeId.value, data)
      showToast('修改成功')
    } else {
      await createEmployee(data)
      showToast('添加成功')
    }
    router.back()
  } catch (e) {
    showFailToast(e?.response?.data?.message || e.message || '操作失败')
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
