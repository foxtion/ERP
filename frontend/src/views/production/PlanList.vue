<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索栏 -->
      <div class="toolbar">
        <div class="filter-bar">
          <el-input v-model="query.search" placeholder="计划编号/产品名称" clearable style="width: 220px" @keyup.enter="fetchData" />
          <el-select v-model="query.status" placeholder="状态" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-date-picker
            v-model="query.plan_date__gte"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="计划日期起"
            style="width: 140px"
          />
          <el-date-picker
            v-model="query.plan_date__lte"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="计划日期止"
            style="width: 140px"
          />
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </div>
        <el-button v-permission="'production:plan:add'" type="primary" @click="handleAdd">新增计划</el-button>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="plan_no" label="计划编号" min-width="150" />
        <el-table-column prop="plan_date" label="计划日期" width="110" />
        <el-table-column prop="product_name" label="产品名称" min-width="160" />
        <el-table-column prop="product_code" label="产品编码" min-width="120" />
        <el-table-column prop="quantity" label="计划数量" width="100" align="right" />
        <el-table-column prop="bom_product_name" label="关联BOM" min-width="140">
          <template #default="{ row }">
            <el-tag v-if="row.bom_product_name" size="small" type="info">{{ row.bom_product_name }}</el-tag>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="order_count" label="已下推工单" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.order_count > 0" type="success" size="small">{{ row.order_count }}</el-tag>
            <span v-else style="color: #909399;">0</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="planner_name" label="计划员" width="100" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <!-- 状态流转按钮 -->
            <el-button v-if="row.status === 'draft'" v-permission="'production:plan:edit'" link type="success" @click="handleConfirm(row)">确认</el-button>
            <el-button v-if="row.status === 'confirmed'" v-permission="'production:plan:edit'" link type="success" @click="handleComplete(row)">完成</el-button>
            <el-button v-if="!['completed','cancelled'].includes(row.status)" v-permission="'production:plan:edit'" link type="danger" @click="handleCancel(row)">取消</el-button>
            <!-- 下推按钮 -->
            <el-button v-if="row.status === 'confirmed'" v-permission="'production:order:add'" link type="warning" @click="handleCreateOrder(row)">生成工单</el-button>
            <el-button v-permission="'production:plan:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'production:plan:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="计划编号" prop="plan_no">
          <el-input v-model="form.plan_no" placeholder="留空自动生成，如 JH20250419-001" />
        </el-form-item>
        <el-form-item label="计划日期" prop="plan_date">
          <el-date-picker v-model="form.plan_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="产品名称" prop="product_name">
          <el-input v-model="form.product_name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="产品编码">
          <el-input v-model="form.product_code" placeholder="请输入产品编码" />
        </el-form-item>
        <el-form-item label="计划数量">
          <el-input-number v-model="form.quantity" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="关联BOM">
          <el-select v-model="form.bom" clearable placeholder="请选择BOM" filterable style="width: 100%">
            <el-option v-for="b in bomOptions" :key="b.id" :label="`${b.product_code} - ${b.product_name}`" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="confirmed">已确认</el-radio>
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
    <el-dialog v-model="viewVisible" title="计划详情" width="700px" top="5vh">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="计划编号">{{ viewData.plan_no }}</el-descriptions-item>
        <el-descriptions-item label="计划日期">{{ viewData.plan_date }}</el-descriptions-item>
        <el-descriptions-item label="产品名称">{{ viewData.product_name }}</el-descriptions-item>
        <el-descriptions-item label="产品编码">{{ viewData.product_code }}</el-descriptions-item>
        <el-descriptions-item label="计划数量">{{ viewData.quantity }}</el-descriptions-item>
        <el-descriptions-item label="已下推工单">
          <el-tag :type="viewData.order_count > 0 ? 'success' : 'info'" size="small">{{ viewData.order_count || 0 }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="关联BOM">{{ viewData.bom_product_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(viewData.status)">{{ statusText(viewData.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="计划员">{{ viewData.planner_name || '-' }}</el-descriptions-item>
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
  getPlanList, createPlan, updatePlan, deletePlan,
  confirmPlan, completePlan, cancelPlan, createOrderFromPlan,
  getBomOptions
} from '@/api/production'

const tableData = ref([])
const total = ref(0)
const query = ref({
  page: 1, size: 10, search: '', status: '',
  plan_date__gte: '', plan_date__lte: ''
})
const bomOptions = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  plan_no: '', plan_date: '', product_name: '', product_code: '', quantity: 1, bom: null, status: 'draft', remark: ''
})

const rules = {
  plan_date: [{ required: true, message: '请选择计划日期', trigger: 'change' }],
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
}

const statusText = (s) => ({ draft: '草稿', confirmed: '已确认', completed: '已完成', cancelled: '已取消' }[s] || s)
const statusType = (s) => ({ draft: 'info', confirmed: 'primary', completed: 'success', cancelled: 'danger' }[s] || '')

const fetchData = async () => {
  const params = { ...query.value }
  if (!params.search) delete params.search
  if (!params.status) delete params.status
  if (!params.plan_date__gte) delete params.plan_date__gte
  if (!params.plan_date__lte) delete params.plan_date__lte
  const res = await getPlanList(params)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchBoms = async () => {
  const res = await getBomOptions()
  bomOptions.value = res.data
}

onMounted(() => {
  fetchData()
  fetchBoms()
})

const resetQuery = () => {
  query.value = { page: 1, size: 10, search: '', status: '', plan_date__gte: '', plan_date__lte: '' }
  fetchData()
}

const resetForm = () => {
  form.value = {
    plan_no: '', plan_date: '', product_name: '', product_code: '', quantity: 1, bom: null, status: 'draft', remark: ''
  }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增生产计划'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑生产计划'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    plan_no: row.plan_no,
    plan_date: row.plan_date,
    product_name: row.product_name,
    product_code: row.product_code,
    quantity: row.quantity,
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
        await updatePlan(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createPlan(form.value)
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
  ElMessageBox.confirm(`确定删除计划 "${row.plan_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deletePlan(row.id)
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
const handleConfirm = async (row) => {
  await ElMessageBox.confirm(`确定确认计划 "${row.plan_no}" 吗？确认后计划将生效。`, '确认计划', { type: 'warning' })
  await confirmPlan(row.id)
  ElMessage.success('确认成功')
  await fetchData()
}

const handleComplete = async (row) => {
  await ElMessageBox.confirm(`确定完成计划 "${row.plan_no}" 吗？`, '完成计划', { type: 'warning' })
  await completePlan(row.id)
  ElMessage.success('完成成功')
  await fetchData()
}

const handleCancel = async (row) => {
  await ElMessageBox.confirm(`确定取消计划 "${row.plan_no}" 吗？`, '取消计划', { type: 'warning' })
  await cancelPlan(row.id)
  ElMessage.success('取消成功')
  await fetchData()
}

// 下推生成工单
const handleCreateOrder = async (row) => {
  await ElMessageBox.confirm(`确定根据计划 "${row.plan_no}" 生成生产工单吗？`, '生成工单', { type: 'info' })
  const res = await createOrderFromPlan(row.id)
  ElMessage.success(res.message || '工单生成成功')
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
