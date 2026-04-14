<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'production:instock:add'" type="primary" @click="handleAdd">新增入库</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="stock_no" label="入库单号" min-width="150" />
        <el-table-column prop="production_order_no" label="关联工单" min-width="150" />
        <el-table-column prop="product_name" label="产品名称" min-width="180" />
        <el-table-column prop="quantity" label="入库数量" width="120" align="right" />
        <el-table-column prop="stock_date" label="入库日期" min-width="120" />
        <el-table-column prop="warehouse" label="入库仓库" min-width="120" />
        <el-table-column prop="operator_name" label="操作人" min-width="120" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'production:instock:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'production:instock:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="入库单号" prop="stock_no">
          <el-input v-model="form.stock_no" placeholder="请输入入库单号" />
        </el-form-item>
        <el-form-item label="关联工单" prop="production_order">
          <el-select v-model="form.production_order" placeholder="请选择生产工单" filterable style="width: 100%">
            <el-option v-for="o in orderOptions" :key="o.id" :label="`${o.order_no} - ${o.product_name}`" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品名称" prop="product_name">
          <el-input v-model="form.product_name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="入库数量">
          <el-input-number v-model="form.quantity" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="入库日期" prop="stock_date">
          <el-date-picker v-model="form.stock_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="入库仓库">
          <el-input v-model="form.warehouse" placeholder="请输入仓库" />
        </el-form-item>
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
import { getProductionInStockList, createProductionInStock, updateProductionInStock, deleteProductionInStock } from '@/api/production'
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
  stock_no: '', production_order: null, product_name: '', quantity: 1, stock_date: '', warehouse: '默认仓库', remark: ''
})

const rules = {
  stock_no: [{ required: true, message: '请输入入库单号', trigger: 'blur' }],
  production_order: [{ required: true, message: '请选择生产工单', trigger: 'change' }],
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  stock_date: [{ required: true, message: '请选择入库日期', trigger: 'change' }],
}

const fetchData = async () => {
  const res = await getProductionInStockList(query.value)
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
  form.value = { stock_no: '', production_order: null, product_name: '', quantity: 1, stock_date: '', warehouse: '默认仓库', remark: '' }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增生产入库'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑生产入库'
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
      if (isEdit.value) {
        await updateProductionInStock(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createProductionInStock(form.value)
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
  ElMessageBox.confirm(`确定删除入库单 "${row.stock_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteProductionInStock(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
</style>
