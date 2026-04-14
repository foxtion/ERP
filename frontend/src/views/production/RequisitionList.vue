<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'production:requisition:add'" type="primary" @click="handleAdd">新增领料</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="requisition_no" label="领料单号" min-width="150" />
        <el-table-column prop="production_order_no" label="关联工单" min-width="150" />
        <el-table-column prop="requisition_date" label="领料日期" min-width="120" />
        <el-table-column prop="warehouse" label="领料仓库" min-width="120" />
        <el-table-column prop="operator_name" label="领料人" min-width="120" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'production:requisition:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'production:requisition:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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
            <el-form-item label="领料单号" prop="requisition_no">
              <el-input v-model="form.requisition_no" placeholder="请输入领料单号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联工单" prop="production_order">
              <el-select v-model="form.production_order" placeholder="请选择生产工单" filterable style="width: 100%">
                <el-option v-for="o in orderOptions" :key="o.id" :label="`${o.order_no} - ${o.product_name}`" :value="o.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="领料日期" prop="requisition_date">
              <el-date-picker v-model="form.requisition_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="领料仓库">
              <el-input v-model="form.warehouse" placeholder="请输入仓库" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>

      <div class="sub-title">领料明细</div>
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
        <el-table-column label="领料数量" width="110">
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
import { getRequisitionList, createRequisition, updateRequisition, deleteRequisition } from '@/api/production'
import { getWorkOrderOptions } from '@/api/production'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10 })
const orderOptions = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  requisition_no: '', production_order: null, requisition_date: '', warehouse: '默认仓库', remark: '', items: []
})

const rules = {
  requisition_no: [{ required: true, message: '请输入领料单号', trigger: 'blur' }],
  production_order: [{ required: true, message: '请选择生产工单', trigger: 'change' }],
  requisition_date: [{ required: true, message: '请选择领料日期', trigger: 'change' }],
}

const fetchData = async () => {
  const res = await getRequisitionList(query.value)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchOrders = async () => {
  const res = await getWorkOrderOptions()
  orderOptions.value = res.data
}

onMounted(() => {
  fetchData()
  fetchOrders()
})

const resetForm = () => {
  form.value = { requisition_no: '', production_order: null, requisition_date: '', warehouse: '默认仓库', remark: '', items: [] }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增领料单'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑领料单'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    requisition_no: row.requisition_no,
    production_order: row.production_order,
    requisition_date: row.requisition_date,
    warehouse: row.warehouse,
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
    submitLoading.value = true
    try {
      const payload = { ...form.value }
      if (isEdit.value) {
        await updateRequisition(currentId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createRequisition(payload)
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
  ElMessageBox.confirm(`确定删除领料单 "${row.requisition_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteRequisition(row.id)
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
