<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索栏 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="单据编号">
          <el-input v-model="searchForm.search" placeholder="单据编号/来源单号" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="往来单位">
          <el-input v-model="searchForm.counterparty" placeholder="请输入往来单位" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.doc_type" placeholder="全部" clearable style="width: 100px">
            <el-option label="应收" value="receivable" />
            <el-option label="应付" value="payable" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 100px">
            <el-option label="未结清" value="unpaid" />
            <el-option label="部分结清" value="partial" />
            <el-option label="已结清" value="paid" />
          </el-select>
        </el-form-item>
        <el-form-item label="单据日期">
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
        <el-form-item label="仅逾期">
          <el-switch v-model="searchForm.overdue" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar">
        <el-button v-permission="'finance:receivable:add'" type="primary" @click="handleAdd">新增单据</el-button>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="doc_no" label="单据编号" min-width="150" />
        <el-table-column prop="doc_type" label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.doc_type === 'receivable' ? 'success' : 'warning'">{{ row.doc_type === 'receivable' ? '应收' : '应付' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="counterparty" label="往来单位" min-width="150" />
        <el-table-column prop="doc_date" label="单据日期" width="110" />
        <el-table-column prop="due_date" label="到期日" width="110">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.is_overdue }">{{ row.due_date || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">
            <span>{{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="paid_amount" label="已结金额" width="120" align="right">
          <template #default="{ row }">
            <span>{{ formatMoney(row.paid_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="remaining_amount" label="剩余未结" width="120" align="right">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.remaining_amount > 0 }">{{ formatMoney(row.remaining_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="overdue_days" label="逾期天数" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.overdue_days > 0" type="danger" size="small">{{ row.overdue_days }}天</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source_type" label="来源" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.source_type === 'sales_order'" type="success" size="small">销售订单</el-tag>
            <el-tag v-else-if="row.source_type === 'purchase_order'" type="warning" size="small">采购订单</el-tag>
            <el-tag v-else type="info" size="small">手工</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source_no" label="来源单号" min-width="130" />
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleViewSettlements(row)">核销明细</el-button>
            <el-button v-permission="'finance:receivable:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'finance:receivable:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="单据编号" prop="doc_no">
          <el-input v-model="form.doc_no" placeholder="请输入单据编号，留空自动生成">
            <template #append>
              <el-button @click="generateDocNo">自动生成</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="类型" prop="doc_type">
          <el-radio-group v-model="form.doc_type">
            <el-radio label="receivable">应收</el-radio>
            <el-radio label="payable">应付</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="往来单位" prop="counterparty">
          <el-input v-model="form.counterparty" placeholder="请输入往来单位" />
        </el-form-item>
        <el-form-item label="单据日期" prop="doc_date">
          <el-date-picker v-model="form.doc_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="到期日">
          <el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" placeholder="选择到期日（可选）" style="width: 100%" />
        </el-form-item>
        <el-form-item label="金额" prop="amount">
          <el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="已结金额">
          <el-input-number v-model="form.paid_amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="来源类型">
          <el-select v-model="form.source_type" style="width: 100%">
            <el-option label="销售订单" value="sales_order" />
            <el-option label="采购订单" value="purchase_order" />
            <el-option label="手工录入" value="manual" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源单号">
          <el-input v-model="form.source_no" placeholder="请输入来源单号（可选）" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="unpaid">未结清</el-radio>
            <el-radio label="partial">部分结清</el-radio>
            <el-radio label="paid">已结清</el-radio>
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

    <!-- 核销明细对话框 -->
    <el-dialog v-model="settlementDialogVisible" title="核销明细" width="650px">
      <el-table :data="currentSettlements" border stripe max-height="400">
        <el-table-column prop="payment_receipt_no" label="收付款单号" min-width="150" />
        <el-table-column prop="amount" label="核销金额" width="120" align="right">
          <template #default="{ row }">
            <span>{{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="核销时间" min-width="160" />
      </el-table>
      <template v-if="!currentSettlements || currentSettlements.length === 0">
        <el-empty description="暂无核销记录" />
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getReceivableList, createReceivable, updateReceivable, deleteReceivable
} from '@/api/finance'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = ref({ page: 1, size: 10 })

const searchForm = reactive({
  search: '',
  counterparty: '',
  doc_type: '',
  status: '',
  dateRange: [],
  overdue: false,
})

const dialogVisible = ref(false)
const settlementDialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)
const currentSettlements = ref([])

const form = ref({
  doc_no: '', doc_type: 'receivable', counterparty: '', doc_date: '', due_date: '',
  amount: 0, paid_amount: 0, status: 'unpaid', source_type: 'manual', source_no: '', remark: ''
})

const rules = {
  doc_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  counterparty: [{ required: true, message: '请输入往来单位', trigger: 'blur' }],
  doc_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
}

const statusText = (s) => ({ unpaid: '未结清', partial: '部分结清', paid: '已结清' }[s] || s)
const statusType = (s) => ({ unpaid: 'info', partial: 'warning', paid: 'success' }[s] || '')
const formatMoney = (v) => {
  if (v === undefined || v === null) return '-'
  return '¥' + Number(v).toFixed(2)
}

const buildQuery = () => {
  const params = { ...query.value }
  if (searchForm.search) params.search = searchForm.search
  if (searchForm.counterparty) params.counterparty = searchForm.counterparty
  if (searchForm.doc_type) params.doc_type = searchForm.doc_type
  if (searchForm.status) params.status = searchForm.status
  if (searchForm.dateRange && searchForm.dateRange.length === 2) {
    params.date_from = searchForm.dateRange[0]
    params.date_to = searchForm.dateRange[1]
  }
  if (searchForm.overdue) params.overdue = '1'
  return params
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getReceivableList(buildQuery())
    tableData.value = res.data.list
    total.value = res.data.pagination.total
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

const handleSearch = () => {
  query.value.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.search = ''
  searchForm.counterparty = ''
  searchForm.doc_type = ''
  searchForm.status = ''
  searchForm.dateRange = []
  searchForm.overdue = false
  query.value.page = 1
  fetchData()
}

const generateDocNo = () => {
  const prefix = form.value.doc_type === 'receivable' ? 'YS' : 'YF'
  const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  const random = String(Math.floor(Math.random() * 900) + 100)
  form.value.doc_no = `${prefix}${dateStr}-${random}`
}

const resetForm = () => {
  form.value = {
    doc_no: '', doc_type: 'receivable', counterparty: '', doc_date: '', due_date: '',
    amount: 0, paid_amount: 0, status: 'unpaid', source_type: 'manual', source_no: '', remark: ''
  }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增应收应付'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑应收应付'
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
        await updateReceivable(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createReceivable(form.value)
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
    await deleteReceivable(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}

const handleViewSettlements = (row) => {
  currentSettlements.value = row.settlements || []
  settlementDialogVisible.value = true
}
</script>

<style scoped>
.page-container { padding: 20px; }
.search-form { margin-bottom: 15px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
.text-danger { color: #f56c6c; font-weight: bold; }
.text-warning { color: #e6a23c; font-weight: bold; }
</style>
