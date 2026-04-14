<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'sales:outstock:add'" type="primary" @click="handleAdd">新增出库</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="stock_no" label="出库单号" min-width="150" />
        <el-table-column prop="order_no" label="关联销售订单" min-width="150" />
        <el-table-column prop="stock_date" label="出库日期" min-width="120" />
        <el-table-column prop="warehouse" label="出库仓库" min-width="120" />
        <el-table-column prop="operator_name" label="操作人" min-width="120" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'sales:outstock:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'sales:outstock:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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
            <el-form-item label="出库单号" prop="stock_no">
              <el-input v-model="form.stock_no" placeholder="请输入出库单号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联订单" prop="order">
              <el-select v-model="form.order" placeholder="请选择销售订单" filterable style="width: 100%">
                <el-option v-for="o in orderOptions" :key="o.id" :label="`${o.order_no} - ${o.customer_name}`" :value="o.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出库日期" prop="stock_date">
              <el-date-picker v-model="form.stock_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出库仓库">
              <el-input v-model="form.warehouse" placeholder="请输入仓库" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>

      <div class="sub-title">出库明细</div>
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
        <el-table-column label="出库数量" width="110">
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
import { getOutStockList, createOutStock, updateOutStock, deleteOutStock } from '@/api/sales'
import { getSalesOrderOptions } from '@/api/sales'

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
  stock_no: '', order: null, stock_date: '', warehouse: '默认仓库', remark: '', items: []
})

const rules = {
  stock_no: [{ required: true, message: '请输入出库单号', trigger: 'blur' }],
  order: [{ required: true, message: '请选择销售订单', trigger: 'change' }],
  stock_date: [{ required: true, message: '请选择出库日期', trigger: 'change' }],
}

const fetchData = async () => {
  const res = await getOutStockList(query.value)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchOrders = async () => {
  const res = await getSalesOrderOptions()
  orderOptions.value = res.data
}

onMounted(() => {
  fetchData()
  fetchOrders()
})

const resetForm = () => {
  form.value = { stock_no: '', order: null, stock_date: '', warehouse: '默认仓库', remark: '', items: [] }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增销售出库'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑销售出库'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    stock_no: row.stock_no,
    order: row.order,
    stock_date: row.stock_date,
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
        await updateOutStock(currentId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createOutStock(payload)
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
  ElMessageBox.confirm(`确定删除出库单 "${row.stock_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteOutStock(row.id)
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
