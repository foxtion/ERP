<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'finance:voucher:add'" type="primary" @click="handleAdd">新增凭证</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="voucher_no" label="凭证号" min-width="150" />
        <el-table-column prop="voucher_date" label="凭证日期" min-width="120" />
        <el-table-column prop="total_debit" label="借方合计" width="120" align="right" />
        <el-table-column prop="total_credit" label="贷方合计" width="120" align="right" />
        <el-table-column prop="preparer_name" label="制单人" min-width="120" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'finance:voucher:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'finance:voucher:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="900px" top="5vh">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="凭证号" prop="voucher_no">
              <el-input v-model="form.voucher_no" placeholder="请输入凭证号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="凭证日期" prop="voucher_date">
              <el-date-picker v-model="form.voucher_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>

      <div class="sub-title">凭证明细</div>
      <el-table :data="form.items" border size="small">
        <el-table-column label="会计科目" min-width="180">
          <template #default="{ $index }">
            <el-select v-model="form.items[$index].subject" filterable placeholder="请选择科目" style="width: 100%">
              <el-option v-for="s in subjectOptions" :key="s.id" :label="`${s.code} ${s.name}`" :value="s.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="摘要" min-width="150">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].summary" placeholder="摘要" />
          </template>
        </el-table-column>
        <el-table-column label="借方金额" width="120">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].debit" :min="0" :precision="2" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="贷方金额" width="120">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].credit" :min="0" :precision="2" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="70" align="center">
          <template #default="{ $index }">
            <el-button link type="danger" @click="removeItem($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button class="add-row-btn" type="primary" plain @click="addItem">+ 添加明细</el-button>

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
import { getVoucherList, createVoucher, updateVoucher, deleteVoucher } from '@/api/finance'
import { getSubjectFlat } from '@/api/finance'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10 })
const subjectOptions = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  voucher_no: '', voucher_date: '', remark: '', items: []
})

const rules = {
  voucher_no: [{ required: true, message: '请输入凭证号', trigger: 'blur' }],
  voucher_date: [{ required: true, message: '请选择凭证日期', trigger: 'change' }],
}

const fetchData = async () => {
  const res = await getVoucherList(query.value)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchSubjects = async () => {
  const res = await getSubjectFlat()
  subjectOptions.value = res.data
}

onMounted(() => {
  fetchData()
  fetchSubjects()
})

const resetForm = () => {
  form.value = { voucher_no: '', voucher_date: '', remark: '', items: [] }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增记账凭证'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑记账凭证'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    voucher_no: row.voucher_no,
    voucher_date: row.voucher_date,
    remark: row.remark || '',
    items: row.items ? row.items.map(i => ({ ...i })) : [],
  }
  dialogVisible.value = true
}

const addItem = () => {
  form.value.items.push({ subject: null, summary: '', debit: 0, credit: 0 })
}

const removeItem = (index) => {
  form.value.items.splice(index, 1)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    if (form.value.items.length === 0) {
      ElMessage.warning('请至少添加一条明细')
      return
    }
    const totalDebit = form.value.items.reduce((sum, i) => sum + (i.debit || 0), 0)
    const totalCredit = form.value.items.reduce((sum, i) => sum + (i.credit || 0), 0)
    if (totalDebit !== totalCredit) {
      ElMessage.warning('借方合计必须等于贷方合计')
      return
    }
    submitLoading.value = true
    try {
      const payload = { ...form.value }
      if (isEdit.value) {
        await updateVoucher(currentId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createVoucher(payload)
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
  ElMessageBox.confirm(`确定删除凭证 "${row.voucher_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteVoucher(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
.sub-title { font-weight: bold; margin: 15px 0 8px; }
.add-row-btn { margin-top: 10px; }
</style>
