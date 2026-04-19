<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索栏 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="凭证号">
          <el-input v-model="searchForm.search" placeholder="凭证号" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 100px">
            <el-option label="草稿" value="draft" />
            <el-option label="已审核" value="audited" />
            <el-option label="已作废" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="凭证日期">
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
        <el-button v-permission="'finance:voucher:add'" type="primary" @click="handleAdd">新增凭证</el-button>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="voucher_no" label="凭证号" min-width="150" />
        <el-table-column prop="voucher_date" label="凭证日期" min-width="110" />
        <el-table-column prop="total_debit" label="借方合计" width="120" align="right">
          <template #default="{ row }">
            <span>{{ formatMoney(row.total_debit) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_credit" label="贷方合计" width="120" align="right">
          <template #default="{ row }">
            <span>{{ formatMoney(row.total_credit) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="preparer_name" label="制单人" width="100" />
        <el-table-column prop="auditor_name" label="审核人" width="100">
          <template #default="{ row }">
            <span v-if="row.auditor_name">{{ row.auditor_name }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="audit_date" label="审核日期" width="130">
          <template #default="{ row }">
            <span v-if="row.audit_date">{{ formatDateTime(row.audit_date) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button link type="info" @click="handleView(row)">查看</el-button>
            <el-button v-if="row.status === 'draft'" v-permission="'finance:voucher:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'draft'" v-permission="'finance:voucher:edit'" link type="success" @click="handleAudit(row)">审核</el-button>
            <el-button v-if="row.status === 'audited'" v-permission="'finance:voucher:edit'" link type="warning" @click="handleCancelAudit(row)">反审核</el-button>
            <el-button v-if="row.status !== 'audited'" v-permission="'finance:voucher:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="900px" top="5vh">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="凭证号" prop="voucher_no">
              <el-input v-model="form.voucher_no" placeholder="请输入凭证号，留空自动生成">
                <template #append>
                  <el-button @click="generateNo">自动生成</el-button>
                </template>
              </el-input>
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

      <div class="sub-title">
        凭证明细
        <el-tag :type="balanceTag.type" class="balance-tag">{{ balanceTag.text }}</el-tag>
      </div>
      <el-table :data="form.items" border size="small">
        <el-table-column label="行号" width="50" align="center">
          <template #default="{ $index }">
            {{ $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column label="会计科目" min-width="200">
          <template #default="{ $index }">
            <el-select v-model="form.items[$index].subject" filterable placeholder="请选择科目" style="width: 100%">
              <el-option-group v-for="group in subjectGroups" :key="group.label" :label="group.label">
                <el-option v-for="s in group.options" :key="s.id" :label="`${s.code} ${s.name}`" :value="s.id" />
              </el-option-group>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="摘要" min-width="150">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].summary" placeholder="摘要" />
          </template>
        </el-table-column>
        <el-table-column label="借方金额" width="130">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].debit" :min="0" :precision="2" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="贷方金额" width="130">
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

    <!-- 查看详情对话框（只读） -->
    <el-dialog v-model="viewDialogVisible" title="凭证详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="凭证号">{{ currentRow?.voucher_no }}</el-descriptions-item>
        <el-descriptions-item label="凭证日期">{{ currentRow?.voucher_date }}</el-descriptions-item>
        <el-descriptions-item label="借方合计">{{ formatMoney(currentRow?.total_debit) }}</el-descriptions-item>
        <el-descriptions-item label="贷方合计">{{ formatMoney(currentRow?.total_credit) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(currentRow?.status)">{{ statusText(currentRow?.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="制单人">{{ currentRow?.preparer_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审核人">{{ currentRow?.auditor_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审核日期">{{ formatDateTime(currentRow?.audit_date) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentRow?.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div class="sub-title">凭证明细</div>
      <el-table :data="currentRow?.items || []" border size="small">
        <el-table-column label="行号" width="50" align="center">
          <template #default="{ $index }">
            {{ $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="subject_code" label="科目编码" width="100" />
        <el-table-column prop="subject_name" label="科目名称" min-width="150" />
        <el-table-column prop="summary" label="摘要" min-width="150" />
        <el-table-column prop="debit" label="借方金额" width="120" align="right">
          <template #default="{ row }">
            <span v-if="row.debit > 0">{{ formatMoney(row.debit) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="credit" label="贷方金额" width="120" align="right">
          <template #default="{ row }">
            <span v-if="row.credit > 0">{{ formatMoney(row.credit) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getVoucherList, createVoucher, updateVoucher, deleteVoucher,
  auditVoucher, cancelAuditVoucher, generateVoucherNo, getSubjectFlat
} from '@/api/finance'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = ref({ page: 1, size: 10 })
const subjectOptions = ref([])

const searchForm = reactive({
  search: '',
  status: '',
  dateRange: [],
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
  voucher_no: '', voucher_date: '', remark: '', items: []
})

const rules = {
  voucher_no: [{ required: true, message: '请输入凭证号', trigger: 'blur' }],
  voucher_date: [{ required: true, message: '请选择凭证日期', trigger: 'change' }],
}

// 按科目类别分组
const categoryMap = {
  asset: '资产', liability: '负债', equity: '所有者权益',
  income: '收入', expense: '费用'
}

const subjectGroups = computed(() => {
  const groups = {}
  subjectOptions.value.forEach(s => {
    const cat = categoryMap[s.category] || s.category || '其他'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(s)
  })
  return Object.entries(groups).map(([label, options]) => ({ label, options }))
})

// 借贷平衡实时计算
const balanceTag = computed(() => {
  const items = form.value.items || []
  const totalDebit = items.reduce((sum, i) => sum + (Number(i.debit) || 0), 0)
  const totalCredit = items.reduce((sum, i) => sum + (Number(i.credit) || 0), 0)
  if (items.length === 0) return { type: 'info', text: '请添加明细' }
  if (totalDebit === 0 && totalCredit === 0) return { type: 'info', text: '请输入金额' }
  if (totalDebit === totalCredit) return { type: 'success', text: `借贷平衡 ¥${totalDebit.toFixed(2)}` }
  const diff = totalDebit - totalCredit
  return { type: 'danger', text: `借贷差额 ¥${Math.abs(diff).toFixed(2)} (${diff > 0 ? '借多' : '贷多'})` }
})

const statusText = (s) => ({ draft: '草稿', audited: '已审核', cancelled: '已作废' }[s] || s)
const statusType = (s) => ({ draft: 'info', audited: 'success', cancelled: 'danger' }[s] || '')
const formatMoney = (v) => {
  if (v === undefined || v === null) return '-'
  return '¥' + Number(v).toFixed(2)
}
const formatDateTime = (v) => {
  if (!v) return ''
  const d = new Date(v)
  return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).replace(/\//g, '-')
}

const buildQuery = () => {
  const params = { ...query.value }
  if (searchForm.search) params.search = searchForm.search
  if (searchForm.status) params.status = searchForm.status
  if (searchForm.dateRange && searchForm.dateRange.length === 2) {
    params.date_from = searchForm.dateRange[0]
    params.date_to = searchForm.dateRange[1]
  }
  return params
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getVoucherList(buildQuery())
    tableData.value = res.data.list
    total.value = res.data.pagination.total
  } finally {
    loading.value = false
  }
}

const fetchSubjects = async () => {
  const res = await getSubjectFlat()
  subjectOptions.value = res.data
}

onMounted(() => {
  fetchData()
  fetchSubjects()
})

const handleSearch = () => {
  query.value.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.search = ''
  searchForm.status = ''
  searchForm.dateRange = []
  query.value.page = 1
  fetchData()
}

const generateNo = async () => {
  const res = await generateVoucherNo()
  form.value.voucher_no = res.data.voucher_no
}

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
    items: row.items ? row.items.map(i => ({
      subject: i.subject,
      summary: i.summary || '',
      debit: i.debit || 0,
      credit: i.credit || 0,
    })) : [],
  }
  dialogVisible.value = true
}

const handleView = (row) => {
  currentRow.value = row
  viewDialogVisible.value = true
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
    const totalDebit = form.value.items.reduce((sum, i) => sum + (Number(i.debit) || 0), 0)
    const totalCredit = form.value.items.reduce((sum, i) => sum + (Number(i.credit) || 0), 0)
    if (totalDebit !== totalCredit) {
      ElMessage.warning('借方合计必须等于贷方合计')
      return
    }
    if (totalDebit === 0) {
      ElMessage.warning('凭证金额不能为0')
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

const handleAudit = (row) => {
  ElMessageBox.confirm(`确定审核凭证 "${row.voucher_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await auditVoucher(row.id)
    ElMessage.success('审核成功')
    await fetchData()
  })
}

const handleCancelAudit = (row) => {
  ElMessageBox.confirm(`确定反审核凭证 "${row.voucher_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await cancelAuditVoucher(row.id)
    ElMessage.success('反审核成功')
    await fetchData()
  })
}
</script>

<style scoped>
.page-container { padding: 20px; }
.search-form { margin-bottom: 15px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
.sub-title { font-weight: bold; margin: 15px 0 8px; display: flex; align-items: center; justify-content: space-between; }
.balance-tag { font-weight: normal; margin-left: 10px; }
.add-row-btn { margin-top: 10px; }
.text-muted { color: #909399; }
</style>
