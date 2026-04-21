<template>
  <div class="page-container">
    <el-card>
      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :span="4">
          <div class="stat-card bg-total">
            <div class="label">总记录</div>
            <div class="value">{{ stats.total || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card bg-normal">
            <div class="label">正常</div>
            <div class="value">{{ stats.normal || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card bg-late">
            <div class="label">迟到</div>
            <div class="value">{{ stats.late || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card bg-early">
            <div class="label">早退</div>
            <div class="value">{{ stats.early || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card bg-absent">
            <div class="label">旷工/请假</div>
            <div class="value">{{ (stats.absent || 0) + (stats.leave || 0) }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card bg-hours">
            <div class="label">总工时</div>
            <div class="value">{{ stats.total_work_hours ? stats.total_work_hours.toFixed(1) : 0 }}h</div>
          </div>
        </el-col>
      </el-row>

      <!-- 搜索栏 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="员工">
          <el-select v-model="searchForm.employee" filterable clearable placeholder="请选择员工" style="width: 160px">
            <el-option v-for="e in employeeOptions" :key="e.id" :label="`${e.employee_no} - ${e.name}`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 100px">
            <el-option label="正常" value="normal" />
            <el-option label="迟到" value="late" />
            <el-option label="早退" value="early" />
            <el-option label="旷工" value="absent" />
            <el-option label="请假" value="leave" />
          </el-select>
        </el-form-item>
        <el-form-item label="考勤日期">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="~"
            start-placeholder="开始"
            end-placeholder="结束"
            style="width: 220px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar">
        <el-button v-permission="'hr:attendance:add'" type="primary" @click="handleAdd">新增考勤</el-button>
        <el-button v-permission="'hr:attendance:add'" type="success" plain @click="handleBulk">批量打卡</el-button>
        <el-button v-permission="'hr:attendance:edit'" type="warning" plain @click="handleDingTalkSync">钉钉同步</el-button>
        <el-button link type="info" @click="handleDingTalkConfig">钉钉配置</el-button>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="employee_no" label="工号" min-width="110" />
        <el-table-column prop="employee_name" label="姓名" min-width="100" />
        <el-table-column prop="department" label="部门" min-width="120" />
        <el-table-column prop="date" label="考勤日期" width="110" />
        <el-table-column prop="check_in" label="上班时间" width="110" align="center">
          <template #default="{ row }">
            <span v-if="row.check_in">{{ row.check_in }}</span>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="check_out" label="下班时间" width="110" align="center">
          <template #default="{ row }">
            <span v-if="row.check_out">{{ row.check_out }}</span>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="work_hours" label="工作时长" width="90" align="right">
          <template #default="{ row }">
            <span v-if="row.work_hours > 0">{{ row.work_hours }}h</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="overtime_hours" label="加班" width="80" align="right">
          <template #default="{ row }">
            <span v-if="row.overtime_hours > 0" class="text-warning">{{ row.overtime_hours }}h</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="info" @click="handleView(row)">查看</el-button>
            <el-button v-permission="'hr:attendance:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'hr:attendance:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="员工" prop="employee">
          <el-select v-model="form.employee" filterable placeholder="请选择员工" style="width: 100%">
            <el-option v-for="e in employeeOptions" :key="e.id" :label="`${e.employee_no} - ${e.name}`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考勤日期" prop="date">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上班时间">
              <el-time-picker v-model="form.check_in" value-format="HH:mm:ss" placeholder="上班时间" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="下班时间">
              <el-time-picker v-model="form.check_out" value-format="HH:mm:ss" placeholder="下班时间" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="考勤状态">
          <el-radio-group v-model="form.status">
            <el-radio label="normal">正常</el-radio>
            <el-radio label="late">迟到</el-radio>
            <el-radio label="early">早退</el-radio>
            <el-radio label="absent">旷工</el-radio>
            <el-radio label="leave">请假</el-radio>
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

    <!-- 批量打卡对话框 -->
    <el-dialog v-model="bulkDialogVisible" title="批量打卡" width="520px">
      <el-form :model="bulkForm" label-width="90px">
        <el-form-item label="考勤日期" prop="date">
          <el-date-picker v-model="bulkForm.date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="选择员工">
          <el-select v-model="bulkForm.employee_ids" multiple filterable placeholder="请选择员工" style="width: 100%">
            <el-option v-for="e in employeeOptions" :key="e.id" :label="`${e.employee_no} - ${e.name}`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上班时间">
              <el-time-picker v-model="bulkForm.check_in" value-format="HH:mm:ss" placeholder="上班时间" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="下班时间">
              <el-time-picker v-model="bulkForm.check_out" value-format="HH:mm:ss" placeholder="下班时间" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="考勤状态">
          <el-radio-group v-model="bulkForm.status">
            <el-radio label="normal">正常</el-radio>
            <el-radio label="late">迟到</el-radio>
            <el-radio label="early">早退</el-radio>
            <el-radio label="absent">旷工</el-radio>
            <el-radio label="leave">请假</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bulkDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="bulkLoading" @click="handleSubmitBulk">确定</el-button>
      </template>
    </el-dialog>

    <!-- 钉钉同步对话框 -->
    <el-dialog v-model="dingTalkSyncVisible" title="钉钉考勤同步" width="500px">
      <el-form :model="syncForm" label-width="100px">
        <el-form-item label="同步日期">
          <el-date-picker
            v-model="syncForm.dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="~"
            start-placeholder="开始"
            end-placeholder="结束"
            style="width: 100%"
          />
        </el-form-item>
        <el-alert
          title="说明"
          description="同步范围最多7天。系统会获取已绑定钉钉用户ID的员工的考勤打卡结果，并自动写入考勤记录表。"
          type="info"
          :closable="false"
          style="margin-bottom: 15px"
        />
      </el-form>
      <template #footer>
        <el-button @click="dingTalkSyncVisible = false">取消</el-button>
        <el-button type="primary" :loading="syncLoading" @click="handleSubmitSync">开始同步</el-button>
      </template>
    </el-dialog>

    <!-- 钉钉配置对话框 -->
    <el-dialog v-model="dingTalkConfigVisible" title="钉钉配置" width="500px">
      <el-form :model="configForm" label-width="100px">
        <el-form-item label="AppKey">
          <el-input v-model="configForm.app_key" placeholder="请输入钉钉 AppKey" />
        </el-form-item>
        <el-form-item label="AppSecret">
          <el-input v-model="configForm.app_secret" placeholder="请输入钉钉 AppSecret" show-password />
        </el-form-item>
        <el-form-item v-if="configInfo && configInfo.has_token">
          <el-tag type="success">Token 有效</el-tag>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dingTalkConfigVisible = false">取消</el-button>
        <el-button type="success" @click="handleTestConnection">测试连接</el-button>
        <el-button type="primary" @click="handleSaveConfig">保存配置</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="考勤详情" width="520px">
      <el-descriptions :column="1" border v-if="currentRow">
        <el-descriptions-item label="工号">{{ currentRow.employee_no }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ currentRow.employee_name }}</el-descriptions-item>
        <el-descriptions-item label="部门">{{ currentRow.department || '-' }}</el-descriptions-item>
        <el-descriptions-item label="考勤日期">{{ currentRow.date }}</el-descriptions-item>
        <el-descriptions-item label="应上班时间">{{ currentRow.base_check_in || '-' }}</el-descriptions-item>
        <el-descriptions-item label="实际上班时间">{{ currentRow.check_in || '-' }}</el-descriptions-item>
        <el-descriptions-item label="应下班时间">{{ currentRow.base_check_out || '-' }}</el-descriptions-item>
        <el-descriptions-item label="实际下班时间">{{ currentRow.check_out || '-' }}</el-descriptions-item>
        <el-descriptions-item label="工作时长">{{ currentRow.work_hours ? currentRow.work_hours + '小时' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="加班时长">{{ currentRow.overtime_hours ? currentRow.overtime_hours + '小时' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(currentRow.status)">{{ statusText(currentRow.status) }}</el-tag>
          <span v-if="currentRow.late_minutes > 0" class="text-warning" style="margin-left: 8px;">(迟到 {{ currentRow.late_minutes }} 分钟)</span>
          <span v-if="currentRow.early_minutes > 0" class="text-warning" style="margin-left: 8px;">(早退 {{ currentRow.early_minutes }} 分钟)</span>
        </el-descriptions-item>
        <el-descriptions-item label="备注">{{ currentRow.remark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <!-- 钉钉打卡原始记录 -->
      <template v-if="currentRow && currentRow.dingtalk_detail && currentRow.dingtalk_detail.records && currentRow.dingtalk_detail.records.length > 0">
        <div style="margin-top: 20px;">
          <div style="font-weight: bold; margin-bottom: 10px;">钉钉打卡原始记录</div>
          <el-table :data="currentRow.dingtalk_detail.records" border size="small">
            <el-table-column label="类型" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="row.checkType === 'OnDuty' ? 'primary' : 'success'">
                  {{ row.checkType === 'OnDuty' ? '上班' : '下班' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="打卡结果" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="dingTalkTimeResultType(row.timeResult)">
                  {{ dingTalkTimeResultText(row.timeResult) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="排班时间" width="110">
              <template #default="{ row }">
                {{ formatDingTalkTime(row.baseCheckTime) }}
              </template>
            </el-table-column>
            <el-table-column label="实际打卡" width="110">
              <template #default="{ row }">
                {{ formatDingTalkTime(row.userCheckTime) }}
              </template>
            </el-table-column>
            <el-table-column label="位置" width="100">
              <template #default="{ row }">
                {{ dingTalkLocationText(row.locationResult) }}
              </template>
            </el-table-column>
            <el-table-column label="来源" min-width="100">
              <template #default="{ row }">
                {{ dingTalkSourceText(row.sourceType) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAttendanceList, createAttendance, updateAttendance, deleteAttendance,
  getAttendanceStats, bulkCreateAttendance, getEmployeeOptions,
  getDingTalkConfig, saveDingTalkConfig, testDingTalkConnection, syncDingTalkAttendance
} from '@/api/hr'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = ref({ page: 1, size: 10 })
const employeeOptions = ref([])
const stats = ref({})

const searchForm = reactive({
  employee: '',
  status: '',
  dateRange: [],
})

const dialogVisible = ref(false)
const bulkDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const bulkLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)
const currentRow = ref(null)

const form = ref({
  employee: null, date: '', check_in: '', check_out: '', status: 'normal', remark: ''
})

const bulkForm = reactive({
  date: '',
  employee_ids: [],
  check_in: '09:00:00',
  check_out: '18:00:00',
  status: 'normal',
})

const dingTalkSyncVisible = ref(false)
const syncLoading = ref(false)
const syncForm = reactive({
  dateRange: [],
})

const dingTalkConfigVisible = ref(false)
const configForm = reactive({
  app_key: '',
  app_secret: '',
})
const configInfo = ref(null)

const rules = {
  employee: [{ required: true, message: '请选择员工', trigger: 'change' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
}

const statusText = (s) => ({ normal: '正常', late: '迟到', early: '早退', absent: '旷工', leave: '请假' }[s] || s)
const statusType = (s) => ({ normal: 'success', late: 'warning', early: 'warning', absent: 'danger', leave: 'info' }[s] || '')

// 钉钉时间结果映射
const dingTalkTimeResultText = (r) => ({ Normal: '正常', Late: '迟到', Early: '早退', SeriousLate: '严重迟到', Absenteeism: '旷工', NotSigned: '未打卡' }[r] || r)
const dingTalkTimeResultType = (r) => ({ Normal: 'success', Late: 'warning', Early: 'warning', SeriousLate: 'danger', Absenteeism: 'danger', NotSigned: 'info' }[r] || '')
// 钉钉位置结果映射
const dingTalkLocationText = (r) => ({ Normal: '正常', Outside: '外勤', NotSigned: '未打卡' }[r] || r || '-')
// 钉钉打卡来源映射
const dingTalkSourceText = (s) => ({ USER: '手动打卡', SYSTEM: '系统打卡', AUTO: '自动打卡', BEACON: '蓝牙', WIFI: 'WiFi' }[s] || s || '-')
// 格式化钉钉毫秒时间戳
const formatDingTalkTime = (ts) => {
  if (!ts) return '-'
  const date = new Date(ts)
  return date.toLocaleTimeString('zh-CN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const buildQuery = () => {
  const params = { ...query.value }
  if (searchForm.employee) params.employee = searchForm.employee
  if (searchForm.status) params.status = searchForm.status
  if (searchForm.dateRange && searchForm.dateRange.length === 2) {
    params.date_from = searchForm.dateRange[0]
    params.date_to = searchForm.dateRange[1]
  }
  return params
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getAttendanceList(buildQuery())
    tableData.value = res.data.list
    total.value = res.data.pagination.total
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  const params = {}
  if (searchForm.dateRange && searchForm.dateRange.length === 2) {
    params.date_from = searchForm.dateRange[0]
    params.date_to = searchForm.dateRange[1]
  }
  const res = await getAttendanceStats(params)
  stats.value = res.data
}

const fetchEmployees = async () => {
  const res = await getEmployeeOptions()
  employeeOptions.value = res.data
}

onMounted(() => {
  fetchData()
  fetchStats()
  fetchEmployees()
})

const handleSearch = () => {
  query.value.page = 1
  fetchData()
  fetchStats()
}

const handleReset = () => {
  searchForm.employee = ''
  searchForm.status = ''
  searchForm.dateRange = []
  query.value.page = 1
  fetchData()
  fetchStats()
}

const resetForm = () => {
  form.value = { employee: null, date: '', check_in: '', check_out: '', status: 'normal', remark: '' }
  currentId.value = null
  isEdit.value = false
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增考勤'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  dialogTitle.value = '编辑考勤'
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    employee: row.employee,
    date: row.date,
    check_in: row.check_in || '',
    check_out: row.check_out || '',
    status: row.status,
    remark: row.remark || '',
  }
  dialogVisible.value = true
}

const handleView = (row) => {
  currentRow.value = row
  viewDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (isEdit.value) {
        await updateAttendance(currentId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await createAttendance(form.value)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      await fetchData()
      await fetchStats()
    } finally {
      submitLoading.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除该考勤记录吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteAttendance(row.id)
    ElMessage.success('删除成功')
    await fetchData()
    await fetchStats()
  })
}

// 批量打卡
const handleBulk = () => {
  bulkForm.date = ''
  bulkForm.employee_ids = []
  bulkForm.check_in = '09:00:00'
  bulkForm.check_out = '18:00:00'
  bulkForm.status = 'normal'
  bulkDialogVisible.value = true
}

const handleSubmitBulk = async () => {
  if (!bulkForm.date || bulkForm.employee_ids.length === 0) {
    ElMessage.warning('请选择日期和员工')
    return
  }
  bulkLoading.value = true
  try {
    await bulkCreateAttendance({
      date: bulkForm.date,
      employee_ids: bulkForm.employee_ids,
      check_in: bulkForm.check_in,
      check_out: bulkForm.check_out,
      status: bulkForm.status,
    })
    ElMessage.success('批量打卡成功')
    bulkDialogVisible.value = false
    await fetchData()
    await fetchStats()
  } finally {
    bulkLoading.value = false
  }
}

// 钉钉同步
const handleDingTalkSync = () => {
  syncForm.dateRange = []
  dingTalkSyncVisible.value = true
}

const handleSubmitSync = async () => {
  if (!syncForm.dateRange || syncForm.dateRange.length !== 2) {
    ElMessage.warning('请选择同步日期范围')
    return
  }
  syncLoading.value = true
  try {
    const res = await syncDingTalkAttendance({
      date_from: syncForm.dateRange[0],
      date_to: syncForm.dateRange[1],
    })
    ElMessage.success(res.message || '同步完成')
    dingTalkSyncVisible.value = false
    await fetchData()
    await fetchStats()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '同步失败')
  } finally {
    syncLoading.value = false
  }
}

// 钉钉配置
const handleDingTalkConfig = async () => {
  const res = await getDingTalkConfig()
  configInfo.value = res.data
  if (res.data) {
    configForm.app_key = res.data.app_key || ''
    configForm.app_secret = ''
  } else {
    configForm.app_key = ''
    configForm.app_secret = ''
  }
  dingTalkConfigVisible.value = true
}

const handleSaveConfig = async () => {
  if (!configForm.app_key || !configForm.app_secret) {
    ElMessage.warning('请填写 AppKey 和 AppSecret')
    return
  }
  await saveDingTalkConfig(configForm)
  ElMessage.success('配置保存成功')
  dingTalkConfigVisible.value = false
}

const handleTestConnection = async () => {
  try {
    const res = await testDingTalkConnection()
    ElMessage.success(res.message || '连接成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '连接失败')
  }
}
</script>

<style scoped>
.page-container { padding: 20px; }
.stats-row { margin-bottom: 20px; }
.stat-card {
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  color: #fff;
}
.stat-card .label { font-size: 13px; margin-bottom: 8px; opacity: 0.9; }
.stat-card .value { font-size: 22px; font-weight: bold; }
.bg-total { background: linear-gradient(135deg, #409eff, #66b1ff); }
.bg-normal { background: linear-gradient(135deg, #67c23a, #85ce61); }
.bg-late { background: linear-gradient(135deg, #e6a23c, #ebb563); }
.bg-early { background: linear-gradient(135deg, #f56c6c, #f78989); }
.bg-absent { background: linear-gradient(135deg, #909399, #a6a9ad); }
.bg-hours { background: linear-gradient(135deg, #c45656, #d47878); }
.search-form { margin-bottom: 15px; }
.toolbar { margin-bottom: 15px; }
.pagination { margin-top: 15px; justify-content: flex-end; }
.text-warning { color: #e6a23c; font-weight: bold; }
.text-muted { color: #909399; }
</style>
