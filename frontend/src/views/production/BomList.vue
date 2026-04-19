<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索栏 -->
      <div class="toolbar">
        <div class="filter-bar">
          <el-input v-model="query.search" placeholder="产品编码/名称" clearable style="width: 220px" @keyup.enter="fetchData" />
          <el-select v-model="query.is_active" placeholder="状态" clearable style="width: 120px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </div>
        <el-button v-permission="'production:bom:add'" type="primary" @click="handleAdd">新增BOM</el-button>
      </div>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="product_code" label="产品编码" min-width="120" />
        <el-table-column prop="product_name" label="产品名称" min-width="180" />
        <el-table-column prop="version" label="版本" width="100" align="center" />
        <el-table-column prop="total_cost" label="总成本" width="120" align="right">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold;">{{ Number(row.total_cost || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button v-permission="'production:bom:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'production:bom:add'" link type="warning" @click="handleCopy(row)">复制</el-button>
            <el-button v-permission="'production:bom:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- 编辑/新增弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="960px" top="4vh" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="产品编码" prop="product_code">
              <el-input v-model="form.product_code" placeholder="请输入产品编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品名称" prop="product_name">
              <el-input v-model="form.product_name" placeholder="请输入产品名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="版本">
              <el-input v-model="form.version" placeholder="如 V1.0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="form.is_active">
                <el-radio :label="true">启用</el-radio>
                <el-radio :label="false">禁用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>

      <div class="sub-title">
        <span>BOM明细</span>
        <span class="cost-summary">总成本：{{ totalCost }} 元</span>
      </div>
      <el-table :data="form.items" border size="small">
        <el-table-column label="物料" min-width="200">
          <template #default="{ $index }">
            <el-select
              v-model="form.items[$index].material"
              placeholder="搜索物料编码/名称"
              clearable
              filterable
              remote
              :remote-method="searchMaterials"
              :loading="materialLoading"
              style="width: 100%"
              @change="(val) => onMaterialChange(val, $index)"
            >
              <el-option
                v-for="item in materialOptions"
                :key="item.id"
                :label="`${item.code} ${item.name}`"
                :value="item.id"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="物料编码" width="120">
          <template #default="{ row }">
            <span style="color: #606266; font-size: 13px;">{{ row.material_code || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="规格" width="120">
          <template #default="{ row }">
            <span style="color: #909399; font-size: 13px;">{{ row.spec || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="用量" width="100">
          <template #default="{ $index }">
            <el-input-number
              v-model="form.items[$index].quantity"
              :min="0"
              :controls="false"
              style="width: 100%"
              @change="calcItemSubtotal($index)"
            />
          </template>
        </el-table-column>
        <el-table-column label="单位" width="70">
          <template #default="{ row }">
            <span style="color: #606266; font-size: 13px;">{{ row.unit || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="单价" width="110">
          <template #default="{ $index }">
            <el-input-number
              v-model="form.items[$index].unit_price"
              :min="0"
              :precision="2"
              :controls="false"
              style="width: 100%"
              @change="calcItemSubtotal($index)"
            />
          </template>
        </el-table-column>
        <el-table-column label="小计" width="100" align="right">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold; font-size: 13px;">{{ Number(row.subtotal || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="100">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].remark" placeholder="备注" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="70" align="center">
          <template #default="{ $index }">
            <el-button link type="danger" size="small" @click="removeItem($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button class="add-row-btn" type="primary" plain size="small" @click="addItem">+ 添加明细</el-button>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情弹窗 -->
    <el-dialog v-model="viewVisible" title="BOM详情" width="800px" top="5vh">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="产品编码">{{ viewData.product_code }}</el-descriptions-item>
        <el-descriptions-item label="产品名称">{{ viewData.product_name }}</el-descriptions-item>
        <el-descriptions-item label="版本">{{ viewData.version }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="viewData.is_active ? 'success' : 'info'">{{ viewData.is_active ? '启用' : '禁用' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总成本">
          <span style="color: #f56c6c; font-weight: bold;">{{ Number(viewData.total_cost || 0).toFixed(2) }} 元</span>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ viewData.created_at }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewData.remark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <div class="sub-title">BOM明细</div>
      <el-table :data="viewData.items || []" border size="small">
        <el-table-column prop="material_code" label="物料编码" width="120" />
        <el-table-column prop="material_name" label="物料名称" min-width="160" />
        <el-table-column prop="spec" label="规格" min-width="120" />
        <el-table-column prop="quantity" label="用量" width="90" align="right" />
        <el-table-column prop="unit" label="单位" width="70" />
        <el-table-column prop="unit_price" label="单价" width="100" align="right">
          <template #default="{ row }">
            {{ Number(row.unit_price || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="subtotal" label="小计" width="100" align="right">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold;">{{ Number(row.subtotal || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBomList, createBom, updateBom, deleteBom, copyBom } from '@/api/production'
import { getMaterialOptions } from '@/api/inventory'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10, search: '', is_active: null })

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  product_code: '', product_name: '', version: 'V1.0', is_active: true, remark: '', items: []
})

const rules = {
  product_code: [{ required: true, message: '请输入产品编码', trigger: 'blur' }],
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
}

// 物料选项
const materialOptions = ref([])
const materialLoading = ref(false)

const totalCost = computed(() => {
  return form.value.items
    .reduce((sum, item) => sum + (Number(item.quantity) || 0) * (Number(item.unit_price) || 0), 0)
    .toFixed(2)
})

const fetchData = async () => {
  const params = { ...query.value }
  if (!params.search) delete params.search
  if (params.is_active === null || params.is_active === '') delete params.is_active
  const res = await getBomList(params)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

onMounted(fetchData)

const resetQuery = () => {
  query.value = { page: 1, size: 10, search: '', is_active: null }
  fetchData()
}

const resetForm = () => {
  form.value = { product_code: '', product_name: '', version: 'V1.0', is_active: true, remark: '', items: [] }
  currentId.value = null
  isEdit.value = false
}

const loadMaterials = async (keyword = '') => {
  materialLoading.value = true
  try {
    const res = await getMaterialOptions({ search: keyword })
    materialOptions.value = res.data || []
  } finally {
    materialLoading.value = false
  }
}

const searchMaterials = async (keyword) => {
  await loadMaterials(keyword)
}

const onMaterialChange = (materialId, index) => {
  const item = form.value.items[index]
  if (!materialId) {
    item.material_name = ''
    item.material_code = ''
    item.spec = ''
    item.unit = ''
    return
  }
  const mat = materialOptions.value.find(m => m.id === materialId)
  if (mat) {
    item.material_name = mat.name
    item.material_code = mat.code
    item.spec = mat.spec || ''
    item.unit = mat.unit || '件'
  }
  calcItemSubtotal(index)
}

const calcItemSubtotal = (index) => {
  const item = form.value.items[index]
  item.subtotal = ((Number(item.quantity) || 0) * (Number(item.unit_price) || 0)).toFixed(2)
}

const handleAdd = async () => {
  resetForm()
  dialogTitle.value = '新增BOM'
  await loadMaterials('')
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  resetForm()
  dialogTitle.value = '编辑BOM'
  isEdit.value = true
  currentId.value = row.id
  await loadMaterials('')
  // 确保当前BOM用到的物料在选项列表中
  if (row.items) {
    row.items.forEach(item => {
      if (item.material && !materialOptions.value.find(m => m.id === item.material)) {
        materialOptions.value.push({
          id: item.material,
          code: item.material_code || '',
          name: item.material_name || '',
          spec: item.spec || '',
          unit: item.unit || '',
        })
      }
    })
  }
  form.value = {
    product_code: row.product_code,
    product_name: row.product_name,
    version: row.version,
    is_active: row.is_active,
    remark: row.remark || '',
    items: row.items ? row.items.map(i => ({
      ...i,
      quantity: Number(i.quantity),
      unit_price: Number(i.unit_price || 0),
      subtotal: Number(i.subtotal || 0).toFixed(2),
    })) : [],
  }
  dialogVisible.value = true
}

const addItem = () => {
  form.value.items.push({ material: null, material_name: '', material_code: '', spec: '', quantity: 1, unit: '件', unit_price: 0, subtotal: '0.00', remark: '' })
}

const removeItem = (index) => {
  form.value.items.splice(index, 1)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    // 清理空明细
    const items = form.value.items
      .filter(i => i.material_name || i.material)
      .map(i => ({
        material: i.material,
        material_name: i.material_name,
        spec: i.spec,
        quantity: i.quantity,
        unit: i.unit,
        unit_price: i.unit_price,
        remark: i.remark,
      }))
    if (items.length === 0) {
      ElMessage.warning('请至少添加一条BOM明细')
      return
    }
    submitLoading.value = true
    try {
      const payload = { ...form.value, items }
      if (isEdit.value) {
        await updateBom(currentId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createBom(payload)
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
  ElMessageBox.confirm(`确定删除BOM "${row.product_name}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteBom(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}

// 查看详情
const viewVisible = ref(false)
const viewData = ref({})

const handleView = (row) => {
  viewData.value = { ...row }
  viewVisible.value = true
}

// 复制BOM
const handleCopy = async (row) => {
  try {
    const res = await copyBom(row.id)
    ElMessage.success('复制成功')
    await fetchData()
    // 打开编辑弹窗让用户修改副本
    if (res.data) {
      await handleEdit(res.data)
    }
  } catch (e) {
    // 错误已在拦截器处理
  }
}
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar {
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.filter-bar {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.pagination { margin-top: 15px; justify-content: flex-end; }
.sub-title {
  font-weight: bold;
  margin: 15px 0 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.cost-summary {
  color: #f56c6c;
  font-size: 15px;
}
.add-row-btn { margin-top: 10px; }
</style>
