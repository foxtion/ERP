<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索筛选 -->
      <el-form :model="query" inline class="search-form">
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="编码/名称/联系人/电话"
            clearable
            style="width: 220px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.is_active" placeholder="全部" clearable style="width: 120px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar">
        <el-button type="primary" @click="handleAdd">新增供应商</el-button>
        <el-button @click="handleExport">导出 Excel</el-button>
        <el-upload
          class="inline-upload"
          action=""
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleImportChange"
          accept=".xlsx,.xls"
        >
          <el-button>导入 Excel</el-button>
        </el-upload>
        <el-button link type="primary" @click="downloadTemplate">下载导入模板</el-button>
      </div>

      <el-table v-loading="tableLoading" :data="tableData" border stripe>
        <el-table-column prop="code" label="供应商编码" min-width="120" />
        <el-table-column prop="name" label="供应商名称" min-width="180" />
        <el-table-column prop="contact" label="联系人" min-width="120" />
        <el-table-column prop="phone" label="联系电话" min-width="130" />
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link :type="row.is_active ? 'warning' : 'success'" @click="handleToggleStatus(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @closed="onDialogClosed">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供应商编码" prop="code">
              <el-input v-model="form.code" :disabled="isEdit" placeholder="请输入编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入名称" />
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
              <el-input v-model="form.phone" placeholder="请输入电话" />
            </el-form-item>
          </el-col>
        </el-row>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getSupplierList, createSupplier, updateSupplier, deleteSupplier,
  toggleSupplierStatus, exportSuppliers, importSuppliers
} from '@/api/purchase'

const tableData = ref([])
const total = ref(0)
const tableLoading = ref(false)
const query = ref({
  page: 1,
  size: 10,
  keyword: '',
  is_active: '',
})

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
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
}

const fetchData = async () => {
  tableLoading.value = true
  try {
    const params = { ...query.value }
    if (params.is_active === '') {
      delete params.is_active
    }
    const res = await getSupplierList(params)
    tableData.value = res.data.list || []
    total.value = res.data.pagination?.total || 0
  } finally {
    tableLoading.value = false
  }
}

onMounted(fetchData)

const handleSearch = () => {
  query.value.page = 1
  fetchData()
}

const handleReset = () => {
  query.value = {
    page: 1,
    size: 10,
    keyword: '',
    is_active: '',
  }
  fetchData()
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

const onDialogClosed = () => {
  formRef.value?.resetFields?.()
  resetForm()
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增供应商'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑供应商'
  isEdit.value = true
  currentId.value = row.id
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
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const payload = { ...form.value }
    if (isEdit.value) {
      await updateSupplier(currentId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createSupplier(payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    await fetchData()
  } finally {
    submitLoading.value = false
  }
}

const handleToggleStatus = async (row) => {
  const actionText = row.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定${actionText}供应商 "${row.name}" 吗？`, '提示', { type: 'warning' })
    await toggleSupplierStatus(row.id)
    ElMessage.success(`${actionText}成功`)
    await fetchData()
  } catch {
    // 取消
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除供应商 "${row.name}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteSupplier(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}

const handleExport = async () => {
  try {
    const params = { ...query.value }
    if (params.is_active === '') {
      delete params.is_active
    }
    delete params.page
    delete params.size
    const res = await exportSuppliers(params)
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `供应商列表_${new Date().toISOString().slice(0, 10)}.xlsx`
    link.click()
    URL.revokeObjectURL(link.href)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleImportChange = async (uploadFile) => {
  if (!uploadFile || !uploadFile.raw) return
  const formData = new FormData()
  formData.append('file', uploadFile.raw)
  try {
    const res = await importSuppliers(formData)
    ElMessage.success(`导入完成，新增 ${res.data.created} 条，更新 ${res.data.updated} 条`)
    if (res.data.errors && res.data.errors.length > 0) {
      console.warn('导入错误:', res.data.errors)
    }
    await fetchData()
  } catch (error) {
    // 错误已由拦截器提示
  }
}

const downloadTemplate = () => {
  const headers = ['供应商编码', '供应商名称', '联系人', '联系电话', '地址', '状态', '备注']
  const rows = [
    headers,
    ['SUP001', '示例科技有限公司', '张三', '13800138000', '北京市朝阳区', '启用', ''],
    ['SUP002', '示例贸易有限公司', '李四', '13900139000', '上海市浦东新区', '启用', '长期合作'],
  ]
  let csvContent = 'data:text/csv;charset=utf-8,\uFEFF'
  rows.forEach((rowArray) => {
    const row = rowArray.map((item) => `"${item}"`).join(',')
    csvContent += row + '\r\n'
  })
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', '供应商导入模板.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}
.search-form {
  margin-bottom: 15px;
}
.toolbar {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.inline-upload {
  display: inline-flex;
}
.pagination {
  margin-top: 15px;
  justify-content: flex-end;
}
</style>
