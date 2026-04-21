<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-form :model="searchForm" inline>
          <el-form-item label="往来单位">
            <el-select
              v-model="searchForm.counterparty"
              filterable
              clearable
              placeholder="请选择往来单位"
              style="width: 200px"
            >
              <el-option
                v-for="c in counterpartyOptions"
                :key="c.id"
                :label="c.name"
                :value="c.name"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              value-format="YYYY-MM-DD"
              range-separator="~"
              start-placeholder="开始"
              end-placeholder="结束"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询对账</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 汇总卡片 -->
      <el-row v-if="summary" :gutter="16" class="summary-row">
        <el-col :span="4">
          <div class="summary-card bg-receivable">
            <div class="label">应收总额</div>
            <div class="value">{{ formatMoney(summary.receivable_total) }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="summary-card bg-receivable-paid">
            <div class="label">应收已结</div>
            <div class="value">{{ formatMoney(summary.receivable_paid) }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="summary-card bg-receivable-unpaid">
            <div class="label">应收未结</div>
            <div class="value">{{ formatMoney(summary.receivable_unpaid) }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="summary-card bg-payable">
            <div class="label">应付总额</div>
            <div class="value">{{ formatMoney(summary.payable_total) }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="summary-card bg-payable-paid">
            <div class="label">应付已结</div>
            <div class="value">{{ formatMoney(summary.payable_paid) }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="summary-card bg-payable-unpaid">
            <div class="label">应付未结</div>
            <div class="value">{{ formatMoney(summary.payable_unpaid) }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 明细表格 -->
      <el-table v-if="items.length > 0" :data="items" border stripe v-loading="loading" class="statement-table" show-summary :summary-method="getSummaries">
        <el-table-column prop="date" label="日期" width="110" />
        <el-table-column prop="doc_no" label="单据编号" min-width="160" show-overflow-tooltip />
        <el-table-column label="类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getDocTypeTag(row)" size="small">
              {{ row.doc_type_text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="130" align="right">
          <template #default="{ row }">
            <span :class="getAmountClass(row)">{{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="已结/核销" width="130" align="right">
          <template #default="{ row }">
            <span>{{ formatMoney(row.paid_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="剩余" width="130" align="right">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.remaining > 0 }">{{ formatMoney(row.remaining) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status_text" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status" :type="statusType(row.status)" size="small">{{ row.status_text }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
      </el-table>

      <el-empty v-else-if="!loading && searched" description="暂无数据，请选择往来单位查询" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getStatement, getCounterpartyOptions } from '@/api/finance'

const loading = ref(false)
const searched = ref(false)
const items = ref([])
const summary = ref(null)
const counterpartyOptions = ref([])

const searchForm = reactive({
  counterparty: '',
  dateRange: [],
})

const formatMoney = (v) => {
  if (v === undefined || v === null) return '-'
  return '¥' + Number(v).toFixed(2)
}

const statusType = (s) => ({ unpaid: 'info', partial: 'warning', paid: 'success' }[s] || '')

const getDocTypeTag = (row) => {
  if (row.type === 'receivable_payable') {
    return row.doc_type === 'receivable' ? 'success' : 'warning'
  }
  return row.doc_type === 'receipt' ? 'primary' : 'danger'
}

const getAmountClass = (row) => {
  if (row.type === 'receivable_payable' && row.doc_type === 'receivable') return 'text-receivable'
  if (row.type === 'receivable_payable' && row.doc_type === 'payable') return 'text-payable'
  if (row.type === 'payment_receipt' && row.doc_type === 'receipt') return 'text-receipt'
  if (row.type === 'payment_receipt' && row.doc_type === 'payment') return 'text-payment'
  return ''
}

const getSummaries = (param) => {
  const { columns, data } = param
  const sums = []
  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = '合计'
      return
    }
    if (['date', 'doc_no', 'status_text', 'remark'].includes(column.property)) {
      sums[index] = ''
      return
    }
    const values = data.map(item => Number(item[column.property]) || 0)
    const sum = values.reduce((a, b) => a + b, 0)
    sums[index] = sum !== 0 ? formatMoney(sum) : '-'
  })
  return sums
}

onMounted(async () => {
  try {
    const res = await getCounterpartyOptions()
    counterpartyOptions.value = res.data || []
  } catch (e) {
    // ignore
  }
})

const handleSearch = async () => {
  if (!searchForm.counterparty) {
    ElMessage.warning('请选择往来单位')
    return
  }
  loading.value = true
  searched.value = true
  try {
    const params = { counterparty: searchForm.counterparty }
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.date_from = searchForm.dateRange[0]
      params.date_to = searchForm.dateRange[1]
    }
    const res = await getStatement(params)
    items.value = res.data.items || []
    summary.value = res.data.summary || null
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  searchForm.counterparty = ''
  searchForm.dateRange = []
  items.value = []
  summary.value = null
  searched.value = false
}
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 15px; }
.summary-row { margin-bottom: 20px; }
.summary-card {
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  color: #fff;
}
.summary-card .label { font-size: 13px; margin-bottom: 8px; opacity: 0.9; }
.summary-card .value { font-size: 18px; font-weight: bold; }
.bg-receivable { background: linear-gradient(135deg, #67c23a, #85ce61); }
.bg-receivable-paid { background: linear-gradient(135deg, #409eff, #66b1ff); }
.bg-receivable-unpaid { background: linear-gradient(135deg, #e6a23c, #ebb563); }
.bg-payable { background: linear-gradient(135deg, #f56c6c, #f78989); }
.bg-payable-paid { background: linear-gradient(135deg, #909399, #a6a9ad); }
.bg-payable-unpaid { background: linear-gradient(135deg, #c45656, #d47878); }
.statement-table { margin-top: 10px; }
.text-receivable { color: #67c23a; font-weight: bold; }
.text-payable { color: #f56c6c; font-weight: bold; }
.text-receipt { color: #409eff; font-weight: bold; }
.text-payment { color: #e6a23c; font-weight: bold; }
.text-warning { color: #e6a23c; font-weight: bold; }
</style>
