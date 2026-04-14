<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-select v-model="query.warehouse" clearable placeholder="选择仓库筛选" style="width: 200px; margin-right: 10px" @change="fetchData">
          <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
        </el-select>
        <el-button type="primary" @click="fetchData">查询</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="warehouse_name" label="仓库" min-width="150" />
        <el-table-column prop="material_name" label="物料名称" min-width="180" />
        <el-table-column prop="spec" label="规格型号" min-width="150" />
        <el-table-column prop="unit" label="单位" width="80" align="center" />
        <el-table-column prop="qty" label="库存数量" width="120" align="right">
          <template #default="{ row }">
            <el-tag :type="row.qty > 0 ? 'success' : 'info'">{{ row.qty }}</el-tag>
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
import { getStockList, getWarehouseOptions } from '@/api/inventory'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10, warehouse: null })
const warehouseOptions = ref([])

const fetchData = async () => {
  const params = { ...query.value }
  if (!params.warehouse) delete params.warehouse
  const res = await getStockList(params)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchWarehouses = async () => {
  const res = await getWarehouseOptions()
  warehouseOptions.value = res.data
}

onMounted(() => {
  fetchData()
  fetchWarehouses()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
</style>
