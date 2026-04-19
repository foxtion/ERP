<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索栏 -->
      <div class="toolbar">
        <div class="filter-bar">
          <el-input v-model="query.search" placeholder="入库单号/产品名称" clearable style="width: 220px" @keyup.enter="fetchData" />
          <el-select v-model="query.status" placeholder="状态" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已审核" value="approved" />
            <el-option label="已入库" value="confirmed" />
            <el-option label="已关闭" value="closed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-date-picker
            v-model="query.stock_date__gte"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="入库日期起"
            style="width: 140px"
          />
          <el-date-picker
            v-model="query.stock_date__lte"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="入库日期止"
            style="width: 140px"
          />
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </div>
        <el-button v-permission="'production:instock:add'" type="primary" @click="handleAdd">新增入库</el-button>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="stock_no" label="入库单号" min-width="150" />
        <el-table-column prop="production_order_no" label="关联工单" min-width="140" />
        <el-table-column prop="product_name" label="产品名称" min-width="160" />
        <el-table-column prop="quantity" label="入库数量" width="100" align="right" />
        <el-table-column prop="actual_quantity" label="实际入库" width="100" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.actual_quantity > 0 ? '#67c23a' : '#909399' }">{{ row.actual_quantity || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock_date" label="入库日期" width="110" />
        <el-table-column prop="warehouse" label="入库仓库" width="110" />
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator_name" label="操作人" width="100" />
        <el-table-column prop="auditor_name" label="审核人" width="100" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <!-- 状态流转按钮 -->
            <el-button v-if="row.status === 'draft'" v-permission="'production:instock:edit'" link type="success" @click="handleSubmit(row)">提交</el-button>
            <el-button v-if="row.status === 'pending'" v-permission="'production:instock:edit'" link type="success" @click="handleApprove(row)">审核</el-button>
            <el-button v-if="row.status === 'approved'" v-permission="'production:instock:edit'" link type="warning" @click="handleConfirm(row)">入库</el-button>
            <el-button v-if="!['confirmed','closed','cancelled'].includes(row.status)" v-permission="'production:instock:edit'" link type="danger" @click="handleCancel(row)">取消</el-button>
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

    <!-- 编辑/新增弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="650px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="入库单号" prop="stock_no">
          <el-input v-model="form.stock_no" placeholder="留空自动生成，如 RK20250419-001" />
        </el-form-item>
        <el-form-item label="关联工单" prop="production_order">
          <el-select v-model="form.production_order" clearable placeholder="请选择生产工单" filterable style="width: 100%" @change="onOrderChange">
            <el-option v-for="o in orderOptions" :key="o.id" :label="`${o.order_no} - ${o.product_name}`" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品名称" prop="product_name">
          <el-input v-model="form.product_name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="入库数量">
          <el-input-number v-model="form.quantity" :min="0" style="width: 100%" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入库日期" prop="stock_date">
              <el-date-picker v-model="form.stock_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入库仓库">
              <el-input v-model="form.warehouse" placeholder="默认仓库" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="pending">待审核</el-radio>
            <el-radio label="approved">已审核</el-radio>
            <el-radio label="confirmed">已入库</el-radio>
            <el-radio label="cancelled">已取消</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleFormSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情弹窗 -->
    <el-dialog v-model="viewVisible" title="入库单详情" width="700px" top="5vh">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="入库单号">{{ viewData.stock_no }}</el-descriptions-item>
        <el-descriptions-item label="关联工单">{{ viewData.production_order_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="产品名称">{{ viewData.product_name }}</el-descriptions-item>
        <el-descriptions-item label="入库数量">{{ viewData.quantity }}</el-descriptions-item>
        <el-descriptions-item label="实际入库">
          <span :style="{ color: viewData.actual_quantity > 0 ? '#67c23a' : '#909399' }">{{ viewData.actual_quantity || 0 }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(viewData.status)">{{ viewData.status_display }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="入库日期">{{ viewData.stock_date }}</el-descriptions-item>
        <el-descriptions-item label="入库仓库">{{ viewData.warehouse }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ viewData.operator_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审核人">{{ viewData.auditor_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审核时间">{{ viewData.audit_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="入库确认时间">{{ viewData.confirm_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewData.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getProductionInStockList, createProductionInStock, updateProductionInStock, deleteProductionInStock,
  submitProductionInStock, approveProductionInStock, confirmProductionInStock, cancelProductionInStock,
  getWorkOrderOptions
} from '@/api/production'

const tableData = ref([])
const total = ref(0)
const query = ref({
  page: 1, size: 10, search: '', status: '',
  stock_date__gte: '', stock_date__lte: ''
})
const orderOptions = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  stock_no: '', production_order: null, product_name: '', quantity: 1,
  stock_date: '', warehouse: '默认仓库', status: 'draft', remark: ''
})

const rules = {
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  stock_date: [{ required: true, message: '请选择入库日期', trigger: 'change' }],
}

const statusText = (s) => ({
  draft: '草稿', pending: '待审核', approved: '已审核', confirmed: '已入库', closed: '已关闭', cancelled: '已取消'
}[s] || s)
const statusType = (s) => ({ draft: 'info', pending: 'warning', approved: 'primary', confirmed: 'success', closed: '', cancelled: 'danger' }[s] || '')

const fetchData = async () => {
  const params = { ...query.value }
  if (!params.search) delete params.search
  if (!params.status) delete params.status
  if (!params.stock_date__gte) delete params.stock_date__gte
  if (!params.stock_date__lte) delete params.stock_date__lte
  const res = await getProductionInStockList(params)
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

const resetQuery = () => {
  query.value = { page: 1, size: 10, search: '', status: '', stock_date__gte: '', stock_date__lte: '' }
  fetchData()
}

const resetForm = () => {
  form.value = {
    stock_no: '', production_order: null, product_name: '', quantity: 1,
    stock_date: '', warehouse: '默认仓库', status: 'draft', remark: ''
  }
  currentId.value = null
  isEdit.value = false
}

const onOrderChange = (orderId) => {
  if (!orderId) return
  const order = orderOptions.value.find(o => o.id === orderId)
  if (order && !form.value.product_name) {
    form.value.product_name = order.product_name
  }
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
  form.value = {
    stock_no: row.stock_no,
    production_order: row.production_order || null,
    product_name: row.product_name,
    quantity: row.quantity,
    stock_date: row.stock_date,
    warehouse: row.warehouse || '默认仓库',
    status: row.status,
    remark: row.remark || '',
  }
  dialogVisible.value = true
}

const handleFormSubmit = async () => {
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

// 查看详情
const viewVisible = ref(false)
const viewData = ref({})

const handleView = (row) => {
  viewData.value = { ...row }
  viewVisible.value = true
}

// 状态流转
const handleSubmit = async (row) => {
  await ElMessageBox.confirm(`确定提交入库单 "${row.stock_no}" 吗？`, '提交审核', { type: 'warning' })
  await submitProductionInStock(row.id)
  ElMessage.success('提交成功')
  await fetchData()
}

const handleApprove = async (row) => {
  await ElMessageBox.confirm(`确定审核通过入库单 "${row.stock_no}" 吗？`, '审核通过', { type: 'warning' })
  await approveProductionInStock(row.id)
  ElMessage.success('审核通过')
  await fetchData()
}

const handleConfirm = async (row) => {
  await ElMessageBox.confirm(`确定确认入库 "${row.stock_no}" 吗？入库后将增加库存。`, '确认入库', { type: 'warning' })
  await confirmProductionInStock(row.id)
  ElMessage.success('入库确认成功')
  await fetchData()
}

const handleCancel = async (row) => {
  await ElMessageBox.confirm(`确定取消入库单 "${row.stock_no}" 吗？`, '取消入库单', { type: 'warning' })
  await cancelProductionInStock(row.id)
  ElMessage.success('取消成功')
  await fetchData()
}
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar {
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.filter-bar {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.pagination { margin-top: 15px; justify-content: flex-end; }
</style>
