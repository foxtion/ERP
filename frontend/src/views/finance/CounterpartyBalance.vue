<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-form :model="searchForm" inline>
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              value-format="YYYY-MM-DD"
              range-separator="~"
              start-placeholder="开始"
              end-placeholder="结束"
              style="width: 260px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 汇总 -->
      <el-row v-if="summary" :gutter="16" class="summary-row">
        <el-col :span="6">
          <div class="summary-card bg-receivable">
            <div class="label">期初应收合计</div>
            <div class="value">{{ formatMoney(summary.total_opening_receivable) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-card bg-receivable-unpaid">
            <div class="label">期末应收合计</div>
            <div class="value">{{ formatMoney(summary.total_closing_receivable) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-card bg-payable">
            <div class="label">期初应付合计</div>
            <div class="value">{{ formatMoney(summary.total_opening_payable) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-card bg-payable-unpaid">
            <div class="label">期末应付合计</div>
            <div class="value">{{ formatMoney(summary.total_closing_payable) }}</div>
          </div>
        </el-col>
      </el-row>

      <el-table :data="tableData" border stripe v-loading="loading" show-summary :summary-method="getSummaries">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="counterparty" label="往来单位" min-width="180" show-overflow-tooltip />
        <el-table-column label="期初应收" width="130" align="right">
          <template #default="{ row }">
            <span v-if="row.opening_receivable > 0" class="text-receivable">{{ formatMoney(row.opening_receivable) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="期初应付" width="130" align="right">
          <template #default="{ row }">
            <span v-if="row.opening_payable > 0" class="text-payable">{{ formatMoney(row.opening_payable) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="本期应收" width="130" align="right">
          <template #default="{ row }">
            <span v-if="row.period_receivable > 0" class="text-receivable">{{ formatMoney(row.period_receivable) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="本期收款" width="130" align="right">
          <template #default="{ row }">
            <span v-if="row.period_receipt > 0">{{ formatMoney(row.period_receipt) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="本期应付" width="130" align="right">
          <template #default="{ row }">
            <span v-if="row.period_payable > 0" class="text-payable">{{ formatMoney(row.period_payable) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="本期付款" width="130" align="right">
          <template #default="{ row }">
            <span v-if="row.period_payment > 0">{{ formatMoney(row.period_payment) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="期末应收" width="130" align="right">
          <template #default="{ row }">
            <span v-if="row.closing_receivable > 0" class="text-receivable">{{ formatMoney(row.closing_receivable) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="期末应付" width="130" align="right">
          <template #default="{ row }">
            <span v-if="row.closing_payable > 0" class="text-payable">{{ formatMoney(row.closing_payable) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="净余额" width="130" align="right" fixed="right">
          <template #default="{ row }">
            <span :class="row.net_balance > 0 ? 'text-receivable' : row.net_balance < 0 ? 'text-payable' : 'text-muted'">
              {{ formatMoney(row.net_balance) }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && tableData.length === 0 && searched" description="暂无数据，请选择日期范围查询" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { getBalanceSheet } from '@/api/finance'

const loading = ref(false)
const searched = ref(false)
const tableData = ref([])
const summary = ref(null)

const searchForm = reactive({
  dateRange: [],
})

const formatMoney = (v) => {
  if (v === undefined || v === null) return '-'
  return '¥' + Number(v).toFixed(2)
}

const handleSearch = async () => {
  if (!searchForm.dateRange || searchForm.dateRange.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }
  loading.value = true
  searched.value = true
  try {
    const res = await getBalanceSheet({
      date_from: searchForm.dateRange[0],
      date_to: searchForm.dateRange[1],
    })
    tableData.value = res.data || []
    // 计算汇总
    const s = {
      total_opening_receivable: 0,
      total_opening_payable: 0,
      total_closing_receivable: 0,
      total_closing_payable: 0,
    }
    for (const row of tableData.value) {
      s.total_opening_receivable += row.opening_receivable || 0
      s.total_opening_payable += row.opening_payable || 0
      s.total_closing_receivable += row.closing_receivable || 0
      s.total_closing_payable += row.closing_payable || 0
    }
    summary.value = s
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  searchForm.dateRange = []
  tableData.value = []
  summary.value = null
  searched.value = false
}

const getSummaries = (param) => {
  const { columns, data } = param
  const sums = []
  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = '合计'
      return
    }
    if (index === 1) {
      sums[index] = `${data.length} 家`
      return
    }
    const values = data.map(item => Number(item[column.property]) || 0)
    const sum = values.reduce((a, b) => a + b, 0)
    sums[index] = sum !== 0 ? formatMoney(sum) : '-'
  })
  return sums
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
.bg-receivable-unpaid { background: linear-gradient(135deg, #e6a23c, #ebb563); }
.bg-payable { background: linear-gradient(135deg, #f56c6c, #f78989); }
.bg-payable-unpaid { background: linear-gradient(135deg, #c45656, #d47878); }
.text-receivable { color: #67c23a; font-weight: bold; }
.text-payable { color: #f56c6c; font-weight: bold; }
.text-muted { color: #909399; }
</style>
