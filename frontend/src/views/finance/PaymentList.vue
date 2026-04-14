<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'finance:payment:add'" type="primary" @click="handleAdd">新增收付款</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="doc_no" label="单据编号" min-width="150" />
        <el-table-column prop="doc_type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.doc_type === 'receipt' ? 'success' : 'warning'">{{ row.doc_type === 'receipt' ? '收款' : '付款' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="counterparty" label="往来单位" min-width="180" />
        <el-table-column prop="doc_date" label="日期" min-width="120" />
        <el-table-column prop="amount" label="金额" width="120" align="right" />
        <el-table-column prop="operator_name" label="经办人" min-width="120" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'finance:payment:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'finance:payment:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="550px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="单据编号" prop="doc_no">
          <el-input v-model="form.doc_no" placeholder="请输入单据编号" />
        </el-form-item>
        <el-form-item label="类型" prop="doc_type">
          <el-radio-group v-model="form.doc_type">
            <el-radio label="receipt">收款</el-radio>
            <el-radio label="payment">付款</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="往来单位" prop="counterparty">
          <el-input v-model="form.counterparty" placeholder="请输入往来单位" />
        </el-form-item>
        <el-form-item label="日期" prop="doc_date">
          <el-date-picker v-model="form.doc_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="金额">
          <el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 100%" />
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
import { getPaymentList, createPayment, updatePayment, deletePayment } from '@/api/finance'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10 })

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  doc_no: '', doc_type: 'receipt', counterparty: '', doc_date: '', amount: 0, remark: ''
})

const rules = {
  doc_no: [{ required: true, message: '请输入单据编号', trigger: 'blur' }],
  doc_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  counterparty: [{ required: true, message: '请输入往来单位', trigger: 'blur' }],
  doc_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
}

const fetchData = async () => {
  const res = await getPaymentList(query.value)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

onMounted(fetchData)

const resetForm = () => {
  form.value = { doc_no: '', doc_type: 'receipt', counterparty: '', doc_date: '', amount: 0, remark: '' }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增收付款'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑收付款'
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form.value, row)
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (isEdit.value) {
        await updatePayment(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createPayment(form.value)
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
  ElMessageBox.confirm(`确定删除单据 "${row.doc_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deletePayment(row.id)
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
