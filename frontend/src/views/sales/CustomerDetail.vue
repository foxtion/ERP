<template>
  <div class="page-container">
    <!-- 顶部返回 -->
    <div class="page-header">
      <el-button link @click="goBack">
        <el-icon><ArrowLeft /></el-icon> 返回列表
      </el-button>
      <span class="page-title">{{ baseInfo.name || '客户详情' }}</span>
      <el-tag :type="levelType(baseInfo.level)" size="small">{{ levelText(baseInfo.level) }}</el-tag>
      <el-tag :type="baseInfo.is_active ? 'success' : 'info'" size="small" style="margin-left: 8px">
        {{ baseInfo.is_active ? '启用' : '禁用' }}
      </el-tag>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">销售订单数</div>
          <div class="stat-value">{{ stats.order_count || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">订单总金额</div>
          <div class="stat-value" style="color: #409EFF">{{ formatMoney(stats.order_total_amount) }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">出库次数</div>
          <div class="stat-value" style="color: #67C23A">{{ stats.outstock_count || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">退货次数</div>
          <div class="stat-value" style="color: #E6A23C">{{ stats.return_count || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 基本信息 -->
    <el-card class="info-card" v-loading="loading">
      <template #header>
        <span>基本信息</span>
        <el-button v-permission="'sales:customer:edit'" link type="primary" style="float: right" @click="handleEdit">
          编辑
        </el-button>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="客户编码">{{ baseInfo.code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="客户名称">{{ baseInfo.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="客户等级">
          <el-tag :type="levelType(baseInfo.level)" size="small">{{ levelText(baseInfo.level) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="联系人">{{ baseInfo.contact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ baseInfo.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ baseInfo.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="所属行业">{{ baseInfo.industry || '-' }}</el-descriptions-item>
        <el-descriptions-item label="信用额度">{{ formatMoney(baseInfo.credit_limit) }}</el-descriptions-item>
        <el-descriptions-item label="统一社会信用代码">{{ baseInfo.tax_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="允许部分出货">
          <el-tag :type="baseInfo.allow_partial_shipment ? 'success' : 'danger'" size="small">
            {{ baseInfo.allow_partial_shipment ? '允许' : '不允许' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ baseInfo.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="baseInfo.is_active ? 'success' : 'info'" size="small">
            {{ baseInfo.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="银行信息" :span="2">{{ baseInfo.bank_info || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ baseInfo.created_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ baseInfo.updated_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="3">{{ baseInfo.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 最近业务记录 -->
    <el-card class="tabs-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="最近销售订单" name="orders">
          <el-table :data="recentOrders" border stripe size="small">
            <el-table-column prop="order_no" label="订单编号" min-width="150" />
            <el-table-column prop="order_date" label="订单日期" min-width="120" />
            <el-table-column prop="status_display" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="orderStatusType(row.status)" size="small">{{ row.status_display }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_amount" label="总金额" width="120" align="right">
              <template #default="{ row }">
                {{ formatMoney(row.total_amount) }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="recentOrders.length === 0" description="暂无销售订单" />
        </el-tab-pane>

        <el-tab-pane label="最近出库记录" name="outstocks">
          <el-table :data="recentOutstocks" border stripe size="small">
            <el-table-column prop="stock_no" label="出库单号" min-width="150" />
            <el-table-column prop="stock_date" label="出库日期" min-width="120" />
            <el-table-column prop="warehouse" label="出库仓库" min-width="120" />
          </el-table>
          <el-empty v-if="recentOutstocks.length === 0" description="暂无出库记录" />
        </el-tab-pane>

        <el-tab-pane label="最近退货记录" name="returns">
          <el-table :data="recentReturns" border stripe size="small">
            <el-table-column prop="return_no" label="退货单号" min-width="150" />
            <el-table-column prop="return_date" label="退货日期" min-width="120" />
            <el-table-column prop="total_amount" label="退货金额" width="120" align="right">
              <template #default="{ row }">
                {{ formatMoney(row.total_amount) }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="recentReturns.length === 0" description="暂无退货记录" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getCustomerDetailStats, getCustomerStats } from '@/api/sales'

const route = useRoute()
const router = useRouter()
const customerId = route.params.id

const loading = ref(false)
const activeTab = ref('orders')

const baseInfo = ref({})
const stats = ref({})
const recentOrders = ref([])
const recentOutstocks = ref([])
const recentReturns = ref([])

const levelType = (level) => {
  const map = { A: 'danger', B: 'warning', C: '', D: 'info' }
  return map[level] || ''
}

const levelText = (level) => {
  const map = { A: 'A级-VIP', B: 'B级-重要', C: 'C级-普通', D: 'D级-潜在' }
  return map[level] || level
}

const orderStatusType = (status) => {
  const map = { draft: 'info', confirmed: 'primary', partial: 'warning', completed: 'success', cancelled: 'danger' }
  return map[status] || ''
}

const formatMoney = (val) => {
  if (val === null || val === undefined) return '-'
  const num = Number(val)
  if (isNaN(num)) return '-'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const fetchData = async () => {
  loading.value = true
  try {
    const [detailRes, statsRes] = await Promise.all([
      getCustomerDetailStats(customerId),
      getCustomerStats(customerId),
    ])
    const detailData = detailRes.data
    baseInfo.value = detailData.base_info || {}
    recentOrders.value = detailData.recent_orders || []
    recentOutstocks.value = detailData.recent_outstocks || []
    recentReturns.value = detailData.recent_returns || []
    stats.value = statsRes.data || {}
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

const goBack = () => {
  router.back()
}

const handleEdit = () => {
  router.push({ path: '/sales/customers', query: { edit: customerId } })
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  text-align: center;
  padding: 8px 0;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.info-card {
  margin-bottom: 16px;
}

.tabs-card {
  margin-bottom: 16px;
}
</style>
