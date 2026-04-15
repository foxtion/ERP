<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索筛选 -->
      <el-form :model="query" inline class="search-form">
        <el-form-item label="关键字">
          <el-input
            v-model="query.search"
            placeholder="用户名/手机号/邮箱"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="所属部门">
          <el-tree-select
            v-model="query.dept"
            :data="deptTreeData"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            check-strictly
            clearable
            placeholder="请选择部门"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.is_active" placeholder="请选择状态" clearable style="width: 150px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD HH:mm:ss"
            :default-time="[new Date(2000, 1, 1, 0, 0, 0), new Date(2000, 1, 1, 23, 59, 59)]"
            style="width: 280px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar">
        <el-button v-permission="'system:user:add'" type="primary" @click="handleAdd">新增用户</el-button>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="phone" label="手机号" min-width="120" />
        <el-table-column prop="dept_name" label="所属部门" min-width="120" />
        <el-table-column prop="role_names" label="角色" min-width="180">
          <template #default="{ row }">
            <el-tag v-for="(name, idx) in row.role_names" :key="idx" size="small" class="role-tag">
              {{ name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'system:user:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'system:user:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="550px" @closed="onDialogClosed">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            :placeholder="isEdit ? '留空表示不修改' : '请输入密码'"
          />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="所属部门">
          <el-tree-select
            v-model="form.dept"
            :data="deptTreeData"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            check-strictly
            clearable
            placeholder="请选择所属部门"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role_ids" multiple placeholder="请选择角色" style="width: 100%">
            <el-option v-for="role in roleList" :key="role.id" :label="role.name" :value="role.id" />
          </el-select>
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
import { getUserList, createUser, updateUser, deleteUser } from '@/api/system'
import { getDeptTree } from '@/api/system'
import { getRoleList } from '@/api/system'

const tableData = ref([])
const total = ref(0)
const query = ref({
  page: 1,
  size: 10,
  search: '',
  dept: null,
  is_active: null,
})
const dateRange = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const deptTreeData = ref([])
const roleList = ref([])

const form = ref({
  username: '',
  password: '',
  email: '',
  phone: '',
  dept: null,
  role_ids: [],
  is_active: true,
  remark: '',
})

const rules = ref({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
})

const fetchData = async () => {
  const params = { ...query.value }
  if (dateRange.value && dateRange.value.length === 2) {
    params.created_at_after = dateRange.value[0]
    params.created_at_before = dateRange.value[1]
  } else {
    params.created_at_after = ''
    params.created_at_before = ''
  }
  const res = await getUserList(params)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchDeptTree = async () => {
  const res = await getDeptTree()
  deptTreeData.value = res.data
}

const fetchRoles = async () => {
  const res = await getRoleList({ size: 999 })
  roleList.value = res.data.list
}

onMounted(() => {
  fetchData()
  fetchDeptTree()
  fetchRoles()
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
    dept: null,
    is_active: null,
  }
  dateRange.value = []
  fetchData()
}

const resetForm = () => {
  form.value = {
    username: '',
    password: '',
    email: '',
    phone: '',
    dept: null,
    role_ids: [],
    is_active: true,
    remark: '',
  }
  currentId.value = null
  isEdit.value = false
}

const onDialogClosed = () => {
  formRef.value?.resetFields()
  resetForm()
  rules.value.password = [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleAdd = () => {
  resetForm()
  rules.value.password = [{ required: true, message: '请输入密码', trigger: 'blur' }]
  dialogTitle.value = '新增用户'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑用户'
  isEdit.value = true
  currentId.value = row.id
  rules.value.password = []
  form.value = {
    username: row.username,
    password: '',
    email: row.email || '',
    phone: row.phone || '',
    dept: row.dept || null,
    role_ids: row.roles || [],
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
      const payload = { ...form.value }
      if (isEdit.value && !payload.password) {
        delete payload.password
      }
      if (isEdit.value) {
        await updateUser(currentId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createUser(payload)
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
  ElMessageBox.confirm(`确定删除用户 "${row.username}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
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
.role-tag {
  margin-right: 5px;
}
</style>
