<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'inventory:transfer:add'" type="primary" @click="handleAdd">新增调拨</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="transfer_no" label="调拨单号" min-width="150" />
        <el-table-column prop="from_warehouse_name" label="调出仓库" min-width="150" />
        <el-table-column prop="to_warehouse_name" label="调入仓库" min-width="150" />
        <el-table-column prop="transfer_date" label="调拨日期" min-width="120" />
        <el-table-column prop="operator_name" label="操作人" min-width="120" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'inventory:transfer:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'inventory:transfer:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="850px" top="5vh">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="调拨单号" prop="transfer_no">
              <el-input v-model="form.transfer_no" placeholder="请输入调拨单号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="调拨日期" prop="transfer_date">
              <el-date-picker v-model="form.transfer_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="调出仓库" prop="from_warehouse">
              <el-select v-model="form.from_warehouse" placeholder="请选择" filterable style="width: 100%">
                <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="调入仓库" prop="to_warehouse">
              <el-select v-model="form.to_warehouse" placeholder="请选择" filterable style="width: 100%">
                <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>

      <div class="sub-title">调拨明细</div>
      <el-table :data="form.items" border size="small">
        <el-table-column label="物料名称" min-width="160">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].material_name" placeholder="物料名称" />
          </template>
        </el-table-column>
        <el-table-column label="规格型号" min-width="120">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].spec" placeholder="规格" />
          </template>
        </el-table-column>
        <el-table-column label="调拨数量" width="110">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].quantity" :min="0" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="单位" width="80">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].unit" placeholder="单位" />
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="120">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].remark" placeholder="备注" />
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTransferList, createTransfer, updateTransfer, deleteTransfer } from '@/api/inventory'
import { getWarehouseOptions } from '@/api/inventory'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10 })
const warehouseOptions = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  transfer_no: '', from_warehouse: null, to_warehouse: null, transfer_date: '', remark: '', items: []
})

const rules = {
  transfer_no: [{ required: true, message: '请输入调拨单号', trigger: 'blur' }],
  transfer_date: [{ required: true, message: '请选择调拨日期', trigger: 'change' }],
  from_warehouse: [{ required: true, message: '请选择调出仓库', trigger: 'change' }],
  to_warehouse: [{ required: true, message: '请选择调入仓库', trigger: 'change' }],
}

const fetchData = async () => {
  const res = await getTransferList(query.value)
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

const resetForm = () => {
  form.value = { transfer_no: '', from_warehouse: null, to_warehouse: null, transfer_date: '', remark: '', items: [] }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增库存调拨'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑库存调拨'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    transfer_no: row.transfer_no,
    from_warehouse: row.from_warehouse,
    to_warehouse: row.to_warehouse,
    transfer_date: row.transfer_date,
    remark: row.remark || '',
    items: row.items ? row.items.map(i => ({ ...i })) : [],
  }
  dialogVisible.value = true
}

const addItem = () => {
  form.value.items.push({ material_name: '', spec: '', quantity: 1, unit: '件', remark: '' })
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
    if (form.value.from_warehouse === form.value.to_warehouse) {
      ElMessage.warning('调出仓库和调入仓库不能相同')
      return
    }
    submitLoading.value = true
    try {
      const payload = { ...form.value }
      if (isEdit.value) {
        await updateTransfer(currentId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createTransfer(payload)
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
  ElMessageBox.confirm(`确定删除调拨单 "${row.transfer_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteTransfer(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
.sub-title { font-weight: bold; margin: 15px 0 8px; }
.add-row-btn { margin-top: 10px; }
</style>
