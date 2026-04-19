<template>
  <div class="page-container">
    <!-- 统计卡片 -->
    <el-row :gutter="15" class="stats-row">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card danger">
          <div class="stat-title">未处理预警</div>
          <div class="stat-value">{{ stats.unhandled }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card warning">
          <div class="stat-title">一般预警</div>
          <div class="stat-value">{{ stats.warning }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card danger">
          <div class="stat-title">紧急预警</div>
          <div class="stat-value">{{ stats.urgent }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="table-card">
      <div class="toolbar">
        <div class="filter-bar">
          <el-input v-model="query.search" placeholder="物料名称" clearable style="width: 220px" @keyup.enter="fetchData" />
          <el-select v-model="query.status" placeholder="预警级别" clearable style="width: 140px">
            <el-option label="预警" value="warning" />
            <el-option label="紧急" value="urgent" />
          </el-select>
          <el-select v-model="query.is_handled" placeholder="处理状态" clearable style="width: 140px">
            <el-option label="未处理" :value="false" />
            <el-option label="已处理" :value="true" />
          </el-select>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </div>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="material_code" label="物料编码" min-width="140" />
        <el-table-column prop="material_name" label="物料名称" min-width="180" />
        <el-table-column prop="warehouse_name" label="仓库" min-width="120" />
        <el-table-column prop="current_qty" label="当前数量" width="110" align="right">
          <template #default="{ row }">
            <el-tag type="danger">{{ Number(row.current_qty).toFixed(0) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="预警阈值" width="110" align="right">
          <template #default="{ row }">
            {{ Number(row.threshold).toFixed(0) }}
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="级别" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'urgent' ? 'danger' : 'warning'">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_handled" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_handled ? 'success' : 'info'">{{ row.is_handled ? '已处理' : '未处理' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
        <el-table-column prop="created_at" label="预警时间" min-width="160" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!row.is_handled" link type="primary" @click="handleMark(row)">标记处理</el-button>
            <span v-else style="color: #909399; font-size: 12px;">已处理</span>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getWarningList, handleWarning, getWarningStats } from '@/api/inventory'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10, search: '', status: '', is_handled: null })

const stats = ref({
  unhandled: 0,
  warning: 0,
  urgent: 0,
})

const fetchData = async () => {
  const params = { ...query.value }
  if (!params.search) delete params.search
  if (!params.status) delete params.status
  if (params.is_handled === null || params.is_handled === '') delete params.is_handled
  const res = await getWarningList(params)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchStats = async () => {
  const res = await getWarningStats()
  stats.value = res.data
}

const resetQuery = () => {
  query.value = { page: 1, size: 10, search: '', status: '', is_handled: null }
  fetchData()
}

const handleMark = async (row) => {
  await handleWarning(row.id)
  ElMessage.success('已标记为处理')
  await fetchData()
  await fetchStats()
}

onMounted(() => {
  fetchData()
  fetchStats()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.stats-row { margin-bottom: 15px; }
.stat-card { text-align: center; }
.stat-card .stat-title { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-card .stat-value { font-size: 28px; font-weight: bold; color: #303133; }
.stat-card.danger .stat-value { color: #f56c6c; }
.stat-card.warning .stat-value { color: #e6a23c; }
.table-card { margin-top: 0; }
.toolbar { margin-bottom: 15px; display: flex; justify-content: flex-start; }
.filter-bar { display: flex; gap: 10px; align-items: center; }
.pagination { margin-top: 15px; justify-content: flex-end; }
</style>
