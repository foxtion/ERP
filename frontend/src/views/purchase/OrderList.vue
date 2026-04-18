<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索筛选区 -->
      <el-form :model="query" inline class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="订单编号/供应商" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="部分入库" value="partial" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="订单日期">
          <el-date-picker
            v-model="query.date_range"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar">
        <el-button :disabled="!hasPermission('purchase:order:add')" type="primary" @click="handleAdd">新增订单</el-button>
        <el-button :disabled="!hasPermission('purchase:order:view')" @click="handleExport">导出 Excel</el-button>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="order_no" label="订单编号" min-width="150" />
        <el-table-column prop="supplier_name" label="供应商" min-width="150" />
        <el-table-column prop="request_no" label="来源申请单" min-width="140" />
        <el-table-column prop="order_date" label="订单日期" min-width="120" />
        <el-table-column prop="delivery_date" label="交货日期" min-width="120" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额" width="120" align="right" />
        <el-table-column prop="purchaser_name" label="采购员" min-width="120" />
        <el-table-column label="操作" width="340" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">详情</el-button>
            <el-button :disabled="!hasPermission('purchase:order:edit') || row.status !== 'draft'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button :disabled="!hasPermission('purchase:order:edit') || row.status !== 'draft'" link type="success" @click="handleConfirm(row)">确认</el-button>
            <el-button :disabled="!hasPermission('purchase:order:delete') || row.status !== 'draft'" link type="danger" @click="handleDelete(row)">删除</el-button>
            <el-button :disabled="!hasPermission('purchase:order:edit') || (row.status !== 'confirmed' && row.status !== 'partial')" link type="warning" @click="handleCancel(row)">取消</el-button>
            <el-button :disabled="!hasPermission('purchase:order:edit') || (row.status !== 'confirmed' && row.status !== 'partial')" link type="success" @click="handleComplete(row)">完成</el-button>
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

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="900px" top="5vh">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="订单编号" prop="order_no">
              <el-input v-model="form.order_no" placeholder="请输入订单编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商" prop="supplier">
              <el-select v-model="form.supplier" placeholder="请选择供应商" filterable style="width: 100%">
                <el-option v-for="s in supplierList" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="订单日期" prop="order_date">
              <el-date-picker v-model="form.order_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="交货日期">
              <el-date-picker v-model="form.delivery_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>

      <div class="sub-title">采购明细</div>
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
        <el-table-column label="数量" width="100">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].quantity" :min="0" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="单位" width="70">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].unit" placeholder="单位" />
          </template>
        </el-table-column>
        <el-table-column label="单价" width="110">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].price" :min="0" :precision="4" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="金额" width="110" align="right">
          <template #default="{ $index }">
            <span>{{ itemAmount(form.items[$index]) }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="isEdit" label="已入库" width="90" align="right">
          <template #default="{ $index }">
            <span>{{ form.items[$index].received_qty || 0 }}</span>
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

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="采购订单详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单编号">{{ detailData.order_no }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ detailData.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="来源申请单">{{ detailData.request_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(detailData.status)">{{ statusText(detailData.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="订单日期">{{ detailData.order_date }}</el-descriptions-item>
        <el-descriptions-item label="交货日期">{{ detailData.delivery_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="总金额">{{ detailData.total_amount }}</el-descriptions-item>
        <el-descriptions-item label="采购员">{{ detailData.purchaser_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailData.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div class="sub-title">采购明细</div>
      <el-table :data="detailData.items" border size="small">
        <el-table-column prop="material_name" label="物料名称" min-width="140" />
        <el-table-column prop="spec" label="规格型号" min-width="120" />
        <el-table-column prop="quantity" label="数量" width="100" align="right" />
        <el-table-column prop="unit" label="单位" width="70" />
        <el-table-column prop="price" label="单价" width="110" align="right" />
        <el-table-column prop="amount" label="金额" width="110" align="right" />
        <el-table-column prop="received_qty" label="已入库" width="90" align="right" />
        <el-table-column prop="remark" label="备注" min-width="120" />
      </el-table>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import {
  getOrderList, createOrder, updateOrder, deleteOrder,
  confirmOrder, cancelOrder, completeOrder, exportOrders, getSupplierList
} from '@/api/purchase'

const userStore = useUserStore()
const hasPermission = (perm) => userStore.hasPermission(perm)

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10, keyword: '', status: '', date_range: null })
const supplierList = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  order_no: '', supplier: null, order_date: '', delivery_date: '', remark: '', items: []
})

const rules = {
  order_no: [{ required: true, message: '请输入订单编号', trigger: 'blur' }],
  supplier: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  order_date: [{ required: true, message: '请选择订单日期', trigger: 'change' }],
}

const statusText = (s) => ({ draft: '草稿', confirmed: '已确认', partial: '部分入库', completed: '已完成', cancelled: '已取消' }[s] || s)
const statusType = (s) => ({ draft: 'info', confirmed: 'primary', partial: 'warning', completed: 'success', cancelled: 'danger' }[s] || '')
const itemAmount = (item) => {
  const qty = Number(item?.quantity || 0)
  const price = Number(item?.price || 0)
  return (qty * price).toFixed(2)
}

const fetchData = async () => {
  const params = { ...query.value }
  if (params.date_range && params.date_range.length === 2) {
    params.order_date_after = params.date_range[0]
    params.order_date_before = params.date_range[1]
  }
  delete params.date_range
  const res = await getOrderList(params)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchSuppliers = async () => {
  const res = await getSupplierList({ size: 999 })
  supplierList.value = res.data.list
}

onMounted(() => {
  fetchData()
  fetchSuppliers()
})

const handleSearch = () => {
  query.value.page = 1
  fetchData()
}

const handleReset = () => {
  query.value = { page: 1, size: 10, keyword: '', status: '', date_range: null }
  fetchData()
}

const resetForm = () => {
  form.value = { order_no: '', supplier: null, order_date: '', delivery_date: '', remark: '', items: [] }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增采购订单'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑采购订单'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    order_no: row.order_no,
    supplier: row.supplier,
    order_date: row.order_date,
    delivery_date: row.delivery_date || '',
    remark: row.remark || '',
    items: row.items ? row.items.map(i => ({ ...i })) : [],
  }
  dialogVisible.value = true
}

const handleView = (row) => {
  detailData.value = { ...row }
  detailVisible.value = true
}

const addItem = () => {
  form.value.items.push({ material_name: '', spec: '', quantity: 1, unit: '件', price: 0, remark: '' })
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
        await updateOrder(currentId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createOrder(payload)
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
  ElMessageBox.confirm(`确定删除订单 "${row.order_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteOrder(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}

const handleConfirm = (row) => {
  ElMessageBox.confirm(`确认订单 "${row.order_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await confirmOrder(row.id)
    ElMessage.success('订单确认成功')
    await fetchData()
  })
}

const handleCancel = (row) => {
  ElMessageBox.confirm(`取消订单 "${row.order_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await cancelOrder(row.id)
    ElMessage.success('订单取消成功')
    await fetchData()
  })
}

const handleComplete = (row) => {
  ElMessageBox.confirm(`手动完成订单 "${row.order_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await completeOrder(row.id)
    ElMessage.success('订单已完成')
    await fetchData()
  })
}

const handleExport = async () => {
  const params = { ...query.value }
  if (params.date_range && params.date_range.length === 2) {
    params.order_date_after = params.date_range[0]
    params.order_date_before = params.date_range[1]
  }
  delete params.date_range
  delete params.page
  delete params.size
  try {
    const res = await exportOrders(params)
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `采购订单_${new Date().toISOString().slice(0,10)}.xlsx`
    link.click()
    URL.revokeObjectURL(link.href)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

// 详情
const detailVisible = ref(false)
const detailData = ref({})
</script>

<style scoped>
.page-container { padding: 20px; }
.search-form { margin-bottom: 15px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
.sub-title { font-weight: bold; margin: 15px 0 8px; }
.add-row-btn { margin-top: 10px; }
</style>
