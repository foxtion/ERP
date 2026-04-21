<template>
  <div class="page-container">
    <el-card>
      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :span="4">
          <div class="stat-card bg-total">
            <div class="label">总人数</div>
            <div class="value">{{ stats.total || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card bg-active">
            <div class="label">在职</div>
            <div class="value">{{ stats.active || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card bg-probation">
            <div class="label">试用期</div>
            <div class="value">{{ stats.probation || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card bg-resigned">
            <div class="label">离职</div>
            <div class="value">{{ stats.resigned || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card bg-expiry">
            <div class="label">合同即将到期</div>
            <div class="value">{{ stats.contract_expiry || 0 }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 搜索栏 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="工号/姓名">
          <el-input v-model="searchForm.search" placeholder="工号/姓名/手机号" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="searchForm.department" placeholder="请输入部门" clearable style="width: 130px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 100px">
            <el-option label="在职" value="active" />
            <el-option label="试用期" value="probation" />
            <el-option label="离职" value="resigned" />
          </el-select>
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="searchForm.gender" placeholder="全部" clearable style="width: 90px">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
          </el-select>
        </el-form-item>
        <el-form-item label="入职日期">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="~"
            start-placeholder="开始"
            end-placeholder="结束"
            style="width: 220px"
          />
        </el-form-item>
        <el-form-item label="仅合同到期">
          <el-switch v-model="searchForm.contract_expiry" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar">
        <el-button v-permission="'hr:employee:add'" type="primary" @click="handleAdd">新增员工</el-button>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="employee_no" label="工号" min-width="130" />
        <el-table-column prop="name" label="姓名" min-width="100" />
        <el-table-column prop="gender" label="性别" width="70" align="center">
          <template #default="{ row }">
            {{ row.gender === 'male' ? '男' : '女' }}
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="70" align="center">
          <template #default="{ row }">
            <span v-if="row.age">{{ row.age }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" min-width="120" />
        <el-table-column prop="position" label="职位" min-width="120" />
        <el-table-column prop="phone" label="手机号" min-width="120" />
        <el-table-column prop="entry_date" label="入职日期" width="110" />
        <el-table-column prop="contract_end_date" label="合同到期" width="110">
          <template #default="{ row }">
            <span :class="{ 'text-danger': isContractExpiring(row) }">{{ row.contract_end_date || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="info" @click="handleView(row)">查看</el-button>
            <el-button v-permission="'hr:employee:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'probation'" v-permission="'hr:employee:edit'" link type="success" @click="handleConfirm(row)">转正</el-button>
            <el-button v-if="row.status !== 'resigned'" v-permission="'hr:employee:edit'" link type="warning" @click="handleResign(row)">离职</el-button>
            <el-button v-permission="'hr:employee:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.size"
        :total="total"
        layout="total, sizes, prev, pager, next"
        :page-sizes="[10, 20, 50]"
        class="pagination"
        @current-change="fetchData"
        @size-change="fetchData"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="750px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工号" prop="employee_no">
              <el-input v-model="form.employee_no" placeholder="请输入工号，留空自动生成">
                <template #append>
                  <el-button @click="generateNo">自动生成</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="钉钉用户ID">
          <el-input v-model="form.dingtalk_user_id" placeholder="请输入钉钉用户ID（用于考勤同步）" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-radio-group v-model="form.gender">
                <el-radio label="male">男</el-radio>
                <el-radio label="female">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="form.status">
                <el-radio label="active">在职</el-radio>
                <el-radio label="probation">试用期</el-radio>
                <el-radio label="resigned">离职</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号">
              <el-input v-model="form.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="身份证号">
              <el-input v-model="form.id_card" placeholder="请输入身份证号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期">
              <el-date-picker v-model="form.birth_date" type="date" value-format="YYYY-MM-DD" placeholder="选择出生日期" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="部门">
              <el-input v-model="form.department" placeholder="请输入部门" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职位">
              <el-input v-model="form.position" placeholder="请输入职位" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学历">
              <el-select v-model="form.education" placeholder="请选择学历" clearable style="width: 100%">
                <el-option label="高中" value="high_school" />
                <el-option label="大专" value="college" />
                <el-option label="本科" value="bachelor" />
                <el-option label="硕士" value="master" />
                <el-option label="博士" value="doctor" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="毕业院校">
              <el-input v-model="form.graduate_school" placeholder="请输入毕业院校" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入职日期">
              <el-date-picker v-model="form.entry_date" type="date" value-format="YYYY-MM-DD" placeholder="选择入职日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="试用期结束">
              <el-date-picker v-model="form.probation_end_date" type="date" value-format="YYYY-MM-DD" placeholder="选择试用期结束日" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同到期">
              <el-date-picker v-model="form.contract_end_date" type="date" value-format="YYYY-MM-DD" placeholder="选择合同到期日" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="离职日期">
              <el-date-picker v-model="form.resignation_date" type="date" value-format="YYYY-MM-DD" placeholder="选择离职日期" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开户行">
              <el-input v-model="form.bank_name" placeholder="请输入开户行" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工资卡号">
              <el-input v-model="form.bank_account" placeholder="请输入工资卡号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="紧急联系人">
              <el-input v-model="form.emergency_contact" placeholder="请输入紧急联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="紧急电话">
              <el-input v-model="form.emergency_phone" placeholder="请输入紧急联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="地址">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="员工详情" width="700px">
      <el-descriptions :column="2" border v-if="currentRow">
        <el-descriptions-item label="工号">{{ currentRow.employee_no }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ currentRow.name }}</el-descriptions-item>
        <el-descriptions-item label="钉钉用户ID">{{ currentRow.dingtalk_user_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ currentRow.gender === 'male' ? '男' : '女' }}</el-descriptions-item>
        <el-descriptions-item label="年龄">{{ currentRow.age || '-' }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ currentRow.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ currentRow.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="身份证号">{{ currentRow.id_card || '-' }}</el-descriptions-item>
        <el-descriptions-item label="出生日期">{{ currentRow.birth_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="部门">{{ currentRow.department || '-' }}</el-descriptions-item>
        <el-descriptions-item label="职位">{{ currentRow.position || '-' }}</el-descriptions-item>
        <el-descriptions-item label="学历">{{ educationText(currentRow.education) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="毕业院校">{{ currentRow.graduate_school || '-' }}</el-descriptions-item>
        <el-descriptions-item label="入职日期">{{ currentRow.entry_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="试用期结束">{{ currentRow.probation_end_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="合同到期">{{ currentRow.contract_end_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="离职日期">{{ currentRow.resignation_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开户行">{{ currentRow.bank_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="工资卡号">{{ currentRow.bank_account || '-' }}</el-descriptions-item>
        <el-descriptions-item label="紧急联系人">{{ currentRow.emergency_contact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="紧急电话">{{ currentRow.emergency_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(currentRow.status)">{{ statusText(currentRow.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="地址">{{ currentRow.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentRow.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getEmployeeList, createEmployee, updateEmployee, deleteEmployee,
  generateEmployeeNo, confirmEmployee, resignEmployee, getEmployeeStats
} from '@/api/hr'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = ref({ page: 1, size: 10 })
const stats = ref({})

const searchForm = reactive({
  search: '',
  department: '',
  status: '',
  gender: '',
  dateRange: [],
  contract_expiry: false,
})

const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)
const currentRow = ref(null)

const form = ref({
  employee_no: '', name: '', gender: 'male', phone: '', email: '', id_card: '', birth_date: '',
  department: '', position: '', education: '', graduate_school: '', entry_date: '',
  probation_end_date: '', contract_end_date: '', resignation_date: '',
  bank_name: '', bank_account: '', emergency_contact: '', emergency_phone: '',
  dingtalk_user_id: '', status: 'active', address: '', remark: ''
})

const rules = {
  employee_no: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
}

const statusText = (s) => ({ active: '在职', probation: '试用期', resigned: '离职' }[s] || s)
const statusType = (s) => ({ active: 'success', probation: 'warning', resigned: 'info' }[s] || '')
const educationText = (e) => ({ high_school: '高中', college: '大专', bachelor: '本科', master: '硕士', doctor: '博士' }[e] || e)

const isContractExpiring = (row) => {
  if (!row.contract_end_date || row.status === 'resigned') return false
  const end = new Date(row.contract_end_date)
  const today = new Date()
  const diff = Math.ceil((end - today) / (1000 * 60 * 60 * 24))
  return diff <= 30 && diff >= 0
}

const buildQuery = () => {
  const params = { ...query.value }
  if (searchForm.search) params.search = searchForm.search
  if (searchForm.department) params.department = searchForm.department
  if (searchForm.status) params.status = searchForm.status
  if (searchForm.gender) params.gender = searchForm.gender
  if (searchForm.dateRange && searchForm.dateRange.length === 2) {
    params.date_from = searchForm.dateRange[0]
    params.date_to = searchForm.dateRange[1]
  }
  if (searchForm.contract_expiry) params.contract_expiry = '1'
  return params
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getEmployeeList(buildQuery())
    tableData.value = res.data.list
    total.value = res.data.pagination.total
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  const res = await getEmployeeStats()
  stats.value = res.data
}

onMounted(() => {
  fetchData()
  fetchStats()
})

const handleSearch = () => {
  query.value.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.search = ''
  searchForm.department = ''
  searchForm.status = ''
  searchForm.gender = ''
  searchForm.dateRange = []
  searchForm.contract_expiry = false
  query.value.page = 1
  fetchData()
}

const generateNo = async () => {
  const res = await generateEmployeeNo()
  form.value.employee_no = res.data.employee_no
}

const resetForm = () => {
  form.value = {
    employee_no: '', name: '', gender: 'male', phone: '', email: '', id_card: '', birth_date: '',
    department: '', position: '', education: '', graduate_school: '', entry_date: '',
    probation_end_date: '', contract_end_date: '', resignation_date: '',
    bank_name: '', bank_account: '', emergency_contact: '', emergency_phone: '',
    status: 'active', address: '', remark: ''
  }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增员工'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑员工'
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form.value, row)
  dialogVisible.value = true
}

const handleView = (row) => {
  currentRow.value = row
  viewDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (isEdit.value) {
        await updateEmployee(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createEmployee(form.value)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      await fetchData()
      await fetchStats()
    } finally {
      submitLoading.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除员工 "${row.name}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteEmployee(row.id)
    ElMessage.success('删除成功')
    await fetchData()
    await fetchStats()
  })
}

const handleConfirm = (row) => {
  ElMessageBox.confirm(`确定将员工 "${row.name}" 转正吗？`, '提示', { type: 'warning' }).then(async () => {
    await confirmEmployee(row.id)
    ElMessage.success('转正成功')
    await fetchData()
    await fetchStats()
  })
}

const handleResign = (row) => {
  ElMessageBox.confirm(`确定将员工 "${row.name}" 标记为离职吗？`, '提示', { type: 'warning' }).then(async () => {
    await resignEmployee(row.id)
    ElMessage.success('离职操作成功')
    await fetchData()
    await fetchStats()
  })
}
</script>

<style scoped>
.page-container { padding: 20px; }
.stats-row { margin-bottom: 20px; }
.stat-card {
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  color: #fff;
}
.stat-card .label { font-size: 13px; margin-bottom: 8px; opacity: 0.9; }
.stat-card .value { font-size: 22px; font-weight: bold; }
.bg-total { background: linear-gradient(135deg, #409eff, #66b1ff); }
.bg-active { background: linear-gradient(135deg, #67c23a, #85ce61); }
.bg-probation { background: linear-gradient(135deg, #e6a23c, #ebb563); }
.bg-resigned { background: linear-gradient(135deg, #909399, #a6a9ad); }
.bg-expiry { background: linear-gradient(135deg, #f56c6c, #f78989); }
.search-form { margin-bottom: 15px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
.text-danger { color: #f56c6c; font-weight: bold; }
.text-muted { color: #909399; }
</style>
