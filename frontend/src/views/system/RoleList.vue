<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索筛选 -->
      <el-form :model="query" inline class="search-form">
        <el-form-item label="关键字">
          <el-input
            v-model="query.search"
            placeholder="角色名称/编码"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar">
        <el-button v-permission="'system:role:add'" type="primary" @click="handleAdd">新增角色</el-button>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="name" label="角色名称" min-width="150" />
        <el-table-column prop="code" label="角色编码" min-width="150" />
        <el-table-column prop="sort_order" label="排序" width="100" align="center" />
        <el-table-column prop="remark" label="备注" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'system:role:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'system:role:edit'" link type="success" @click="handleAssignMenu(row)">分配菜单</el-button>
            <el-button v-permission="'system:role:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- 新增/编辑角色弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" @closed="onDialogClosed">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" :disabled="isEdit" placeholder="请输入角色编码" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" style="width: 100%" />
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

    <!-- 分配菜单弹窗 -->
    <el-dialog v-model="menuDialogVisible" title="分配菜单权限" width="500px">
      <el-tree
        ref="menuTreeRef"
        :data="menuTreeData"
        show-checkbox
        node-key="id"
        :props="{ label: 'title', children: 'children' }"
        default-expand-all
      />
      <template #footer>
        <el-button @click="menuDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="menuSubmitLoading" @click="handleMenuSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRoleList, createRole, updateRole, deleteRole, getRoleMenus, updateRoleMenus } from '@/api/system'
import { getMenuFlat } from '@/api/system'

const tableData = ref([])
const total = ref(0)
const query = ref({
  page: 1,
  size: 10,
  search: '',
})

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  name: '',
  code: '',
  sort_order: 0,
  remark: '',
})

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

const menuDialogVisible = ref(false)
const menuSubmitLoading = ref(false)
const menuTreeRef = ref(null)
const menuTreeData = ref([])
const currentRoleId = ref(null)

const fetchData = async () => {
  const res = await getRoleList({ ...query.value })
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchMenuTree = async () => {
  const res = await getMenuFlat()
  menuTreeData.value = res.data
}

onMounted(() => {
  fetchData()
  fetchMenuTree()
})

const handleSearch = () => {
  query.value.page = 1
  fetchData()
}

const handleReset = () => {
  query.value = {
    page: 1,
    size: 10,
    search: '',
  }
  fetchData()
}

const resetForm = () => {
  form.value = {
    name: '',
    code: '',
    sort_order: 0,
    remark: '',
  }
  currentId.value = null
  isEdit.value = false
}

const onDialogClosed = () => {
  formRef.value?.resetFields()
  resetForm()
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增角色'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑角色'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    name: row.name,
    code: row.code,
    sort_order: row.sort_order,
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
    if (isEdit.value) {
      await updateRole(currentId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await createRole(form.value)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    await fetchData()
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除角色 "${row.name}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}

const handleAssignMenu = async (row) => {
  currentRoleId.value = row.id
  menuDialogVisible.value = true
  try {
    const res = await getRoleMenus(row.id)
    const checkedKeys = res.data.menu_ids
    setTimeout(() => {
      menuTreeRef.value?.setCheckedKeys(checkedKeys)
    }, 100)
  } catch {
    // 错误已在拦截器中提示
  }
}

const handleMenuSubmit = async () => {
  if (!currentRoleId.value) return
  menuSubmitLoading.value = true
  try {
    const checkedKeys = menuTreeRef.value.getCheckedKeys(false)
    const halfCheckedKeys = menuTreeRef.value.getHalfCheckedKeys()
    const menuIds = [...checkedKeys, ...halfCheckedKeys]
    await updateRoleMenus(currentRoleId.value, { menu_ids: menuIds })
    ElMessage.success('菜单权限分配成功')
    menuDialogVisible.value = false
  } finally {
    menuSubmitLoading.value = false
  }
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
}
.pagination {
  margin-top: 15px;
  justify-content: flex-end;
}
</style>
