<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'hr:attendance:add'" type="primary" @click="handleAdd">新增考勤</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="employee_no" label="工号" min-width="120" />
        <el-table-column prop="employee_name" label="姓名" min-width="100" />
        <el-table-column prop="date" label="考勤日期" min-width="120" />
        <el-table-column prop="check_in" label="上班" min-width="100" />
        <el-table-column prop="check_out" label="下班" min-width="100" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'hr:attendance:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'hr:attendance:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="员工" prop="employee">
          <el-select v-model="form.employee" filterable placeholder="请选择员工" style="width: 100%">
            <el-option v-for="e in employeeOptions" :key="e.id" :label="`${e.employee_no} - ${e.name}`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考勤日期" prop="date">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上班时间">
              <el-time-picker v-model="form.check_in" value-format="HH:mm:ss" placeholder="上班时间" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="下班时间">
              <el-time-picker v-model="form.check_out" value-format="HH:mm:ss" placeholder="下班时间" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="考勤状态">
          <el-radio-group v-model="form.status">
            <el-radio label="normal">正常</el-radio>
            <el-radio label="late">迟到</el-radio>
            <el-radio label="early">早退</el-radio>
            <el-radio label="absent">旷工</el-radio>
            <el-radio label="leave">请假</el-radio>
          </el-radio-group>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAttendanceList, createAttendance, updateAttendance, deleteAttendance } from '@/api/hr'
import { getEmployeeOptions } from '@/api/hr'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10 })
const employeeOptions = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  employee: null, date: '', check_in: '', check_out: '', status: 'normal', remark: ''
})

const rules = {
  employee: [{ required: true, message: '请选择员工', trigger: 'change' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
}

const statusText = (s) => ({ normal: '正常', late: '迟到', early: '早退', absent: '旷工', leave: '请假' }[s] || s)
const statusType = (s) => ({ normal: 'success', late: 'warning', early: 'warning', absent: 'danger', leave: 'info' }[s] || '')

const fetchData = async () => {
  const res = await getAttendanceList(query.value)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchEmployees = async () => {
  const res = await getEmployeeOptions()
  employeeOptions.value = res.data
}

onMounted(() => {
  fetchData()
  fetchEmployees()
})

const resetForm = () => {
  form.value = { employee: null, date: '', check_in: '', check_out: '', status: 'normal', remark: '' }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增考勤'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑考勤'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    employee: row.employee,
    date: row.date,
    check_in: row.check_in || '',
    check_out: row.check_out || '',
    status: row.status,
    remark: row.remark || '',
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (isEdit.value) {
        await updateAttendance(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createAttendance(form.value)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      await fetchData()
    } finally {
      submitLoading.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除该考勤记录吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteAttendance(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
</style>
