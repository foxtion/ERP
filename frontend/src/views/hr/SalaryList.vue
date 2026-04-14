<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'hr:salary:add'" type="primary" @click="handleAdd">新增薪资</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="employee_no" label="工号" min-width="120" />
        <el-table-column prop="employee_name" label="姓名" min-width="100" />
        <el-table-column prop="year_month" label="薪资月份" min-width="120" />
        <el-table-column prop="base_salary" label="基本工资" width="120" align="right" />
        <el-table-column prop="bonus" label="奖金" width="100" align="right" />
        <el-table-column prop="deduction" label="扣款" width="100" align="right" />
        <el-table-column prop="total_salary" label="实发工资" width="120" align="right">
          <template #default="{ row }">
            <el-tag type="success">{{ row.total_salary }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'hr:salary:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'hr:salary:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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
        <el-form-item label="薪资月份" prop="year_month">
          <el-input v-model="form.year_month" placeholder="如 2026-04" />
        </el-form-item>
        <el-form-item label="基本工资">
          <el-input-number v-model="form.base_salary" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="奖金">
          <el-input-number v-model="form.bonus" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="扣款">
          <el-input-number v-model="form.deduction" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="实发工资">
          <el-input :model-value="(form.base_salary || 0) + (form.bonus || 0) - (form.deduction || 0)" disabled style="width: 100%" />
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
import { getSalaryList, createSalary, updateSalary, deleteSalary } from '@/api/hr'
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
  employee: null, year_month: '', base_salary: 0, bonus: 0, deduction: 0, remark: ''
})

const rules = {
  employee: [{ required: true, message: '请选择员工', trigger: 'change' }],
  year_month: [{ required: true, message: '请输入薪资月份', trigger: 'blur' }],
}

const fetchData = async () => {
  const res = await getSalaryList(query.value)
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
  form.value = { employee: null, year_month: '', base_salary: 0, bonus: 0, deduction: 0, remark: '' }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增薪资'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑薪资'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    employee: row.employee,
    year_month: row.year_month,
    base_salary: row.base_salary,
    bonus: row.bonus,
    deduction: row.deduction,
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
        await updateSalary(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createSalary(form.value)
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
  ElMessageBox.confirm(`确定删除该薪资记录吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteSalary(row.id)
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
