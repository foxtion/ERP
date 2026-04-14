<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索与工具栏 -->
      <div class="toolbar">
        <div class="search-area">
          <el-input
            v-model="query.search"
            placeholder="客户编码/名称/联系人/电话"
            clearable
            style="width: 260px; margin-right: 10px"
            @keyup.enter="fetchData"
          />
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
        <el-button v-permission="'sales:customer:add'" type="primary" @click="handleAdd">新增客户</el-button>
      </div>

      <!-- 数据表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="code" label="客户编码" min-width="120" />
        <el-table-column prop="name" label="客户名称" min-width="180" />
        <el-table-column prop="contact" label="联系人" min-width="120" />
        <el-table-column prop="phone" label="联系电话" min-width="130" />
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
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
      width="520px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="客户编码" prop="code">
          <el-input v-model="form.code" :disabled="isEdit" placeholder="请输入客户编码" />
        </el-form-item>
        <el-form-item label="客户名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入客户名称" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.is_active">
            <el-radio :label="true">启用</el-radio>
            <el-radio :label="false">禁用</el-radio>
          </el-radio-group>
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

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="客户详情" width="560px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="客户编码" :span="1">{{ detailData.code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="客户名称" :span="1">{{ detailData.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系人" :span="1">{{ detailData.contact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话" :span="1">{{ detailData.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ detailData.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态" :span="1">
          <el-tag :type="detailData.is_active ? 'success' : 'info'">
            {{ detailData.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailData.remark || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="1">{{ detailData.created_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间" :span="1">{{ detailData.updated_at || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCustomerList, createCustomer, updateCustomer, deleteCustomer } from '@/api/sales'

// ==================== 表格数据 ====================
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = ref({
  page: 1,
  size: 10,
  search: '',
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
  address: '',
  is_active: true,
  remark: '',
})

const rules = {
  code: [{ required: true, message: '请输入客户编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
}

// ==================== 详情弹窗 ====================
const detailVisible = ref(false)
const detailData = ref({})

// ==================== 方法 ====================

/**
 * 获取客户列表
 */
const fetchData = async () => {
  loading.value = true
  try {
    const params = { ...query.value }
    // 将通用搜索字段映射到后端的 search 参数（DRF search_fields 支持多字段模糊搜索）
    if (!params.search) delete params.search
    if (params.is_active === '' || params.is_active === null) delete params.is_active
    const res = await getCustomerList(params)
    tableData.value = res.data.list
    total.value = res.data.pagination.total
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

/**
 * 重置搜索条件
 */
const handleReset = () => {
  query.value = {
    page: 1,
    size: 10,
    search: '',
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
    address: '',
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
  // 回显数据
  form.value = {
    code: row.code,
    name: row.name,
    contact: row.contact || '',
    phone: row.phone || '',
    address: row.address || '',
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
 * 查看客户详情
 */
const handleDetail = (row) => {
  detailData.value = { ...row }
  detailVisible.value = true
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
}

.search-area {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 15px;
  justify-content: flex-end;
}
</style>
