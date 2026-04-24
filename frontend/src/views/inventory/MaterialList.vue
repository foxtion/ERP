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
        <el-table-column label="大库位" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.large_location">{{ row.large_location }}</span>
            <el-button
              v-if="row.large_location"
              link
              type="danger"
              size="small"
              @click="clearLocation(row, 'large')"
            >删除</el-button>
          </template>
        </el-table-column>
        <el-table-column label="小库位" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.small_location">{{ row.small_location }}</span>
            <el-button
              v-if="row.small_location && isAdmin"
              link
              type="danger"
              size="small"
              @click="clearLocation(row, 'small')"
            >删除</el-button>
          </template>
        </el-table-column>
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
            <el-button
              v-if="isAdmin"
              v-permission="'inventory:material:delete'"
              link
              type="danger"
              @click="handleDelete(row)"
            >删除</el-button>
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
        <el-form-item label="选择库位">
          <el-select-v2
            v-model="selectedLocation"
            :options="locationProductOptions"
            placeholder="搜索库位编码/货物编码/名称/条码"
            clearable
            filterable
            remote
            :remote-method="searchLocationProducts"
            :loading="locationProductLoading"
            style="width: 100%"
            @change="onLocationSelect"
          />
        </el-form-item>
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
            <el-form-item label="大库位">
              <el-select-v2
                v-model="form.large_location"
                :options="largeOptions"
                placeholder="请选择大库位"
                clearable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="小库位">
              <el-select-v2
                v-model="form.small_location"
                :options="smallOptions"
                placeholder="请选择小库位"
                clearable
                style="width: 100%"
              />
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
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
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
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getMaterialList, createMaterial, updateMaterial, patchMaterial, deleteMaterial,
  getLocationOptions, getLocationProducts
} from '@/api/inventory'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.is_superuser)

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 20, search: '', category: '', status: '' })

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const largeLocations = ref([])
const smallLocations = ref([])
const largeOptions = computed(() => largeLocations.value.map(loc => ({ label: loc, value: loc })))
const smallOptions = computed(() => smallLocations.value.map(loc => ({ label: loc, value: loc })))

const selectedLocation = ref(null)
const locationProductOptions = ref([])
const locationProductLoading = ref(false)
const locationProductMap = ref(new Map())

const form = ref({
  code: '', name: '', spec: '', category: '', unit: '件', barcode: '',
  large_location: '', small_location: '',
  qty: 0, warning_threshold: 50, status: 'active', remark: ''
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

const fetchLocations = async () => {
  try {
    const res = await getLocationOptions()
    largeLocations.value = res.data.large || []
    smallLocations.value = res.data.small || []
  } catch (e) {
    // ignore
  }
}

onMounted(() => {
  fetchData()
  fetchLocations()
})

const resetQuery = () => {
  query.value = { page: 1, size: 20, search: '', category: '', status: '' }
  fetchData()
}

const resetForm = () => {
  form.value = {
    code: '', name: '', spec: '', category: '', unit: '件', barcode: '',
    large_location: '', small_location: '',
    qty: 0, warning_threshold: 50, status: 'active', remark: ''
  }
  currentId.value = null
  isEdit.value = false
  selectedLocation.value = null
  locationProductMap.value = new Map()
}

const searchLocationProducts = async (queryStr) => {
  if (!queryStr || queryStr.length < 1) {
    locationProductOptions.value = []
    return
  }
  locationProductLoading.value = true
  try {
    const res = await getLocationProducts({ search: queryStr })
    const list = res.data || []
    locationProductMap.value = new Map(list.map(item => [item.id, item]))
    locationProductOptions.value = list.map(item => ({
      label: `${item.location_code} | ${item.product_code} ${item.product_name}`,
      value: item.id
    }))
  } finally {
    locationProductLoading.value = false
  }
}

const onLocationSelect = (val) => {
  if (!val) return
  const item = locationProductMap.value.get(val)
  if (!item) return
  form.value.code = item.product_code || ''
  form.value.name = item.product_name || ''
  form.value.barcode = item.barcode || ''
  if (item.size === '小') {
    form.value.small_location = item.location_code
    form.value.large_location = ''
  } else {
    form.value.large_location = item.location_code
    form.value.small_location = ''
  }
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
  form.value.code = row.code || ''
  form.value.name = row.name || ''
  form.value.spec = row.spec || ''
  form.value.category = row.category || ''
  form.value.unit = row.unit || '件'
  form.value.barcode = row.barcode || ''
  form.value.large_location = row.large_location || ''
  form.value.small_location = row.small_location || ''
  form.value.qty = Number(row.qty || 0)
  form.value.warning_threshold = Number(row.warning_threshold || 50)
  form.value.status = row.status || 'active'
  form.value.remark = row.remark || ''
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
    } catch (e) {
      console.error('Submit error:', e)
      console.error('Response:', e?.response)
      console.error('Response data:', e?.response?.data)
      console.error('Response status:', e?.response?.status)
      const msg = e?.response?.data?.message || e?.response?.data?.detail || JSON.stringify(e?.response?.data) || e?.message || '提交失败'
      ElMessage.error(msg)
    } finally {
      submitLoading.value = false
    }
  })
}

const clearLocation = async (row, type) => {
  const fieldName = type === 'large' ? '大库位' : '小库位'
  const fieldKey = type === 'large' ? 'large_location' : 'small_location'
  ElMessageBox.confirm(`确定清空${fieldName} "${row[fieldKey]}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await patchMaterial(row.id, { [fieldKey]: null })
    ElMessage.success('清空成功')
    await fetchData()
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
