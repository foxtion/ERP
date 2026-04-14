<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'system:dept:add'" type="primary" @click="handleAdd">新增部门</el-button>
      </div>
      <el-table
        :data="tableData"
        row-key="id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        border
        stripe
      >
        <el-table-column prop="name" label="部门名称" min-width="180" />
        <el-table-column prop="code" label="部门编码" min-width="150" />
        <el-table-column prop="sort_order" label="排序" width="100" align="center" />
        <el-table-column prop="remark" label="备注" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'system:dept:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'system:dept:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="上级部门">
          <el-tree-select
            v-model="form.parent"
            :data="treeData"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            check-strictly
            clearable
            placeholder="请选择上级部门"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="部门编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入部门编码" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="3" placeholder="请输入备注" />
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
import { getDeptList, getDeptTree, createDept, updateDept, deleteDept } from '@/api/system'

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
  name: '',
  code: '',
  sort_order: 0,
  remark: '',
})

const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入部门编码', trigger: 'blur' }],
}

const fetchData = async () => {
  const res = await getDeptList()
  tableData.value = res.data
}

const fetchTree = async () => {
  const res = await getDeptTree()
  treeData.value = res.data
}

onMounted(() => {
  fetchData()
  fetchTree()
})

const resetForm = () => {
  form.value = {
    parent: null,
    name: '',
    code: '',
    sort_order: 0,
    remark: '',
  }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增部门'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑部门'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    parent: row.parent || null,
    name: row.name,
    code: row.code,
    sort_order: row.sort_order,
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
        await updateDept(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createDept(form.value)
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
  ElMessageBox.confirm(`确定删除部门 "${row.name}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteDept(row.id)
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
