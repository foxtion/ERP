<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索栏 -->
      <div class="toolbar">
        <div class="filter-bar">
          <el-input v-model="query.search" placeholder="领料单号" clearable style="width: 220px" @keyup.enter="fetchData" />
          <el-select v-model="query.status" placeholder="状态" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已审核" value="approved" />
            <el-option label="已出库" value="issued" />
            <el-option label="已关闭" value="closed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-date-picker
            v-model="query.requisition_date__gte"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="领料日期起"
            style="width: 140px"
          />
          <el-date-picker
            v-model="query.requisition_date__lte"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="领料日期止"
            style="width: 140px"
          />
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </div>
        <el-button v-permission="'production:requisition:add'" type="primary" @click="handleAdd">新增领料</el-button>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="requisition_no" label="领料单号" min-width="150" />
        <el-table-column prop="production_order_no" label="关联工单" min-width="140" />
        <el-table-column prop="requisition_date" label="领料日期" width="110" />
        <el-table-column prop="warehouse" label="领料仓库" width="110" />
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额" width="110" align="right">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold;">{{ Number(row.total_amount || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="operator_name" label="领料人" width="100" />
        <el-table-column prop="auditor_name" label="审核人" width="100" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <!-- 状态流转按钮 -->
            <el-button v-if="row.status === 'draft'" v-permission="'production:requisition:edit'" link type="success" @click="handleSubmit(row)">提交</el-button>
            <el-button v-if="row.status === 'pending'" v-permission="'production:requisition:edit'" link type="success" @click="handleApprove(row)">审核</el-button>
            <el-button v-if="row.status === 'approved'" v-permission="'production:requisition:edit'" link type="warning" @click="handleIssue(row)">出库</el-button>
            <el-button v-if="!['closed','cancelled','issued'].includes(row.status)" v-permission="'production:requisition:edit'" link type="danger" @click="handleCancel(row)">取消</el-button>
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

    <!-- 编辑/新增弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="900px" top="4vh" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="领料单号" prop="requisition_no">
              <el-input v-model="form.requisition_no" placeholder="留空自动生成，如 LL20250419-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联工单" prop="production_order">
              <el-select v-model="form.production_order" clearable placeholder="请选择工单" filterable style="width: 100%">
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
              <el-input v-model="form.warehouse" placeholder="默认仓库" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>

      <div class="sub-title">
        <span>领料明细</span>
        <span class="cost-summary">总金额：{{ totalAmount }} 元</span>
      </div>
      <el-table :data="form.items" border size="small">
        <el-table-column label="物料" min-width="200">
          <template #default="{ $index }">
            <el-select
              v-model="form.items[$index].material"
              placeholder="搜索物料编码/名称"
              clearable
              filterable
              remote
              :remote-method="searchMaterials"
              :loading="materialLoading"
              style="width: 100%"
              @change="(val) => onMaterialChange(val, $index)"
            >
              <el-option
                v-for="item in materialOptions"
                :key="item.id"
                :label="`${item.code} ${item.name}`"
                :value="item.id"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="物料编码" width="120">
          <template #default="{ row }">
            <span style="color: #606266; font-size: 13px;">{{ row.material_code || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="规格" width="120">
          <template #default="{ row }">
            <span style="color: #909399; font-size: 13px;">{{ row.spec || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="领料数量" width="100">
          <template #default="{ $index }">
            <el-input-number
              v-model="form.items[$index].quantity"
              :min="0"
              :controls="false"
              style="width: 100%"
              @change="calcItemSubtotal($index)"
            />
          </template>
        </el-table-column>
        <el-table-column label="单位" width="70">
          <template #default="{ row }">
            <span style="color: #606266; font-size: 13px;">{{ row.unit || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="单价" width="110">
          <template #default="{ $index }">
            <el-input-number
              v-model="form.items[$index].unit_price"
              :min="0"
              :precision="2"
              :controls="false"
              style="width: 100%"
              @change="calcItemSubtotal($index)"
            />
          </template>
        </el-table-column>
        <el-table-column label="小计" width="100" align="right">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold; font-size: 13px;">{{ Number(row.subtotal || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="100">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].remark" placeholder="备注" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="70" align="center">
          <template #default="{ $index }">
            <el-button link type="danger" size="small" @click="removeItem($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button class="add-row-btn" type="primary" plain size="small" @click="addItem">+ 添加明细</el-button>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleFormSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情弹窗 -->
    <el-dialog v-model="viewVisible" title="领料单详情" width="800px" top="5vh">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="领料单号">{{ viewData.requisition_no }}</el-descriptions-item>
        <el-descriptions-item label="关联工单">{{ viewData.production_order_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="领料日期">{{ viewData.requisition_date }}</el-descriptions-item>
        <el-descriptions-item label="领料仓库">{{ viewData.warehouse }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(viewData.status)">{{ viewData.status_display }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总金额">
          <span style="color: #f56c6c; font-weight: bold;">{{ Number(viewData.total_amount || 0).toFixed(2) }} 元</span>
        </el-descriptions-item>
        <el-descriptions-item label="领料人">{{ viewData.operator_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审核人">{{ viewData.auditor_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审核时间">{{ viewData.audit_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="出库时间">{{ viewData.issue_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewData.remark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <div class="sub-title">领料明细</div>
      <el-table :data="viewData.items || []" border size="small">
        <el-table-column prop="material_code" label="物料编码" width="120" />
        <el-table-column prop="material_name" label="物料名称" min-width="160" />
        <el-table-column prop="spec" label="规格" min-width="120" />
        <el-table-column prop="quantity" label="领料数量" width="90" align="right" />
        <el-table-column prop="actual_quantity" label="实发数量" width="90" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.actual_quantity > 0 ? '#67c23a' : '#909399' }">{{ row.actual_quantity || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="70" />
        <el-table-column prop="unit_price" label="单价" width="100" align="right">
          <template #default="{ row }">
            {{ Number(row.unit_price || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="subtotal" label="小计" width="100" align="right">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold;">{{ Number(row.subtotal || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getRequisitionList, createRequisition, updateRequisition, deleteRequisition,
  submitRequisition, approveRequisition, issueRequisition, cancelRequisition,
  getWorkOrderOptions
} from '@/api/production'
import { getMaterialOptions } from '@/api/inventory'

const tableData = ref([])
const total = ref(0)
const query = ref({
  page: 1, size: 10, search: '', status: '',
  requisition_date__gte: '', requisition_date__lte: ''
})
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
  production_order: [{ required: true, message: '请选择关联工单', trigger: 'change' }],
  requisition_date: [{ required: true, message: '请选择领料日期', trigger: 'change' }],
}

const statusText = (s) => ({
  draft: '草稿', pending: '待审核', approved: '已审核', issued: '已出库', closed: '已关闭', cancelled: '已取消'
}[s] || s)
const statusType = (s) => ({ draft: 'info', pending: 'warning', approved: 'primary', issued: 'success', closed: '', cancelled: 'danger' }[s] || '')

// 物料选项
const materialOptions = ref([])
const materialLoading = ref(false)

const totalAmount = computed(() => {
  return form.value.items
    .reduce((sum, item) => sum + (Number(item.quantity) || 0) * (Number(item.unit_price) || 0), 0)
    .toFixed(2)
})

const fetchData = async () => {
  const params = { ...query.value }
  if (!params.search) delete params.search
  if (!params.status) delete params.status
  if (!params.requisition_date__gte) delete params.requisition_date__gte
  if (!params.requisition_date__lte) delete params.requisition_date__lte
  const res = await getRequisitionList(params)
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
  query.value = { page: 1, size: 10, search: '', status: '', requisition_date__gte: '', requisition_date__lte: '' }
  fetchData()
}

const resetForm = () => {
  form.value = {
    requisition_no: '', production_order: null, requisition_date: '', warehouse: '默认仓库', remark: '', items: []
  }
  currentId.value = null
  isEdit.value = false
}

const loadMaterials = async (keyword = '') => {
  materialLoading.value = true
  try {
    const res = await getMaterialOptions({ search: keyword })
    materialOptions.value = res.data || []
  } finally {
    materialLoading.value = false
  }
}

const searchMaterials = async (keyword) => {
  await loadMaterials(keyword)
}

const onMaterialChange = (materialId, index) => {
  const item = form.value.items[index]
  if (!materialId) {
    item.material_name = ''
    item.material_code = ''
    item.spec = ''
    item.unit = ''
    return
  }
  const mat = materialOptions.value.find(m => m.id === materialId)
  if (mat) {
    item.material_name = mat.name
    item.material_code = mat.code
    item.spec = mat.spec || ''
    item.unit = mat.unit || '件'
  }
  calcItemSubtotal(index)
}

const calcItemSubtotal = (index) => {
  const item = form.value.items[index]
  item.subtotal = ((Number(item.quantity) || 0) * (Number(item.unit_price) || 0)).toFixed(2)
}

const handleAdd = async () => {
  resetForm()
  dialogTitle.value = '新增领料单'
  await loadMaterials('')
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  resetForm()
  dialogTitle.value = '编辑领料单'
  isEdit.value = true
  currentId.value = row.id
  await loadMaterials('')
  // 确保当前明细用到的物料在选项列表中
  if (row.items) {
    row.items.forEach(item => {
      if (item.material && !materialOptions.value.find(m => m.id === item.material)) {
        materialOptions.value.push({
          id: item.material,
          code: item.material_code || '',
          name: item.material_name || '',
          spec: item.spec || '',
          unit: item.unit || '',
        })
      }
    })
  }
  form.value = {
    requisition_no: row.requisition_no,
    production_order: row.production_order || null,
    requisition_date: row.requisition_date,
    warehouse: row.warehouse || '默认仓库',
    remark: row.remark || '',
    items: row.items ? row.items.map(i => ({
      ...i,
      quantity: Number(i.quantity),
      unit_price: Number(i.unit_price || 0),
      subtotal: Number(i.subtotal || 0).toFixed(2),
    })) : [],
  }
  dialogVisible.value = true
}

const addItem = () => {
  form.value.items.push({ material: null, material_name: '', material_code: '', spec: '', quantity: 1, unit: '件', unit_price: 0, subtotal: '0.00', remark: '' })
}

const removeItem = (index) => {
  form.value.items.splice(index, 1)
}

const handleFormSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    const items = form.value.items
      .filter(i => i.material_name || i.material)
      .map(i => ({
        material: i.material,
        material_name: i.material_name,
        spec: i.spec,
        quantity: i.quantity,
        unit: i.unit,
        unit_price: i.unit_price,
        remark: i.remark,
      }))
    if (items.length === 0) {
      ElMessage.warning('请至少添加一条领料明细')
      return
    }
    submitLoading.value = true
    try {
      const payload = { ...form.value, items }
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

// 查看详情
const viewVisible = ref(false)
const viewData = ref({})

const handleView = (row) => {
  viewData.value = { ...row }
  viewVisible.value = true
}

// 状态流转
const handleSubmit = async (row) => {
  await ElMessageBox.confirm(`确定提交领料单 "${row.requisition_no}" 吗？`, '提交审核', { type: 'warning' })
  await submitRequisition(row.id)
  ElMessage.success('提交成功')
  await fetchData()
}

const handleApprove = async (row) => {
  await ElMessageBox.confirm(`确定审核通过领料单 "${row.requisition_no}" 吗？`, '审核通过', { type: 'warning' })
  await approveRequisition(row.id)
  ElMessage.success('审核通过')
  await fetchData()
}

const handleIssue = async (row) => {
  await ElMessageBox.confirm(`确定出库领料单 "${row.requisition_no}" 吗？出库后将扣减库存。`, '确认出库', { type: 'warning' })
  await issueRequisition(row.id)
  ElMessage.success('出库成功')
  await fetchData()
}

const handleCancel = async (row) => {
  await ElMessageBox.confirm(`确定取消领料单 "${row.requisition_no}" 吗？`, '取消领料单', { type: 'warning' })
  await cancelRequisition(row.id)
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
.sub-title {
  font-weight: bold;
  margin: 15px 0 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.cost-summary {
  color: #f56c6c;
  font-size: 15px;
}
.add-row-btn { margin-top: 10px; }
</style>
