<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'inventory:location:add'" type="primary" @click="handleAdd">新增库位</el-button>
        <div class="filter-bar">
          <el-select v-model="query.warehouse" placeholder="所属仓库" clearable style="width: 160px">
            <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
          <el-input v-model="query.search" placeholder="库位编码/货物名称/条码" clearable style="width: 220px" @keyup.enter="fetchData" />
          <el-select v-model="query.is_empty" placeholder="库位状态" clearable style="width: 120px">
            <el-option label="有货" :value="false" />
            <el-option label="空位" :value="true" />
          </el-select>
          <el-select v-model="query.location_size" placeholder="库位大小" clearable style="width: 120px">
            <el-option label="小" value="小" />
            <el-option label="中" value="中" />
            <el-option label="大" value="大" />
          </el-select>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </div>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="product_code" label="货物编码" min-width="120" />
        <el-table-column prop="product_name" label="货物名称" min-width="180" />
        <el-table-column prop="barcode" label="条码" min-width="120" />
        <el-table-column prop="location_code" label="库位编码" min-width="120" />
        <el-table-column prop="warehouse_name" label="所属仓库" min-width="120" />
        <el-table-column prop="size" label="大小" width="80" align="center" />
        <el-table-column prop="status_display" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_empty ? 'info' : 'success'">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inbound_time" label="入库时间" min-width="160" />
        <el-table-column prop="outbound_barcode" label="已出库条码" min-width="120" />
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'inventory:location:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'inventory:location:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.size"
        :total="total"
        layout="total, sizes, prev, pager, next"
        :page-sizes="[10, 20, 50, 100]"
        class="pagination"
        @current-change="fetchData"
        @size-change="fetchData"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="所属仓库" prop="warehouse">
          <el-select v-model="form.warehouse" placeholder="请选择仓库" style="width: 100%">
            <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="库位编码" prop="location_code">
          <el-input v-model="form.location_code" placeholder="如 A00F101" />
        </el-form-item>
        <el-form-item label="条码">
          <el-input v-model="form.barcode" placeholder="请输入条码" />
        </el-form-item>
        <el-form-item label="库位大小">
          <el-radio-group v-model="form.size">
            <el-radio label="小">小</el-radio>
            <el-radio label="中">中</el-radio>
            <el-radio label="大">大</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="是否空位">
          <el-radio-group v-model="form.is_empty">
            <el-radio :label="true">空位</el-radio>
            <el-radio :label="false">有货</el-radio>
          </el-radio-group>
        </el-form-item>
        <template v-if="!form.is_empty">
          <el-form-item label="货物编码">
            <el-input v-model="form.product_code" placeholder="请输入货物编码" />
          </el-form-item>
          <el-form-item label="货物名称">
            <el-input v-model="form.product_name" placeholder="请输入货物名称" />
          </el-form-item>
          <el-form-item label="入库时间">
            <el-date-picker v-model="form.inbound_time" type="datetime" placeholder="选择日期时间" style="width: 100%" />
          </el-form-item>
          <el-form-item label="已出库条码">
            <el-input v-model="form.outbound_barcode" placeholder="请输入已出库条码" />
          </el-form-item>
        </template>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getLocationList, createLocation, updateLocation, deleteLocation
} from '@/api/inventory'
import { getWarehouseOptions } from '@/api/inventory'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 20, search: '', warehouse: null, is_empty: null, location_size: null })
const warehouseOptions = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  warehouse: null,
  location_code: '',
  barcode: '',
  size: '小',
  is_empty: true,
  product_code: '',
  product_name: '',
  inbound_time: null,
  outbound_barcode: '',
  remark: ''
})

const rules = {
  warehouse: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  location_code: [{ required: true, message: '请输入库位编码', trigger: 'blur' }]
}

const fetchData = async () => {
  const params = { ...query.value }
  if (!params.warehouse) delete params.warehouse
  if (params.is_empty === null || params.is_empty === '') delete params.is_empty
  if (!params.location_size) delete params.location_size
  const res = await getLocationList(params)
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

const resetQuery = () => {
  query.value = { page: 1, size: 20, search: '', warehouse: null, is_empty: null, location_size: null }
  fetchData()
}

const resetForm = () => {
  form.value = {
    warehouse: null,
    location_code: '',
    barcode: '',
    size: '小',
    is_empty: true,
    product_code: '',
    product_name: '',
    inbound_time: null,
    outbound_barcode: '',
    remark: ''
  }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增库位'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑库位'
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
      const payload = { ...form.value }
      if (!payload.is_empty) {
        if (!payload.inbound_time) delete payload.inbound_time
      } else {
        payload.product_code = ''
        payload.product_name = ''
        payload.inbound_time = null
        payload.outbound_barcode = ''
      }
      if (isEdit.value) {
        await updateLocation(currentId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createLocation(payload)
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
  ElMessageBox.confirm(`确定删除库位 "${row.location_code}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteLocation(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
.filter-bar { display: flex; gap: 10px; align-items: center; }
.pagination { margin-top: 15px; justify-content: flex-end; }
</style>
