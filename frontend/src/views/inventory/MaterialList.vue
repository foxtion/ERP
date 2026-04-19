<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'inventory:material:add'" type="primary" @click="handleAdd">新增物料</el-button>
        <div class="filter-bar">
          <el-input v-model="query.search" placeholder="物料编码/名称/规格/条码" clearable style="width: 240px" @keyup.enter="fetchData" />
          <el-select v-model="query.category" placeholder="分类" clearable style="width: 140px">
            <el-option label="硅胶模具" value="硅胶模具" />
            <el-option label="摆件" value="摆件" />
            <el-option label="蜡烛" value="蜡烛" />
            <el-option label="收纳盒" value="收纳盒" />
            <el-option label="托盘" value="托盘" />
            <el-option label="杯垫" value="杯垫" />
            <el-option label="其他" value="其他" />
          </el-select>
          <el-select v-model="query.status" placeholder="状态" clearable style="width: 120px">
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </div>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="code" label="物料编码" min-width="120" />
        <el-table-column prop="name" label="物料名称" min-width="180" />
        <el-table-column prop="spec" label="规格型号" min-width="150" />
        <el-table-column prop="category" label="分类" width="100" align="center" />
        <el-table-column prop="unit" label="单位" width="80" align="center" />
        <el-table-column prop="barcode" label="条码" min-width="120" />
        <el-table-column prop="qty" label="库存数量" width="120" align="right">
          <template #default="{ row }">
            <el-tag :type="Number(row.qty) > 0 ? 'success' : 'info'">{{ Number(row.qty).toFixed(0) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="warning_status_display" label="预警状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="Number(row.qty) <= Number(row.warning_threshold)" type="danger">预警</el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status === 'active' ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'inventory:material:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'inventory:material:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.size"
        :total="total"
        layout="total, sizes, prev, pager, next"
        :page-sizes="[10, 20, 50, 100]"
        class="pagination"
        @current-change="fetchData"
        @size-change="fetchData"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="物料编码" prop="code">
              <el-input v-model="form.code" placeholder="请输入物料编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="物料名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入物料名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规格型号">
              <el-input v-model="form.spec" placeholder="请输入规格型号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
                <el-option label="硅胶模具" value="硅胶模具" />
                <el-option label="摆件" value="摆件" />
                <el-option label="蜡烛" value="蜡烛" />
                <el-option label="收纳盒" value="收纳盒" />
                <el-option label="托盘" value="托盘" />
                <el-option label="杯垫" value="杯垫" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="form.unit" placeholder="如：件、套、个" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="条码">
              <el-input v-model="form.barcode" placeholder="请输入条码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="库存数量">
              <el-input-number v-model="form.qty" :min="0" :precision="0" :controls="false" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预警阈值">
              <el-input-number v-model="form.warning_threshold" :min="0" :precision="0" :controls="false" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">停用</el-radio>
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
import {
  getMaterialList, createMaterial, updateMaterial, deleteMaterial
} from '@/api/inventory'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 20, search: '', category: '', status: '' })

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  code: '', name: '', spec: '', category: '', unit: '件', barcode: '', qty: 0, warning_threshold: 50, status: 'active', remark: ''
})

const rules = {
  code: [{ required: true, message: '请输入物料编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入物料名称', trigger: 'blur' }]
}

const fetchData = async () => {
  const params = { ...query.value }
  if (!params.category) delete params.category
  if (!params.status) delete params.status
  const res = await getMaterialList(params)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

onMounted(fetchData)

const resetQuery = () => {
  query.value = { page: 1, size: 20, search: '', category: '', status: '' }
  fetchData()
}

const resetForm = () => {
  form.value = { code: '', name: '', spec: '', category: '', unit: '件', barcode: '', qty: 0, warning_threshold: 50, status: 'active', remark: '' }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增物料'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑物料'
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form.value, row)
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (isEdit.value) {
        await updateMaterial(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createMaterial(form.value)
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
  ElMessageBox.confirm(`确定删除物料 "${row.name}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteMaterial(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
.filter-bar { display: flex; gap: 10px; align-items: center; }
.pagination { margin-top: 15px; justify-content: flex-end; }
</style>
