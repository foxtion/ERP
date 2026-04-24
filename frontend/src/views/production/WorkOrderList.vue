<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索栏 -->
      <div class="toolbar">
        <div class="filter-bar">
          <el-input v-model="query.search" placeholder="工单编号/产品名称" clearable style="width: 220px" @keyup.enter="fetchData" />
          <el-select v-model="query.status" placeholder="状态" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="已下达" value="released" />
            <el-option label="生产中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-select v-model="query.priority" placeholder="优先级" clearable style="width: 120px">
            <el-option label="紧急" value="urgent" />
            <el-option label="高" value="high" />
            <el-option label="普通" value="normal" />
            <el-option label="低" value="low" />
          </el-select>
          <el-date-picker
            v-model="query.order_date__gte"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="开工日期起"
            style="width: 140px"
          />
          <el-date-picker
            v-model="query.order_date__lte"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="开工日期止"
            style="width: 140px"
          />
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </div>
        <el-button v-permission="'production:order:add'" type="primary" @click="handleAdd">新增工单</el-button>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="order_no" label="工单编号" min-width="150" />
        <el-table-column prop="product_name" label="产品名称" min-width="160" />
        <el-table-column prop="quantity" label="计划数量" width="100" align="right" />
        <el-table-column prop="completed_qty" label="完工数量" width="100" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.completed_qty >= row.quantity ? '#67c23a' : '#e6a23c' }">{{ row.completed_qty }}</span>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="120" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.progress || 0" :stroke-width="10" :status="row.progress >= 100 ? 'success' : ''" />
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="priorityType(row.priority)" size="small">{{ row.priority_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_date" label="开工日期" width="110" />
        <el-table-column prop="actual_start_date" label="实际开工" width="110" />
        <el-table-column prop="actual_end_date" label="实际完工" width="110" />
        <el-table-column prop="plan_no" label="关联计划" min-width="130" />
        <el-table-column prop="bom_product_name" label="关联BOM" min-width="130" />
        <el-table-column prop="operator_name" label="负责人" width="100" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <!-- 状态流转按钮 -->
            <el-button v-if="row.status === 'draft'" v-permission="'production:order:edit'" link type="success" @click="handleRelease(row)">下达</el-button>
            <el-button v-if="row.status === 'released'" v-permission="'production:order:edit'" link type="warning" @click="handleStart(row)">开工</el-button>
            <el-button v-if="row.status === 'processing'" v-permission="'production:order:edit'" link type="success" @click="handleComplete(row)">完工</el-button>
            <el-button v-if="!['completed','cancelled'].includes(row.status)" v-permission="'production:order:edit'" link type="danger" @click="handleCancel(row)">取消</el-button>
            <!-- 下推按钮 -->
            <el-button v-if="['released','processing'].includes(row.status)" v-permission="'production:requisition:add'" link type="primary" @click="handleCreateRequisition(row)">领料</el-button>
            <el-button v-if="['released','processing','completed'].includes(row.status)" v-permission="'production:instock:add'" link type="primary" @click="handleCreateInStock(row)">入库</el-button>
            <el-button v-permission="'production:order:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'production:order:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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
        <el-form-item label="工单编号" prop="order_no">
          <el-input v-model="form.order_no" placeholder="留空自动生成，如 GD20250419-001" />
        </el-form-item>
        <el-form-item label="产品名称" prop="product_name">
          <el-input v-model="form.product_name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="生产数量">
          <el-input-number v-model="form.quantity" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="开工日期" prop="order_date">
          <el-date-picker v-model="form.order_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="form.priority">
            <el-radio label="urgent">紧急</el-radio>
            <el-radio label="high">高</el-radio>
            <el-radio label="normal">普通</el-radio>
            <el-radio label="low">低</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="关联计划">
          <el-select v-model="form.plan" clearable placeholder="请选择生产计划" filterable style="width: 100%">
            <el-option v-for="p in planOptions" :key="p.id" :label="`${p.plan_no} - ${p.product_name}`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联BOM">
          <el-select v-model="form.bom" clearable placeholder="请选择BOM" filterable style="width: 100%">
            <el-option v-for="b in bomOptions" :key="b.id" :label="`${b.product_code} - ${b.product_name}`" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="released">已下达</el-radio>
            <el-radio label="processing">生产中</el-radio>
            <el-radio label="completed">已完成</el-radio>
            <el-radio label="cancelled">已取消</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情弹窗 -->
    <el-dialog v-model="viewVisible" title="工单详情" width="700px" top="5vh">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="工单编号">{{ viewData.order_no }}</el-descriptions-item>
        <el-descriptions-item label="产品名称">{{ viewData.product_name }}</el-descriptions-item>
        <el-descriptions-item label="计划数量">{{ viewData.quantity }}</el-descriptions-item>
        <el-descriptions-item label="完工数量">{{ viewData.completed_qty }}</el-descriptions-item>
        <el-descriptions-item label="进度">
          <el-progress :percentage="viewData.progress || 0" :stroke-width="14" style="width: 150px" />
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="priorityType(viewData.priority)" size="small">{{ viewData.priority_display }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(viewData.status)">{{ statusText(viewData.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="开工日期">{{ viewData.order_date }}</el-descriptions-item>
        <el-descriptions-item label="实际开工">{{ viewData.actual_start_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="实际完工">{{ viewData.actual_end_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="关联计划">{{ viewData.plan_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="关联BOM">{{ viewData.bom_product_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ viewData.operator_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ viewData.created_at }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewData.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getWorkOrderList, createWorkOrder, updateWorkOrder, deleteWorkOrder,
  releaseWorkOrder, startWorkOrder, completeWorkOrder, cancelWorkOrder,
  createRequisitionFromOrder, createInStockFromOrder,
  getPlanList, getBomOptions
} from '@/api/production'

const tableData = ref([])
const total = ref(0)
const query = ref({
  page: 1, size: 10, search: '', status: '', priority: '',
  order_date__gte: '', order_date__lte: ''
})
const planOptions = ref([])
const bomOptions = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  order_no: '', product_name: '', quantity: 1, order_date: '',
  priority: 'normal', plan: null, bom: null, status: 'draft', remark: ''
})

const rules = {
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  order_date: [{ required: true, message: '请选择开工日期', trigger: 'change' }],
}

const statusText = (s) => ({ draft: '草稿', released: '已下达', processing: '生产中', completed: '已完成', cancelled: '已取消' }[s] || s)
const statusType = (s) => ({ draft: 'info', released: 'primary', processing: 'warning', completed: 'success', cancelled: 'danger' }[s])
const priorityType = (p) => ({ urgent: 'danger', high: 'warning', normal: undefined, low: 'info' }[p])

const fetchData = async () => {
  const params = { ...query.value }
  if (!params.search) delete params.search
  if (!params.status) delete params.status
  if (!params.priority) delete params.priority
  if (!params.order_date__gte) delete params.order_date__gte
  if (!params.order_date__lte) delete params.order_date__lte
  const res = await getWorkOrderList(params)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchPlans = async () => {
  const res = await getPlanList({ size: 999 })
  planOptions.value = res.data.list
}

const fetchBoms = async () => {
  const res = await getBomOptions()
  bomOptions.value = res.data
}

onMounted(() => {
  fetchData()
  fetchPlans()
  fetchBoms()
})

const resetQuery = () => {
  query.value = { page: 1, size: 10, search: '', status: '', priority: '', order_date__gte: '', order_date__lte: '' }
  fetchData()
}

const resetForm = () => {
  form.value = {
    order_no: '', product_name: '', quantity: 1, order_date: '',
    priority: 'normal', plan: null, bom: null, status: 'draft', remark: ''
  }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增生产工单'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑生产工单'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    order_no: row.order_no,
    product_name: row.product_name,
    quantity: row.quantity,
    order_date: row.order_date,
    priority: row.priority || 'normal',
    plan: row.plan || null,
    bom: row.bom || null,
    status: row.status,
    remark: row.remark || '',
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (isEdit.value) {
        await updateWorkOrder(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createWorkOrder(form.value)
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
  ElMessageBox.confirm(`确定删除工单 "${row.order_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteWorkOrder(row.id)
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
const handleRelease = async (row) => {
  await ElMessageBox.confirm(`确定下达工单 "${row.order_no}" 吗？`, '确认下达', { type: 'warning' })
  await releaseWorkOrder(row.id)
  ElMessage.success('下达成功')
  await fetchData()
}

const handleStart = async (row) => {
  await ElMessageBox.confirm(`确定开工工单 "${row.order_no}" 吗？`, '确认开工', { type: 'warning' })
  await startWorkOrder(row.id)
  ElMessage.success('开工成功')
  await fetchData()
}

const handleComplete = async (row) => {
  await ElMessageBox.confirm(`确定完工工单 "${row.order_no}" 吗？`, '确认完工', { type: 'warning' })
  await completeWorkOrder(row.id)
  ElMessage.success('完工成功')
  await fetchData()
}

const handleCancel = async (row) => {
  await ElMessageBox.confirm(`确定取消工单 "${row.order_no}" 吗？`, '确认取消', { type: 'warning' })
  await cancelWorkOrder(row.id)
  ElMessage.success('取消成功')
  await fetchData()
}

// 下推领料单
const handleCreateRequisition = async (row) => {
  await ElMessageBox.confirm(`确定根据工单 "${row.order_no}" 生成领料单吗？`, '生成领料单', { type: 'info' })
  const res = await createRequisitionFromOrder(row.id)
  ElMessage.success(res.message || '领料单生成成功')
  await fetchData()
}

// 下推入库单
const handleCreateInStock = async (row) => {
  await ElMessageBox.confirm(`确定根据工单 "${row.order_no}" 生成生产入库单吗？`, '生成入库单', { type: 'info' })
  const res = await createInStockFromOrder(row.id)
  ElMessage.success(res.message || '入库单生成成功')
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
