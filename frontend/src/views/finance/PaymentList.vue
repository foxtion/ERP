<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索栏 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="单据编号">
          <el-input v-model="searchForm.search" placeholder="单据编号" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="往来单位">
          <el-input v-model="searchForm.counterparty" placeholder="请输入往来单位" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.doc_type" placeholder="全部" clearable style="width: 100px">
            <el-option label="收款" value="receipt" />
            <el-option label="付款" value="payment" />
          </el-select>
        </el-form-item>
        <el-form-item label="付款方式">
          <el-select v-model="searchForm.payment_method" placeholder="全部" clearable style="width: 120px">
            <el-option label="现金" value="cash" />
            <el-option label="银行转账" value="bank_transfer" />
            <el-option label="支票" value="check" />
            <el-option label="微信支付" value="wechat" />
            <el-option label="支付宝" value="alipay" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
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
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar">
        <el-button v-permission="'finance:payment:add'" type="primary" @click="handleAdd">新增收付款</el-button>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="doc_no" label="单据编号" min-width="150" />
        <el-table-column prop="doc_type" label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.doc_type === 'receipt' ? 'success' : 'warning'">{{ row.doc_type === 'receipt' ? '收款' : '付款' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="counterparty" label="往来单位" min-width="150" />
        <el-table-column prop="doc_date" label="日期" width="110" />
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">
            <span>{{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="settled_amount" label="已核销" width="120" align="right">
          <template #default="{ row }">
            <span :class="{ 'text-success': row.settled_amount > 0 }">{{ formatMoney(row.settled_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unsettled_amount" label="未核销" width="120" align="right">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.unsettled_amount > 0 }">{{ formatMoney(row.unsettled_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="付款方式" width="100" align="center">
          <template #default="{ row }">
            {{ methodText(row.payment_method) }}
          </template>
        </el-table-column>
        <el-table-column prop="bank_account" label="银行账户" min-width="140" show-overflow-tooltip />
        <el-table-column prop="operator_name" label="经办人" width="100" />
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.unsettled_amount > 0" link type="success" @click="handleSettle(row)">核销</el-button>
            <el-button link type="primary" @click="handleViewSettlements(row)">核销明细</el-button>
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
        <el-form-item label="金额" prop="amount">
          <el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="付款方式">
          <el-select v-model="form.payment_method" style="width: 100%">
            <el-option label="现金" value="cash" />
            <el-option label="银行转账" value="bank_transfer" />
            <el-option label="支票" value="check" />
            <el-option label="微信支付" value="wechat" />
            <el-option label="支付宝" value="alipay" />
          </el-select>
        </el-form-item>
        <el-form-item label="银行账户">
          <el-input v-model="form.bank_account" placeholder="请输入银行账户（可选）" />
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

    <!-- 核销对话框 -->
    <el-dialog v-model="settleDialogVisible" title="收付款核销" width="650px">
      <el-alert
        v-if="currentPayment"
        :title="`收付款单：${currentPayment.doc_no} | 往来单位：${currentPayment.counterparty} | 未核销金额：${formatMoney(currentPayment.unsettled_amount)}`"
        type="info"
        :closable="false"
        style="margin-bottom: 15px"
      />
      <el-form :model="settleForm" label-width="100px">
        <el-form-item label="选择应收应付">
          <el-select
            v-model="settleForm.receivable_id"
            filterable
            remote
            :remote-method="searchReceivables"
            :loading="receivableLoading"
            placeholder="输入往来单位或单号搜索"
            style="width: 100%"
          >
            <el-option
              v-for="item in receivableOptions"
              :key="item.id"
              :label="`${item.doc_no} | ${item.counterparty} | 剩余${formatMoney(item.remaining_amount)}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="核销金额">
          <el-input-number v-model="settleForm.amount" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="settleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="settleLoading" @click="handleSubmitSettle">确定核销</el-button>
      </template>
    </el-dialog>

    <!-- 核销明细对话框 -->
    <el-dialog v-model="settlementDialogVisible" title="核销明细" width="650px">
      <el-table :data="currentSettlements" border stripe max-height="400">
        <el-table-column prop="receivable_payable_no" label="应收应付单号" min-width="150" />
        <el-table-column prop="amount" label="核销金额" width="120" align="right">
          <template #default="{ row }">
            <span>{{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="核销时间" min-width="160" />
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click="handleCancelSettle(row)">取消</el-button>
          </template>
        </el-table-column>
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
  getPaymentList, createPayment, updatePayment, deletePayment,
  settlePayment, cancelSettlement, getReceivableList
} from '@/api/finance'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = ref({ page: 1, size: 10 })

const searchForm = reactive({
  search: '',
  counterparty: '',
  doc_type: '',
  payment_method: '',
  dateRange: [],
})

const dialogVisible = ref(false)
const settleDialogVisible = ref(false)
const settlementDialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const settleLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)
const currentPayment = ref(null)
const currentSettlements = ref([])

const form = ref({
  doc_no: '', doc_type: 'receipt', counterparty: '', doc_date: '', amount: 0,
  payment_method: 'bank_transfer', bank_account: '', remark: ''
})

const settleForm = reactive({
  receivable_id: null,
  amount: 0,
})

const receivableOptions = ref([])
const receivableLoading = ref(false)

const rules = {
  doc_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  counterparty: [{ required: true, message: '请输入往来单位', trigger: 'blur' }],
  doc_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
}

const methodText = (m) => ({
  cash: '现金', bank_transfer: '银行转账', check: '支票', wechat: '微信支付', alipay: '支付宝'
}[m] || m)
const formatMoney = (v) => {
  if (v === undefined || v === null) return '-'
  return '¥' + Number(v).toFixed(2)
}

const buildQuery = () => {
  const params = { ...query.value }
  if (searchForm.search) params.search = searchForm.search
  if (searchForm.counterparty) params.counterparty = searchForm.counterparty
  if (searchForm.doc_type) params.doc_type = searchForm.doc_type
  if (searchForm.payment_method) params.payment_method = searchForm.payment_method
  if (searchForm.dateRange && searchForm.dateRange.length === 2) {
    params.date_from = searchForm.dateRange[0]
    params.date_to = searchForm.dateRange[1]
  }
  return params
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getPaymentList(buildQuery())
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
  searchForm.payment_method = ''
  searchForm.dateRange = []
  query.value.page = 1
  fetchData()
}

const generateDocNo = () => {
  const prefix = form.value.doc_type === 'receipt' ? 'SK' : 'FK'
  const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  const random = String(Math.floor(Math.random() * 900) + 100)
  form.value.doc_no = `${prefix}${dateStr}-${random}`
}

const resetForm = () => {
  form.value = {
    doc_no: '', doc_type: 'receipt', counterparty: '', doc_date: '', amount: 0,
    payment_method: 'bank_transfer', bank_account: '', remark: ''
  }
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

// 核销相关
const handleSettle = (row) => {
  currentPayment.value = row
  settleForm.receivable_id = null
  settleForm.amount = row.unsettled_amount || 0
  receivableOptions.value = []
  settleDialogVisible.value = true
}

const searchReceivables = async (queryStr) => {
  if (!queryStr || queryStr.length < 1) return
  receivableLoading.value = true
  try {
    const expectedType = currentPayment.value?.doc_type === 'receipt' ? 'receivable' : 'payable'
    const res = await getReceivableList({
      search: queryStr,
      doc_type: expectedType,
      status__in: 'unpaid,partial',
      size: 50,
    })
    receivableOptions.value = (res.data.list || []).filter(item => item.remaining_amount > 0)
  } finally {
    receivableLoading.value = false
  }
}

const handleSubmitSettle = async () => {
  if (!settleForm.receivable_id) {
    ElMessage.warning('请选择应收应付单')
    return
  }
  if (!settleForm.amount || settleForm.amount <= 0) {
    ElMessage.warning('请输入有效的核销金额')
    return
  }
  settleLoading.value = true
  try {
    await settlePayment(currentPayment.value.id, {
      receivable_id: settleForm.receivable_id,
      amount: settleForm.amount,
    })
    ElMessage.success('核销成功')
    settleDialogVisible.value = false
    await fetchData()
  } finally {
    settleLoading.value = false
  }
}

const handleViewSettlements = (row) => {
  currentSettlements.value = row.settlements || []
  settlementDialogVisible.value = true
}

const handleCancelSettle = (row) => {
  ElMessageBox.confirm('确定取消该核销记录吗？', '提示', { type: 'warning' }).then(async () => {
    await cancelSettlement(row.id)
    ElMessage.success('取消核销成功')
    settlementDialogVisible.value = false
    await fetchData()
  })
}
</script>

<style scoped>
.page-container { padding: 20px; }
.search-form { margin-bottom: 15px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
.text-success { color: #67c23a; font-weight: bold; }
.text-warning { color: #e6a23c; font-weight: bold; }
</style>
