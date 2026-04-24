<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索与工具栏 -->
      <div class="toolbar">
        <div class="search-area">
          <el-input
            v-model="query.search"
            placeholder="客户编码/名称/联系人/电话/邮箱"
            clearable
            style="width: 240px; margin-right: 10px"
            @keyup.enter="fetchData"
          />
          <el-select
            v-model="query.level"
            clearable
            placeholder="客户等级"
            style="width: 130px; margin-right: 10px"
            @change="fetchData"
          >
            <el-option label="A级-VIP" value="A" />
            <el-option label="B级-重要" value="B" />
            <el-option label="C级-普通" value="C" />
            <el-option label="D级-潜在" value="D" />
          </el-select>
          <el-input
            v-model="query.industry"
            placeholder="所属行业"
            clearable
            style="width: 140px; margin-right: 10px"
            @keyup.enter="fetchData"
          />
          <el-select
            v-model="query.allow_partial_shipment"
            clearable
            placeholder="部分出货"
            style="width: 130px; margin-right: 10px"
            @change="fetchData"
          >
            <el-option label="允许" :value="true" />
            <el-option label="不允许" :value="false" />
          </el-select>
          <el-select
            v-model="query.is_active"
            clearable
            placeholder="状态"
            style="width: 120px; margin-right: 10px"
            @change="fetchData"
          >
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </div>
        <div class="action-area">
          <el-button v-permission="'sales:customer:view'" type="success" plain @click="handleExport">
            <el-icon><Download /></el-icon> 导出
          </el-button>
          <el-button v-permission="'sales:customer:add'" type="primary" @click="handleAdd">新增客户</el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="code" label="客户编码" min-width="120" />
        <el-table-column prop="name" label="客户名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="contact" label="联系人" min-width="100" />
        <el-table-column prop="phone" label="联系电话" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="160" show-overflow-tooltip />
        <el-table-column prop="industry" label="所属行业" min-width="110" />
        <el-table-column prop="level" label="等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="levelType(row.level)" size="small">
              {{ levelText(row.level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="allow_partial_shipment" label="部分出货" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.allow_partial_shipment ? 'success' : 'danger'" size="small">
              {{ row.allow_partial_shipment ? '允许' : '不允许' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="credit_limit" label="信用额度" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.credit_limit) }}
          </template>
        </el-table-column>
        <el-table-column prop="order_count" label="订单数" width="80" align="center" />
        <el-table-column prop="order_total_amount" label="订单金额" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.order_total_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleDetail(row)">详情</el-button>
            <el-button v-permission="'sales:customer:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'sales:customer:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户编码" prop="code">
              <el-input v-model="form.code" :disabled="isEdit" placeholder="请输入客户编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入客户名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人">
              <el-input v-model="form.contact" placeholder="请输入联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="form.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属行业">
              <el-input v-model="form.industry" placeholder="请输入所属行业" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户等级">
              <el-select v-model="form.level" placeholder="请选择" style="width: 100%">
                <el-option label="A级-VIP" value="A" />
                <el-option label="B级-重要" value="B" />
                <el-option label="C级-普通" value="C" />
                <el-option label="D级-潜在" value="D" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="信用额度">
              <el-input-number v-model="form.credit_limit" :min="0" :precision="2" :controls="false" placeholder="请输入信用额度" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="统一社会信用代码">
              <el-input v-model="form.tax_no" placeholder="请输入统一社会信用代码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="允许部分出货">
              <el-radio-group v-model="form.allow_partial_shipment">
                <el-radio :label="true">允许</el-radio>
                <el-radio :label="false">不允许</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="form.is_active">
                <el-radio :label="true">启用</el-radio>
                <el-radio :label="false">禁用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="地址">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="银行信息">
          <el-input v-model="form.bank_info" placeholder="开户行及账号" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
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
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { getCustomerList, createCustomer, updateCustomer, deleteCustomer, exportCustomers } from '@/api/sales'

const router = useRouter()
const route = useRoute()

// ==================== 表格数据 ====================
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = ref({
  page: 1,
  size: 10,
  search: '',
  level: null,
  industry: '',
  allow_partial_shipment: null,
  is_active: null,
})

// ==================== 新增 / 编辑弹窗 ====================
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  code: '',
  name: '',
  contact: '',
  phone: '',
  email: '',
  address: '',
  industry: '',
  level: 'C',
  credit_limit: 0,
  tax_no: '',
  bank_info: '',
  is_active: true,
  remark: '',
})

const rules = {
  code: [{ required: true, message: '请输入客户编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
}

// ==================== 方法 ====================

const levelType = (level) => {
  const map = { A: 'danger', B: 'warning', C: '', D: 'info' }
  return map[level] || ''
}

const levelText = (level) => {
  const map = { A: 'A级-VIP', B: 'B级-重要', C: 'C级-普通', D: 'D级-潜在' }
  return map[level] || level
}

const formatMoney = (val) => {
  if (val === null || val === undefined) return '-'
  const num = Number(val)
  if (isNaN(num)) return '-'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

/**
 * 获取客户列表
 */
const fetchData = async () => {
  loading.value = true
  try {
    const params = { ...query.value }
    if (!params.search) delete params.search
    if (!params.level) delete params.level
    if (!params.industry) delete params.industry
    if (params.allow_partial_shipment === '' || params.allow_partial_shipment === null) delete params.allow_partial_shipment
    if (params.is_active === '' || params.is_active === null) delete params.is_active
    const res = await getCustomerList(params)
    tableData.value = res.data.list
    total.value = res.data.pagination.total
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData().then(() => {
    // 如果从详情页点击编辑跳转过来，自动打开编辑弹窗
    const editId = route.query.edit
    if (editId) {
      const row = tableData.value.find(item => String(item.id) === String(editId))
      if (row) {
        handleEdit(row)
      }
      // 清除 query 参数，避免刷新后重复打开
      router.replace({ query: {} })
    }
  })
})

/**
 * 重置搜索条件
 */
const handleReset = () => {
  query.value = {
    page: 1,
    size: 10,
    search: '',
    level: null,
    industry: '',
    allow_partial_shipment: null,
    is_active: null,
  }
  fetchData()
}

/**
 * 关闭弹窗后重置表单和校验
 */
const handleDialogClosed = () => {
  formRef.value?.resetFields()
  resetForm()
}

const resetForm = () => {
  form.value = {
    code: '',
    name: '',
    contact: '',
    phone: '',
    email: '',
    address: '',
    industry: '',
    level: 'C',
    credit_limit: 0,
    allow_partial_shipment: false,
    tax_no: '',
    bank_info: '',
    is_active: true,
    remark: '',
  }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增客户'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑客户'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    code: row.code,
    name: row.name,
    contact: row.contact || '',
    phone: row.phone || '',
    email: row.email || '',
    address: row.address || '',
    industry: row.industry || '',
    level: row.level || 'C',
    credit_limit: row.credit_limit || 0,
    allow_partial_shipment: row.allow_partial_shipment || false,
    tax_no: row.tax_no || '',
    bank_info: row.bank_info || '',
    is_active: row.is_active,
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
        await updateCustomer(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createCustomer(form.value)
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
  ElMessageBox.confirm(`确定删除客户 "${row.name}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteCustomer(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}

/**
 * 查看客户详情（跳转到详情页）
 */
const handleDetail = (row) => {
  router.push(`/sales/customer-detail/${row.id}`)
}

/**
 * 导出客户列表
 */
const handleExport = async () => {
  try {
    const params = { ...query.value }
    if (!params.search) delete params.search
    if (!params.level) delete params.level
    if (!params.industry) delete params.industry
    if (params.allow_partial_shipment === '' || params.allow_partial_shipment === null) delete params.allow_partial_shipment
    if (params.is_active === '' || params.is_active === null) delete params.is_active

    const res = await exportCustomers(params)
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `客户列表_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(link.href)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.search-area {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0;
}

.action-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination {
  margin-top: 15px;
  justify-content: flex-end;
}
</style>
