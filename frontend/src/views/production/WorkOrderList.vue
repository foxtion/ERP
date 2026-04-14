<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'production:order:add'" type="primary" @click="handleAdd">新增工单</el-button>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="order_no" label="工单编号" min-width="150" />
        <el-table-column prop="product_name" label="产品名称" min-width="180" />
        <el-table-column prop="quantity" label="生产数量" width="120" align="right" />
        <el-table-column prop="order_date" label="开工日期" min-width="120" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="plan_no" label="关联计划" min-width="150" />
        <el-table-column prop="bom_product_name" label="关联BOM" min-width="150" />
        <el-table-column prop="operator_name" label="负责人" min-width="120" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="工单编号" prop="order_no">
          <el-input v-model="form.order_no" placeholder="请输入工单编号" />
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
import { getWorkOrderList, createWorkOrder, updateWorkOrder, deleteWorkOrder } from '@/api/production'
import { getPlanList } from '@/api/production'
import { getBomOptions } from '@/api/production'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10 })
const planOptions = ref([])
const bomOptions = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  order_no: '', product_name: '', quantity: 1, order_date: '', plan: null, bom: null, status: 'draft', remark: ''
})

const rules = {
  order_no: [{ required: true, message: '请输入工单编号', trigger: 'blur' }],
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  order_date: [{ required: true, message: '请选择开工日期', trigger: 'change' }],
}

const statusText = (s) => ({ draft: '草稿', released: '已下达', processing: '生产中', completed: '已完成', cancelled: '已取消' }[s] || s)
const statusType = (s) => ({ draft: 'info', released: 'primary', processing: 'warning', completed: 'success', cancelled: 'danger' }[s] || '')

const fetchData = async () => {
  const res = await getWorkOrderList(query.value)
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

const resetForm = () => {
  form.value = { order_no: '', product_name: '', quantity: 1, order_date: '', plan: null, bom: null, status: 'draft', remark: '' }
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
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
</style>
