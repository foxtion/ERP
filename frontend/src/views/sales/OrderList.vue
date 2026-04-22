<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <el-button v-permission="'sales:order:add'" type="primary" @click="handleAdd">新增订单</el-button>
        <div class="filter-bar">
          <el-input v-model="query.search" placeholder="订单编号/客户名称" clearable style="width: 200px" @keyup.enter="fetchData" />
          <el-select v-model="query.status" placeholder="订单状态" clearable style="width: 140px">
            <el-option label="草稿" value="draft" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="部分出库" value="partial" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </div>
      </div>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="order_no" label="订单编号" min-width="150" />
        <el-table-column prop="customer_name" label="客户" min-width="150" />
        <el-table-column prop="order_date" label="订单日期" min-width="120" />
        <el-table-column prop="delivery_date" label="交货日期" min-width="120" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额" width="120" align="right" />
        <el-table-column prop="salesman_name" label="销售员" min-width="120" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'sales:order:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'sales:order:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
            <el-button v-if="['confirmed','partial'].includes(row.status)" v-permission="'sales:picking:add'" link type="success" @click="handleCreatePicking(row)">生成拣货单</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="900px" top="5vh">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="订单编号" prop="order_no">
              <el-input v-model="form.order_no" placeholder="请输入订单编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户" prop="customer">
              <el-select v-model="form.customer" placeholder="请选择客户" filterable style="width: 100%">
                <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="订单日期" prop="order_date">
              <el-date-picker v-model="form.order_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="交货日期">
              <el-date-picker v-model="form.delivery_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>

      <div class="sub-title">销售明细</div>
      <el-table :data="form.items" border size="small">
        <el-table-column label="物料编码" min-width="120">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].material_code" placeholder="编码" disabled />
          </template>
        </el-table-column>
        <el-table-column label="物料名称" min-width="180">
          <template #default="{ $index }">
            <el-select
              v-model="form.items[$index].material_code"
              filterable
              remote
              reserve-keyword
              placeholder="搜索物料名称或编码"
              :remote-method="(q) => searchMaterial(q, $index)"
              :loading="materialLoading[$index]"
              style="width: 100%"
              @change="(val) => onMaterialSelect($index, val)"
            >
              <el-option
                v-for="m in materialOptions[$index] || []"
                :key="m.code"
                :label="`${m.code} - ${m.name}`"
                :value="m.code"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="规格型号" min-width="120">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].spec" placeholder="规格" />
          </template>
        </el-table-column>
        <el-table-column label="数量" width="100">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].quantity" :min="0" :precision="0" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="单位" width="70">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].unit" placeholder="单位" />
          </template>
        </el-table-column>
        <el-table-column label="单价" width="110">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].price" :min="0" :precision="4" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="100">
          <template #default="{ $index }">
            <el-input v-model="form.items[$index].remark" placeholder="备注" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="70" align="center">
          <template #default="{ $index }">
            <el-button link type="danger" @click="removeItem($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button class="add-row-btn" type="primary" plain @click="addItem">+ 添加明细</el-button>

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
import { getSalesOrderList, createSalesOrder, updateSalesOrder, deleteSalesOrder, createPickingFromOrder } from '@/api/sales'
import { getCustomerList } from '@/api/sales'
import { getMaterialOptions } from '@/api/inventory'

const tableData = ref([])
const total = ref(0)
const query = ref({ page: 1, size: 10, search: '', status: '' })
const customerList = ref([])
const materialOptions = ref({})
const materialLoading = ref({})

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  order_no: '', customer: null, order_date: '', delivery_date: '', remark: '', items: []
})

const rules = {
  order_no: [{ required: true, message: '请输入订单编号', trigger: 'blur' }],
  customer: [{ required: true, message: '请选择客户', trigger: 'change' }],
  order_date: [{ required: true, message: '请选择订单日期', trigger: 'change' }],
}

const statusText = (s) => ({ draft: '草稿', confirmed: '已确认', partial: '部分出库', completed: '已完成', cancelled: '已取消' }[s] || s)
const statusType = (s) => ({ draft: 'info', confirmed: 'primary', partial: 'warning', completed: 'success', cancelled: 'danger' }[s] || '')

const fetchData = async () => {
  const res = await getSalesOrderList(query.value)
  tableData.value = res.data.list
  total.value = res.data.pagination.total
}

const fetchCustomers = async () => {
  const res = await getCustomerList({ size: 999 })
  customerList.value = res.data.list
}

onMounted(() => {
  fetchData()
  fetchCustomers()
})

const resetForm = () => {
  form.value = { order_no: '', customer: null, order_date: '', delivery_date: '', remark: '', items: [] }
  currentId.value = null
  isEdit.value = false
}

const generateClientOrderNo = () => {
  const now = new Date()
  const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '')
  const rand = Math.floor(1000 + Math.random() * 9000)
  return `SO${dateStr}${rand}`
}

const handleAdd = () => {
  resetForm()
  form.value.order_no = generateClientOrderNo()
  dialogTitle.value = '新增销售订单'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑销售订单'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    order_no: row.order_no,
    customer: row.customer,
    order_date: row.order_date,
    delivery_date: row.delivery_date || '',
    remark: row.remark || '',
    items: row.items ? row.items.map((i, idx) => {
      const item = { ...i }
      // 编辑时预加载当前物料到 options，确保 select 能正确显示
      if (item.material_code) {
        materialOptions.value[idx] = [{
          id: idx,
          code: item.material_code,
          name: item.material_name,
          spec: item.spec,
          unit: item.unit,
        }]
      }
      return item
    }) : [],
  }
  dialogVisible.value = true
}

const searchMaterial = async (query, index) => {
  if (!query || query.length < 1) {
    materialOptions.value[index] = []
    return
  }
  materialLoading.value[index] = true
  try {
    const res = await getMaterialOptions({ search: query })
    materialOptions.value[index] = res.data || []
  } finally {
    materialLoading.value[index] = false
  }
}

const onMaterialSelect = (index, code) => {
  const options = materialOptions.value[index] || []
  const mat = options.find(m => m.code === code)
  if (mat) {
    form.value.items[index].material_code = mat.code
    form.value.items[index].material_name = mat.name
    form.value.items[index].spec = mat.spec
    form.value.items[index].unit = mat.unit
  }
}

const addItem = () => {
  form.value.items.push({ material_code: '', material_name: '', spec: '', quantity: 1, unit: '件', price: 0, remark: '' })
}

const removeItem = (index) => {
  form.value.items.splice(index, 1)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    if (form.value.items.length === 0) {
      ElMessage.warning('请至少添加一条明细')
      return
    }
    submitLoading.value = true
    try {
      const payload = { ...form.value }
      if (isEdit.value) {
        await updateSalesOrder(currentId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createSalesOrder(payload)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      await fetchData()
    } finally {
      submitLoading.value = false
    }
  })
}

const resetQuery = () => {
  query.value = { page: 1, size: 10, search: '', status: '' }
  fetchData()
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除订单 "${row.order_no}" 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteSalesOrder(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  })
}

const handleCreatePicking = async (row) => {
  try {
    await ElMessageBox.confirm(`确定为订单 "${row.order_no}" 生成拣货单吗？`, '提示', { type: 'info' })
    const res = await createPickingFromOrder(row.id)
    ElMessage.success(`拣货单 ${res.data.picking_no} 生成成功`)
  } catch (e) {
    // 取消或报错
  }
}
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
.filter-bar { display: flex; gap: 10px; align-items: center; }
.pagination { margin-top: 15px; justify-content: flex-end; }
.sub-title { font-weight: bold; margin: 15px 0 8px; }
.add-row-btn { margin-top: 10px; }
</style>
