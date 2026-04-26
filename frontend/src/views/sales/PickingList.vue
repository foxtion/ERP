<template>
  <div class="page-container">
    <el-card>
      <div class="toolbar">
        <div class="filter-bar">
          <el-input v-model="query.search" placeholder="拣货单号/订单编号" clearable style="width: 200px" @keyup.enter="fetchData" />
          <el-input v-model="query.user_name" placeholder="员工姓名" clearable style="width: 140px" @keyup.enter="fetchData" />
          <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px">
            <el-option label="待指派" value="pending" />
            <el-option label="已指派" value="assigned" />
            <el-option label="已接单" value="accepted" />
            <el-option label="拿货中" value="picking" />
            <el-option label="齐发待出库" value="complete" />
            <el-option label="欠发待出库" value="shortage" />
            <el-option label="已完成" value="done" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-date-picker
            v-model="query.created_at_range"
            type="daterange"
            range-separator="至"
            start-placeholder="创建开始"
            end-placeholder="创建结束"
            value-format="YYYY-MM-DD"
            clearable
            style="width: 260px"
            @change="fetchData"
          />
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </div>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="picking_no" label="拣货单号" min-width="150" />
        <el-table-column prop="order_no" label="关联订单" min-width="150" />
        <el-table-column prop="customer_name" label="客户" min-width="120" />
        <el-table-column prop="warehouse" label="仓库" width="120" />
        <el-table-column prop="status" label="状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assigned_to_name" label="指派员工" width="120" />
        <el-table-column prop="picker_name" label="实际拿货人" width="120" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button v-if="row.status === 'pending'" v-permission="'sales:picking:assign'" link type="success" @click="handleAssign(row)">指派</el-button>
            <el-button v-if="row.status === 'assigned'" v-permission="'sales:picking:job'" link type="warning" @click="handleAccept(row)">接单</el-button>
            <el-button v-if="['picking','complete','shortage'].includes(row.status)" v-permission="'sales:picking:job'" link type="primary" @click="handleGoJob(row)">去作业</el-button>
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

    <!-- 查看详情 -->
    <el-dialog v-model="viewVisible" title="拣货单详情" width="700px">
      <el-descriptions :column="2" border v-if="currentRow">
        <el-descriptions-item label="拣货单号">{{ currentRow.picking_no }}</el-descriptions-item>
        <el-descriptions-item label="关联订单">{{ currentRow.order_no }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ currentRow.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="仓库">{{ currentRow.warehouse }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(currentRow.status)">{{ statusText(currentRow.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="指派员工">{{ currentRow.assigned_to_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="实际拿货人">{{ currentRow.picker_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ currentRow.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div class="sub-title">拣货明细</div>
      <el-table :data="currentRow?.items" border size="small">
        <el-table-column prop="location_code" label="库位号" width="100" />
        <el-table-column prop="material_code" label="商品代码" width="120" />
        <el-table-column prop="material_name" label="商品名称" min-width="150" />
        <el-table-column prop="spec" label="规格" width="100" />
        <el-table-column label="需拿数量" width="90" align="right">
          <template #default="{ row }">{{ fmtInt(row.quantity) }}</template>
        </el-table-column>
        <el-table-column label="已拿数量" width="90" align="right">
          <template #default="{ row }">{{ fmtInt(row.picked_qty) }}</template>
        </el-table-column>
        <el-table-column label="缺货数量" width="90" align="right">
          <template #default="{ row }">{{ fmtInt(row.shortage_qty) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'picked' ? 'success' : row.status === 'shortage' ? 'danger' : 'info'">
              {{ {pending:'待拿', picked:'已拿', shortage:'缺货'}[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 指派弹窗 -->
    <el-dialog v-model="assignVisible" title="指派员工" width="400px">
      <el-form label-width="80px">
        <el-form-item label="选择员工">
          <el-select v-model="assigneeId" filterable placeholder="请选择员工" style="width: 100%">
            <el-option v-for="u in userList" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="primary" :loading="assignLoading" @click="confirmAssign">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getPickingList, getPickingDetail, assignPicking, acceptPicking } from '@/api/sales'
import { getUserList } from '@/api/system'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.is_superuser)
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = ref({ page: 1, size: 10, search: '', status: '', user_name: '', created_at_range: null })

const viewVisible = ref(false)
const currentRow = ref(null)

const assignVisible = ref(false)
const assignLoading = ref(false)
const assigneeId = ref(null)
const currentAssignId = ref(null)
const userList = ref([])

const statusText = (s) => ({
  pending: '待指派', assigned: '已指派', accepted: '已接单',
  picking: '拿货中', complete: '齐发待出库', shortage: '欠发待出库',
  done: '已完成', cancelled: '已取消'
}[s] || s)

const statusType = (s) => ({
  pending: 'info', assigned: 'primary', accepted: 'warning',
  picking: 'warning', complete: 'success', shortage: 'danger',
  done: 'success', cancelled: 'info'
}[s] || '')

const fetchData = async () => {
  loading.value = true
  try {
    const params = { ...query.value }
    if (params.created_at_range && params.created_at_range.length === 2) {
      params.created_at_start = params.created_at_range[0]
      params.created_at_end = params.created_at_range[1]
    }
    delete params.created_at_range
    const res = await getPickingList(params)
    tableData.value = res.data.list
    total.value = res.data.pagination.total
  } finally {
    loading.value = false
  }
}

const fetchUsers = async () => {
  try {
    const res = await getUserList({ size: 999 })
    userList.value = res.data.list
  } catch (e) {
    // 非管理员可能没有 system:user:view 权限，静默忽略
    userList.value = []
  }
}

onMounted(() => {
  fetchData()
  if (isAdmin.value) {
    fetchUsers()
  }
})

const resetQuery = () => {
  query.value = { page: 1, size: 10, search: '', status: '', user_name: '', created_at_range: null }
  fetchData()
}

const handleView = async (row) => {
  const res = await getPickingDetail(row.id)
  currentRow.value = res.data
  viewVisible.value = true
}

const handleAssign = (row) => {
  currentAssignId.value = row.id
  assigneeId.value = null
  assignVisible.value = true
}

const confirmAssign = async () => {
  if (!assigneeId.value) {
    ElMessage.warning('请选择员工')
    return
  }
  assignLoading.value = true
  try {
    await assignPicking(currentAssignId.value, assigneeId.value)
    ElMessage.success('指派成功')
    assignVisible.value = false
    await fetchData()
  } finally {
    assignLoading.value = false
  }
}

const handleAccept = async (row) => {
  try {
    await acceptPicking(row.id)
    ElMessage.success('接单成功')
    await fetchData()
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || e?.message || '接单失败')
  }
}

// 格式化数量为纯整数（去掉小数）
const fmtInt = (val) => {
  if (val === null || val === undefined || val === '') return '0'
  return String(Math.floor(Number(val)))
}

const handleGoJob = (row) => {
  router.push(`/sales/picking-job/${row.id}`)
}
</script>

<style scoped>
.page-container { padding: 20px; }
.toolbar { margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
.filter-bar { display: flex; gap: 10px; align-items: center; }
.pagination { margin-top: 15px; justify-content: flex-end; }
.sub-title { font-weight: bold; margin: 15px 0 8px; }
</style>
