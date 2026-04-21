<template>
  <div class="page-container">
    <el-card>
      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :span="6">
          <div class="stat-card bg-total">
            <div class="label">往来单位总数</div>
            <div class="value">{{ stats.total || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card bg-receivable">
            <div class="label">客户数</div>
            <div class="value">{{ stats.customer || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card bg-payable">
            <div class="label">供应商数</div>
            <div class="value">{{ stats.supplier || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card bg-both">
            <div class="label">双重身份</div>
            <div class="value">{{ stats.both || 0 }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 搜索栏 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="单位名称">
          <el-input v-model="searchForm.name" placeholder="请输入单位名称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.type" placeholder="全部" clearable style="width: 120px">
            <el-option label="客户" value="customer" />
            <el-option label="供应商" value="supplier" />
            <el-option label="客户+供应商" value="both" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar">
        <el-button v-permission="'finance:receivable:add'" type="primary" @click="handleAdd">新增单位</el-button>
      </div>

      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="name" label="单位名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="typeType(row.type)" size="small">{{ typeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="contact" label="联系人" width="120" />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column label="应收未结" width="130" align="right">
          <template #default="{ row }">
            <span v-if="row.receivable_unpaid > 0" class="text-receivable">{{ formatMoney(row.receivable_unpaid) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="应付未结" width="130" align="right">
          <template #default="{ row }">
            <span v-if="row.payable_unpaid > 0" class="text-payable">{{ formatMoney(row.payable_unpaid) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="净余额" width="130" align="right">
          <template #default="{ row }">
            <span :class="row.net_balance > 0 ? 'text-receivable' : row.net_balance < 0 ? 'text-payable' : 'text-muted'">
              {{ formatMoney(row.net_balance) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="info" @click="handleView(row)">详情</el-button>
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑往来单位' : '新增往来单位'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="单位名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入单位名称" />
        </el-form-item>
        <el-form-item label="单位类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio label="customer">客户</el-radio>
            <el-radio label="supplier">供应商</el-radio>
            <el-radio label="both">客户+供应商</el-radio>
            <el-radio label="other">其他</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人">
              <el-input v-model="form.contact" placeholder="联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="form.phone" placeholder="联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="地址">
          <el-input v-model="form.address" placeholder="地址" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开户银行">
              <el-input v-model="form.bank_name" placeholder="开户银行" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="银行账号">
              <el-input v-model="form.bank_account" placeholder="银行账号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="税号">
          <el-input v-model="form.tax_no" placeholder="统一社会信用代码/税号" />
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

    <!-- 详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="往来单位详情" width="560px">
      <el-descriptions :column="1" border v-if="currentRow">
        <el-descriptions-item label="单位名称">{{ currentRow.name }}</el-descriptions-item>
        <el-descriptions-item label="单位类型">{{ typeText(currentRow.type) }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ currentRow.contact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentRow.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="地址">{{ currentRow.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开户银行">{{ currentRow.bank_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="银行账号">{{ currentRow.bank_account || '-' }}</el-descriptions-item>
        <el-descriptions-item label="税号">{{ currentRow.tax_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="应收总额">{{ formatMoney(currentRow.receivable_total) }}</el-descriptions-item>
        <el-descriptions-item label="应收未结">{{ formatMoney(currentRow.receivable_unpaid) }}</el-descriptions-item>
        <el-descriptions-item label="应付总额">{{ formatMoney(currentRow.payable_total) }}</el-descriptions-item>
        <el-descriptions-item label="应付未结">{{ formatMoney(currentRow.payable_unpaid) }}</el-descriptions-item>
        <el-descriptions-item label="净余额">
          <span :class="currentRow.net_balance > 0 ? 'text-receivable' : currentRow.net_balance < 0 ? 'text-payable' : ''">
            {{ formatMoney(currentRow.net_balance) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="备注">{{ currentRow.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getCounterpartyList, createCounterparty, updateCounterparty, deleteCounterparty
} from '@/api/finance'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = ref({ page: 1, size: 10 })
const stats = ref({})

const searchForm = reactive({ name: '', type: '' })

const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)
const currentRow = ref(null)

const form = ref({
  name: '', type: 'customer', contact: '', phone: '', address: '',
  bank_name: '', bank_account: '', tax_no: '', remark: ''
})

const rules = {
  name: [{ required: true, message: '请输入单位名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择单位类型', trigger: 'change' }],
}

const typeText = (t) => ({ customer: '客户', supplier: '供应商', both: '客户+供应商', other: '其他' }[t] || t)
const typeType = (t) => ({ customer: 'success', supplier: 'warning', both: 'primary', other: 'info' }[t] || '')

const formatMoney = (v) => {
  if (v === undefined || v === null) return '-'
  return '¥' + Number(v).toFixed(2)
}

const buildQuery = () => {
  const params = { ...query.value }
  if (searchForm.name) params.search = searchForm.name
  if (searchForm.type) params.type = searchForm.type
  return params
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getCounterpartyList(buildQuery())
    tableData.value = res.data.list || res.data.results || res.data
    total.value = res.data.pagination?.total || res.data.count || tableData.value.length
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  const all = tableData.value
  stats.value = {
    total: total.value,
    customer: all.filter(x => x.type === 'customer').length,
    supplier: all.filter(x => x.type === 'supplier').length,
    both: all.filter(x => x.type === 'both').length,
  }
}

onMounted(() => {
  fetchData()
})

const handleSearch = () => {
  query.value.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.name = ''
  searchForm.type = ''
  query.value.page = 1
  fetchData()
}

const resetForm = () => {
  form.value = { name: '', type: 'customer', contact: '', phone: '', address: '', bank_name: '', bank_account: '', tax_no: '', remark: '' }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  isEdit.value = true
  currentId.value = row.id
  form.value = { ...row }
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
        await updateCounterparty(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createCounterparty(form.value)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await fetchData()
    } finally {
      submitLoading.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除往来单位「${row.name}」吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteCounterparty(row.id)
    ElMessage.success('删除成功')
    await fetchData()
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
.bg-receivable { background: linear-gradient(135deg, #67c23a, #85ce61); }
.bg-payable { background: linear-gradient(135deg, #f56c6c, #f78989); }
.bg-both { background: linear-gradient(135deg, #e6a23c, #ebb563); }
.search-form { margin-bottom: 15px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
.text-receivable { color: #67c23a; font-weight: bold; }
.text-payable { color: #f56c6c; font-weight: bold; }
.text-muted { color: #909399; }
</style>
