<template>
  <div class="page-container">
    <!-- 统计卡片 -->
    <el-row :gutter="15" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">总库存量</div>
          <div class="stat-value">{{ stats.total_qty }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">物料种类</div>
          <div class="stat-value">{{ stats.material_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">涉及仓库</div>
          <div class="stat-value">{{ stats.warehouse_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card warning">
          <div class="stat-title">零库存</div>
          <div class="stat-value">{{ stats.zero_count }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="table-card">
      <div class="toolbar">
        <div class="filter-bar">
          <el-select v-model="query.warehouse" clearable placeholder="选择仓库筛选" style="width: 180px" @change="handleSearch">
            <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
          <el-input v-model="query.search" placeholder="物料编码/名称/规格" clearable style="width: 220px" @keyup.enter="handleSearch" />
          <el-select v-model="query.warning" clearable placeholder="预警状态" style="width: 140px" @change="handleSearch">
            <el-option label="仅看预警" value="true" />
            <el-option label="全部" value="" />
          </el-select>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </div>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="warehouse_name" label="仓库" min-width="140" />
        <el-table-column prop="material_code" label="物料编码" min-width="120" />
        <el-table-column prop="material_name" label="物料名称" min-width="180" />
        <el-table-column prop="spec" label="规格型号" min-width="150" />
        <el-table-column prop="unit" label="单位" width="80" align="center" />
        <el-table-column prop="qty" label="库存数量" width="120" align="right" sortable>
          <template #default="{ row }">
            <el-tag :type="qtyTagType(row.qty, row.warning_status)">{{ Number(row.qty).toFixed(0) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="warning_status_display" label="预警状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.warning_status === 'warning'" type="danger">预警</el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" min-width="160" />
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getStockList, getStockStats, getWarehouseOptions } from '@/api/inventory'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10, warehouse: null, search: '', warning: '' })
const warehouseOptions = ref([])

const stats = ref({
  total_qty: 0,
  material_count: 0,
  warehouse_count: 0,
  zero_count: 0,
})

const fetchData = async () => {
  const params = { ...query.value }
  if (!params.warehouse) delete params.warehouse
  if (!params.search) delete params.search
  if (!params.warning) delete params.warning
  const res = await getStockList(params)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchStats = async () => {
  const params = {}
  if (query.value.warehouse) params.warehouse = query.value.warehouse
  if (query.value.search) params.search = query.value.search
  const res = await getStockStats(params)
  stats.value = res.data
}

const handleSearch = () => {
  query.value.page = 1
  fetchData()
  fetchStats()
}

const resetQuery = () => {
  query.value = { page: 1, size: 10, warehouse: null, search: '', warning: '' }
  fetchData()
  fetchStats()
}

const fetchWarehouses = async () => {
  const res = await getWarehouseOptions()
  warehouseOptions.value = res.data
}

const qtyTagType = (qty, warningStatus) => {
  const q = Number(qty)
  if (q === 0) return 'danger'
  if (warningStatus === 'warning' || q <= 50) return 'warning'
  if (q < 10) return 'warning'
  return 'success'
}

onMounted(() => {
  fetchData()
  fetchStats()
  fetchWarehouses()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.stats-row { margin-bottom: 15px; }
.stat-card { text-align: center; }
.stat-card .stat-title { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-card .stat-value { font-size: 28px; font-weight: bold; color: #303133; }
.stat-card.warning .stat-value { color: #f56c6c; }
.table-card { margin-top: 0; }
.toolbar { margin-bottom: 15px; display: flex; justify-content: flex-start; }
.filter-bar { display: flex; gap: 10px; align-items: center; }
.pagination { margin-top: 15px; justify-content: flex-end; }
</style>
