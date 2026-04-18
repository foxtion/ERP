<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'purchase:request:add'" type="primary" @click="handleAdd">新增申请</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="request_no" label="申请单号" min-width="150" />
        <el-table-column prop="request_date" label="申请日期" min-width="120" />
        <el-table-column prop="applicant_name" label="申请人" min-width="120" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额" width="120" align="right" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'purchase:request:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'purchase:request:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
            <el-button v-permission="'purchase:order:add'" v-if="row.status === 'approved'" link type="success" @click="handleConvert(row)">转采购订单</el-button>
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
            <el-form-item label="申请单号" prop="request_no">
              <el-input v-model="form.request_no" placeholder="请输入申请单号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="申请日期" prop="request_date">
              <el-date-picker v-model="form.request_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>

      <div class="sub-title">申请明细</div>
      <el-table :data="form.items" border size="small">
        <el-table-column label="物料名称" min-width="140">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].material_name" placeholder="物料名称" />
          </template>
        </el-table-column>
        <el-table-column label="规格型号" min-width="120">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].spec" placeholder="规格" />
          </template>
        </el-table-column>
        <el-table-column label="数量" width="110">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].quantity" :min="0" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="单位" width="80">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].unit" placeholder="单位" />
          </template>
        </el-table-column>
        <el-table-column label="预估单价" width="110">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].estimated_price" :min="0" :precision="4" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="120">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].remark" placeholder="备注" />
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

    <!-- 转采购订单弹窗 -->
    <el-dialog v-model="convertVisible" title="转采购订单" width="600px">
      <el-form ref="convertFormRef" :model="convertForm" :rules="convertRules" label-width="100px">
        <el-form-item label="申请单号">
          <el-input v-model="convertForm.request_no" disabled />
        </el-form-item>
        <el-form-item label="订单编号" prop="order_no">
          <el-input v-model="convertForm.order_no" placeholder="请输入采购订单编号" />
        </el-form-item>
        <el-form-item label="供应商" prop="supplier">
          <el-select v-model="convertForm.supplier" placeholder="请选择供应商" filterable style="width: 100%">
            <el-option v-for="s in supplierList" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="订单日期" prop="order_date">
          <el-date-picker v-model="convertForm.order_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="交货日期">
          <el-date-picker v-model="convertForm.delivery_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="convertForm.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="convertVisible = false">取消</el-button>
        <el-button type="primary" :loading="convertLoading" @click="handleConvertSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRequestList, createRequest, updateRequest, deleteRequest, convertRequestToOrder, getSupplierList } from '@/api/purchase'

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
  request_no: '',
  request_date: '',
  remark: '',
  items: [],
})

const rules = {
  request_no: [{ required: true, message: '请输入申请单号', trigger: 'blur' }],
  request_date: [{ required: true, message: '请选择申请日期', trigger: 'change' }],
}

const statusText = (s) => ({ draft: '草稿', pending: '待审批', approved: '已批准', rejected: '已驳回', ordered: '已转单' }[s] || s)
const statusType = (s) => ({ draft: 'info', pending: 'warning', approved: 'success', rejected: 'danger', ordered: '' }[s] || '')

const fetchData = async () => {
  const res = await getRequestList(query.value)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

onMounted(fetchData)

const resetForm = () => {
  form.value = { request_no: '', request_date: '', remark: '', items: [] }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增采购申请'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑采购申请'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    request_no: row.request_no,
    request_date: row.request_date,
    remark: row.remark || '',
    items: row.items ? row.items.map(i => ({ ...i })) : [],
  }
  dialogVisible.value = true
}

const addItem = () => {
  form.value.items.push({ material_name: '', spec: '', quantity: 1, unit: '件', estimated_price: 0, remark: '' })
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
    submitLoading.value = true
    try {
      const payload = { ...form.value }
      if (isEdit.value) {
        await updateRequest(currentId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createRequest(payload)
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
  ElMessageBox.confirm(`确定删除申请单 "${row.request_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteRequest(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}

// 转采购订单
const convertVisible = ref(false)
const convertLoading = ref(false)
const convertFormRef = ref(null)
const supplierList = ref([])
const convertForm = ref({
  request_id: null,
  request_no: '',
  order_no: '',
  supplier: null,
  order_date: '',
  delivery_date: '',
  remark: '',
})

const convertRules = {
  order_no: [{ required: true, message: '请输入订单编号', trigger: 'blur' }],
  supplier: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  order_date: [{ required: true, message: '请选择订单日期', trigger: 'change' }],
}

const handleConvert = async (row) => {
  convertForm.value = {
    request_id: row.id,
    request_no: row.request_no,
    order_no: '',
    supplier: null,
    order_date: '',
    delivery_date: '',
    remark: row.remark || '',
  }
  const res = await getSupplierList({ size: 999 })
  supplierList.value = res.data.list
  convertVisible.value = true
}

const handleConvertSubmit = async () => {
  if (!convertFormRef.value) return
  await convertFormRef.value.validate(async (valid) => {
    if (!valid) return
    convertLoading.value = true
    try {
      const { request_id, ...payload } = convertForm.value
      await convertRequestToOrder(request_id, payload)
      ElMessage.success('转采购订单成功')
      convertVisible.value = false
      await fetchData()
    } finally {
      convertLoading.value = false
    }
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
