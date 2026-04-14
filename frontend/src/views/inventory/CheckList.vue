<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'inventory:check:add'" type="primary" @click="handleAdd">新增盘点</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="check_no" label="盘点单号" min-width="150" />
        <el-table-column prop="warehouse_name" label="盘点仓库" min-width="150" />
        <el-table-column prop="check_date" label="盘点日期" min-width="120" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'info'">{{ row.status === 'completed' ? '已完成' : '草稿' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator_name" label="操作人" min-width="120" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'inventory:check:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'inventory:check:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="900px" top="5vh">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="盘点单号" prop="check_no">
              <el-input v-model="form.check_no" placeholder="请输入盘点单号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="盘点仓库" prop="warehouse">
              <el-select v-model="form.warehouse" placeholder="请选择仓库" filterable style="width: 100%">
                <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="盘点日期" prop="check_date">
              <el-date-picker v-model="form.check_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="form.status">
                <el-radio label="draft">草稿</el-radio>
                <el-radio label="completed">已完成</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>

      <div class="sub-title">盘点明细</div>
      <el-table :data="form.items" border size="small">
        <el-table-column label="物料名称" min-width="140">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].material_name" placeholder="物料名称" />
          </template>
        </el-table-column>
        <el-table-column label="规格型号" min-width="120">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].spec" placeholder="规格" />
          </template>
        </el-table-column>
        <el-table-column label="单位" width="70">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].unit" placeholder="单位" />
          </template>
        </el-table-column>
        <el-table-column label="账面数量" width="110">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].book_qty" :min="0" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="实盘数量" width="110">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].actual_qty" :min="0" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="差异" width="90" align="right">
          <template #default="{ row }">
            <span :style="{ color: (row.actual_qty - row.book_qty) > 0 ? '#67c23a' : (row.actual_qty - row.book_qty) < 0 ? '#f56c6c' : '#909399' }">
              {{ row.actual_qty - row.book_qty }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="100">
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
import { getCheckList, createCheck, updateCheck, deleteCheck } from '@/api/inventory'
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
  check_no: '', warehouse: null, check_date: '', status: 'draft', remark: '', items: []
})

const rules = {
  check_no: [{ required: true, message: '请输入盘点单号', trigger: 'blur' }],
  warehouse: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  check_date: [{ required: true, message: '请选择盘点日期', trigger: 'change' }],
}

const fetchData = async () => {
  const res = await getCheckList(query.value)
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
  form.value = { check_no: '', warehouse: null, check_date: '', status: 'draft', remark: '', items: [] }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增库存盘点'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑库存盘点'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    check_no: row.check_no,
    warehouse: row.warehouse,
    check_date: row.check_date,
    status: row.status,
    remark: row.remark || '',
    items: row.items ? row.items.map(i => ({ ...i })) : [],
  }
  dialogVisible.value = true
}

const addItem = () => {
  form.value.items.push({ material_name: '', spec: '', unit: '件', book_qty: 0, actual_qty: 0, remark: '' })
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
    submitLoading.value = true
    try {
      const payload = { ...form.value }
      if (isEdit.value) {
        await updateCheck(currentId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createCheck(payload)
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
  ElMessageBox.confirm(`确定删除盘点单 "${row.check_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteCheck(row.id)
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
