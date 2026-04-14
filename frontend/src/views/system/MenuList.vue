<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'system:menu:add'" type="primary" @click="handleAdd">新增菜单</el-button>
      </div>
      <el-table
        :data="tableData"
        row-key="id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        border
        stripe
      >
        <el-table-column prop="title" label="菜单标题" min-width="160" />
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="menu_type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.menu_type === 'DIR'">目录</el-tag>
            <el-tag v-else-if="row.menu_type === 'MENU'" type="success">菜单</el-tag>
            <el-tag v-else type="warning">按钮</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路由路径" min-width="150" />
        <el-table-column prop="component" label="组件路径" min-width="180" show-overflow-tooltip />
        <el-table-column prop="permission" label="权限标识" min-width="150" />
        <el-table-column prop="icon" label="图标" width="100" align="center" />
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'system:menu:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'system:menu:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="上级菜单">
          <el-tree-select
            v-model="form.parent"
            :data="treeData"
            :props="{ label: 'title', value: 'id', children: 'children' }"
            check-strictly
            clearable
            placeholder="请选择上级菜单"
            style="width: 100%"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="菜单类型" prop="menu_type">
              <el-select v-model="form.menu_type" placeholder="请选择类型" style="width: 100%">
                <el-option label="目录" value="DIR" />
                <el-option label="菜单" value="MENU" />
                <el-option label="按钮" value="BUTTON" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="form.sort_order" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="菜单标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入菜单标题" />
        </el-form-item>
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入菜单名称（路由name）" />
        </el-form-item>
        <el-form-item label="路由路径">
          <el-input v-model="form.path" placeholder="请输入路由路径" />
        </el-form-item>
        <el-form-item label="组件路径">
          <el-input v-model="form.component" placeholder="如 system/UserList.vue" />
        </el-form-item>
        <el-form-item label="权限标识">
          <el-input v-model="form.permission" placeholder="如 system:user:view" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="form.icon" placeholder="Element Plus 图标名称" />
        </el-form-item>
        <el-form-item label="是否隐藏">
          <el-radio-group v-model="form.is_hidden">
            <el-radio :label="false">显示</el-radio>
            <el-radio :label="true">隐藏</el-radio>
          </el-radio-group>
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
import { getMenuList, getMenuTree, createMenu, updateMenu, deleteMenu } from '@/api/system'

const tableData = ref([])
const treeData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  parent: null,
  menu_type: 'MENU',
  title: '',
  name: '',
  path: '',
  component: '',
  permission: '',
  icon: '',
  sort_order: 0,
  is_hidden: false,
})

const rules = {
  menu_type: [{ required: true, message: '请选择菜单类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入菜单标题', trigger: 'blur' }],
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
}

const fetchData = async () => {
  const res = await getMenuList()
  tableData.value = res.data
}

const fetchTree = async () => {
  const res = await getMenuTree()
  treeData.value = res.data
}

onMounted(() => {
  fetchData()
  fetchTree()
})

const resetForm = () => {
  form.value = {
    parent: null,
    menu_type: 'MENU',
    title: '',
    name: '',
    path: '',
    component: '',
    permission: '',
    icon: '',
    sort_order: 0,
    is_hidden: false,
  }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增菜单'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑菜单'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    parent: row.parent || null,
    menu_type: row.menu_type,
    title: row.title,
    name: row.name,
    path: row.path || '',
    component: row.component || '',
    permission: row.permission || '',
    icon: row.icon || '',
    sort_order: row.sort_order,
    is_hidden: row.is_hidden,
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
        await updateMenu(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createMenu(form.value)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      await fetchData()
      await fetchTree()
    } finally {
      submitLoading.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除菜单 "${row.title}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteMenu(row.id)
    ElMessage.success('删除成功')
    await fetchData()
    await fetchTree()
  })
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 15px;
}
</style>
