<template>
  <div class="page-container">
    <el-card>
      <!-- 搜索筛选 -->
      <el-form :model="query" inline class="search-form">
        <el-form-item label="关键字">
          <el-input
            v-model="query.search"
            placeholder="菜单标题/名称/路径"
            clearable
            style="width: 220px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="菜单类型">
          <el-select v-model="query.menu_type" placeholder="全部" clearable style="width: 120px">
            <el-option label="目录" value="DIR" />
            <el-option label="菜单" value="MENU" />
            <el-option label="按钮" value="BUTTON" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar">
        <el-button v-permission="'system:menu:add'" type="primary" @click="handleAdd">新增菜单</el-button>
        <el-button @click="expandAll">展开全部</el-button>
        <el-button @click="collapseAll">收起全部</el-button>
      </div>

      <el-table
        ref="tableRef"
        :data="filteredTableData"
        row-key="id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        border
        stripe
        default-expand-all
      >
        <el-table-column prop="title" label="菜单标题" min-width="160">
          <template #default="{ row }">
            <el-icon v-if="row.icon" style="vertical-align: middle; margin-right: 4px;">
              <IconRender :icon="row.icon" />
            </el-icon>
            <span>{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="menu_type" label="类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.menu_type === 'DIR'">目录</el-tag>
            <el-tag v-else-if="row.menu_type === 'MENU'" type="success">菜单</el-tag>
            <el-tag v-else type="warning">按钮</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路由路径" min-width="140" show-overflow-tooltip />
        <el-table-column prop="component" label="组件路径" min-width="160" show-overflow-tooltip />
        <el-table-column prop="permission" label="权限标识" min-width="140" show-overflow-tooltip />
        <el-table-column prop="sort_order" label="排序" width="70" align="center" />
        <el-table-column label="状态" width="180" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_active" size="small" type="success">启用</el-tag>
            <el-tag v-else size="small" type="info">停用</el-tag>
            <el-tag v-if="row.is_hidden" size="small" type="danger" style="margin-left: 4px;">隐藏</el-tag>
            <el-tag v-if="row.keep_alive && row.menu_type === 'MENU'" size="small" type="primary" style="margin-left: 4px;">缓存</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button v-permission="'system:menu:add'" link type="primary" @click="handleAddChild(row)">新增</el-button>
            <el-button v-permission="'system:menu:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'system:menu:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑菜单弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="650px" @closed="onDialogClosed">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="菜单类型" prop="menu_type">
              <el-select v-model="form.menu_type" placeholder="请选择类型" style="width: 100%" @change="onMenuTypeChange">
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

        <el-form-item label="上级菜单">
          <el-tree-select
            v-model="form.parent"
            :data="excludeSelfTree"
            :props="{ label: 'title', value: 'id', children: 'children' }"
            check-strictly
            clearable
            placeholder="请选择上级菜单（留空为顶级）"
            style="width: 100%"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="菜单标题" prop="title">
              <el-input v-model="form.title" placeholder="请输入菜单标题" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单名称" prop="name">
              <el-input v-model="form.name" placeholder="路由name，需唯一" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item v-if="form.menu_type !== 'BUTTON'" label="路由路径" prop="path">
          <el-input v-model="form.path" placeholder="请输入路由路径，如 /system/user" />
        </el-form-item>

        <el-form-item v-if="form.menu_type === 'MENU'" label="组件路径" prop="component">
          <el-input v-model="form.component" placeholder="如 system/UserList.vue，或 views/system/UserList.vue" />
        </el-form-item>

        <el-form-item v-if="form.menu_type !== 'DIR'" label="权限标识" prop="permission">
          <el-input v-model="form.permission" placeholder="如 system:user:view" />
        </el-form-item>

        <el-form-item v-if="form.menu_type !== 'BUTTON'" label="图标">
          <el-input v-model="form.icon" placeholder="点击选择图标" readonly style="width: calc(100% - 110px)" />
          <el-button style="margin-left: 10px" @click="iconDialogVisible = true">选择图标</el-button>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item v-if="form.menu_type !== 'BUTTON'" label="是否隐藏">
              <el-radio-group v-model="form.is_hidden">
                <el-radio :label="false">显示</el-radio>
                <el-radio :label="true">隐藏</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item v-if="form.menu_type === 'MENU'" label="是否缓存">
              <el-radio-group v-model="form.keep_alive">
                <el-radio :label="true">缓存</el-radio>
                <el-radio :label="false">不缓存</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 图标选择弹窗 -->
    <el-dialog v-model="iconDialogVisible" title="选择图标" width="700px">
      <div class="icon-grid">
        <div
          v-for="icon in iconList"
          :key="icon"
          class="icon-item"
          :class="{ active: form.icon === icon }"
          @click="selectIcon(icon)"
        >
          <el-icon :size="20"><IconRender :icon="icon" /></el-icon>
          <span class="icon-name">{{ icon }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMenuList, getMenuTree, createMenu, updateMenu, deleteMenu } from '@/api/system'
import IconRender from '@/components/IconRender.vue'

const tableRef = ref(null)
const tableData = ref([])
const treeData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentId = ref(null)
const iconDialogVisible = ref(false)

const query = ref({
  search: '',
  menu_type: '',
})

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
  keep_alive: true,
  remark: '',
})

const rules = computed(() => {
  const base = {
    menu_type: [{ required: true, message: '请选择菜单类型', trigger: 'change' }],
    title: [{ required: true, message: '请输入菜单标题', trigger: 'blur' }],
    name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
  }
  if (form.value.menu_type === 'MENU') {
    base.path = [{ required: true, message: '请输入路由路径', trigger: 'blur' }]
    base.component = [{ required: true, message: '请输入组件路径', trigger: 'blur' }]
  } else if (form.value.menu_type === 'DIR') {
    base.path = [{ required: true, message: '请输入路由路径', trigger: 'blur' }]
  }
  if (form.value.menu_type !== 'DIR') {
    base.permission = [{ required: true, message: '请输入权限标识', trigger: 'blur' }]
  }
  return base
})

// 图标列表（与 IconRender.vue 中注册的图标保持一致）
const iconList = [
  'AddLocation', 'Aim', 'AlarmClock', 'Apple', 'ArrowDown', 'ArrowDownBold', 'ArrowLeft', 'ArrowLeftBold',
  'ArrowRight', 'ArrowRightBold', 'ArrowUp', 'ArrowUpBold', 'Avatar', 'Back', 'Baseball', 'Basketball',
  'Bell', 'BellFilled', 'Bicycle', 'Bottom', 'BottomLeft', 'BottomRight', 'Bowl', 'Box',
  'Briefcase', 'Brush', 'BrushFilled', 'Burger', 'Calendar', 'Camera', 'CameraFilled', 'CaretBottom',
  'CaretLeft', 'CaretRight', 'CaretTop', 'Cellphone', 'ChatDotRound', 'ChatDotSquare', 'ChatLineRound', 'ChatLineSquare',
  'ChatRound', 'ChatSquare', 'Check', 'Checked', 'Cherry', 'Chicken', 'ChromeFilled', 'CircleCheck',
  'CircleCheckFilled', 'CircleClose', 'CircleCloseFilled', 'CirclePlus', 'CirclePlusFilled', 'Clock', 'Close', 'CloseBold',
  'Cloudy', 'Coffee', 'CoffeeCup', 'Coin', 'ColdDrink', 'Collection', 'CollectionTag', 'Comment',
  'Compass', 'Connection', 'Coordinate', 'CopyDocument', 'Cpu', 'CreditCard', 'Crop', 'DArrowLeft',
  'DArrowRight', 'DCaret', 'DataAnalysis', 'DataBoard', 'DataLine', 'Delete', 'DeleteFilled', 'DeleteLocation',
  'Dessert', 'Discount', 'Dish', 'DishDot', 'Document', 'DocumentAdd', 'DocumentChecked', 'DocumentCopy',
  'DocumentDelete', 'DocumentRemove', 'Download', 'Drizzling', 'Edit', 'EditPen', 'Eleme', 'ElemeFilled',
  'ElementPlus', 'Expand', 'Failed', 'Female', 'Files', 'Film', 'Filter', 'Finished',
  'FirstAidKit', 'Flag', 'Fold', 'Folder', 'FolderAdd', 'FolderChecked', 'FolderDelete', 'FolderOpened',
  'FolderRemove', 'Food', 'Football', 'ForkSpoon', 'Fries', 'FullScreen', 'Goblet', 'GobletFull',
  'GobletSquare', 'GobletSquareFull', 'GoldMedal', 'Goods', 'GoodsFilled', 'Grape', 'Grid', 'Guide',
  'Handbag', 'Headset', 'Help', 'HelpFilled', 'Hide', 'Histogram', 'HomeFilled', 'HotWater',
  'House', 'IceCream', 'IceCreamRound', 'IceCreamSquare', 'IceDrink', 'IceTea', 'InfoFilled', 'Iphone',
  'Key', 'KnifeFork', 'Lightning', 'Link', 'List', 'Loading', 'Location', 'LocationFilled',
  'LocationInformation', 'Lock', 'Lollipop', 'MagicStick', 'Magnet', 'Male', 'Management', 'MapLocation',
  'Medal', 'Memo', 'Menu', 'Message', 'MessageBox', 'Mic', 'Microphone', 'MilkTea',
  'Minus', 'Money', 'Monitor', 'Moon', 'MoonNight', 'More', 'MoreFilled', 'MostlyCloudy',
  'Mouse', 'Mug', 'Mute', 'MuteNotification', 'NoSmoking', 'Notebook', 'Notification', 'Odometer',
  'OfficeBuilding', 'Open', 'Operation', 'Opportunity', 'Orange', 'Paperclip', 'PartlyCloudy', 'Pear',
  'Phone', 'PhoneFilled', 'Picture', 'PictureFilled', 'PictureRounded', 'PieChart', 'Place', 'Platform',
  'Plus', 'Pointer', 'Position', 'Postcard', 'Pouring', 'Present', 'PriceTag', 'Printer',
  'Promotion', 'QuartzWatch', 'QuestionFilled', 'Rank', 'Reading', 'ReadingLamp', 'Refresh', 'RefreshLeft',
  'RefreshRight', 'Refrigerator', 'Remove', 'RemoveFilled', 'Right', 'ScaleToOriginal', 'School', 'Scissor',
  'Search', 'Select', 'Sell', 'SemiSelect', 'Service', 'SetUp', 'Setting', 'Share',
  'Ship', 'Shop', 'ShoppingBag', 'ShoppingCart', 'ShoppingCartFull', 'ShoppingTrolley', 'Smoking', 'Soccer',
  'SoldOut', 'Sort', 'SortDown', 'SortUp', 'Stamp', 'Star', 'StarFilled', 'Stopwatch',
  'SuccessFilled', 'Sugar', 'Suitcase', 'SuitcaseLine', 'Sunny', 'Sunrise', 'Sunset', 'Switch',
  'SwitchButton', 'SwitchFilled', 'TakeawayBox', 'Ticket', 'Tickets', 'Timer', 'ToiletPaper', 'Tools',
  'Top', 'TopLeft', 'TopRight', 'TrendCharts', 'Trophy', 'TrophyBase', 'TurnOff', 'Umbrella',
  'Unlock', 'Upload', 'UploadFilled', 'User', 'UserFilled', 'Van', 'VideoCamera', 'VideoCameraFilled',
  'VideoPause', 'VideoPlay', 'View', 'Wallet', 'WalletFilled', 'WarnTriangleFilled', 'Warning', 'WarningFilled',
  'Watch', 'Watermelon', 'WindPower', 'ZoomIn', 'ZoomOut'
]

// 过滤后的表格数据（前端搜索）
const filteredTableData = computed(() => {
  const keyword = query.value.search?.trim().toLowerCase()
  const type = query.value.menu_type
  if (!keyword && !type) return tableData.value

  function filterTree(nodes) {
    return nodes
      .map((node) => {
        const children = node.children ? filterTree(node.children) : []
        const matchKeyword =
          !keyword ||
          node.title?.toLowerCase().includes(keyword) ||
          node.name?.toLowerCase().includes(keyword) ||
          node.path?.toLowerCase().includes(keyword)
        const matchType = !type || node.menu_type === type
        const selfMatch = matchKeyword && matchType
        if (selfMatch || children.length > 0) {
          return { ...node, children }
        }
        return null
      })
      .filter(Boolean)
  }

  return filterTree(tableData.value)
})

// 编辑时排除自己及子节点的树
const excludeSelfTree = computed(() => {
  if (!isEdit.value || !currentId.value) return treeData.value
  function filter(nodes) {
    return nodes
      .filter((node) => node.id !== currentId.value)
      .map((node) => {
        const children = node.children ? filter(node.children) : []
        return { ...node, children }
      })
  }
  return filter(treeData.value)
})

const fetchData = async () => {
  const res = await getMenuList()
  tableData.value = res.data.list || res.data || []
}

const fetchTree = async () => {
  const res = await getMenuTree()
  treeData.value = res.data
}

onMounted(() => {
  fetchData()
  fetchTree()
})

const handleSearch = () => {
  nextTick(() => {
    expandAll()
  })
}

const handleReset = () => {
  query.value = {
    search: '',
    menu_type: '',
  }
}

const expandAll = () => {
  const expandRows = (rows) => {
    if (!Array.isArray(rows)) return
    rows.forEach((row) => {
      tableRef.value?.toggleRowExpansion?.(row, true)
      if (row.children?.length) expandRows(row.children)
    })
  }
  expandRows(filteredTableData.value)
}

const collapseAll = () => {
  const collapseRows = (rows) => {
    if (!Array.isArray(rows)) return
    rows.forEach((row) => {
      tableRef.value?.toggleRowExpansion?.(row, false)
      if (row.children?.length) collapseRows(row.children)
    })
  }
  collapseRows(filteredTableData.value)
}

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
    keep_alive: true,
    remark: '',
  }
  currentId.value = null
  isEdit.value = false
}

const onDialogClosed = () => {
  formRef.value?.resetFields?.()
  resetForm()
}

const onMenuTypeChange = (val) => {
  if (val === 'DIR') {
    form.value.component = ''
    form.value.permission = ''
    form.value.keep_alive = true
  } else if (val === 'BUTTON') {
    form.value.path = ''
    form.value.component = ''
    form.value.icon = ''
    form.value.is_hidden = false
    form.value.keep_alive = true
  } else {
    form.value.keep_alive = true
  }
}

const handleAdd = () => {
  resetForm()
  dialogTitle.value = '新增菜单'
  dialogVisible.value = true
}

const handleAddChild = (row) => {
  resetForm()
  form.value.parent = row.id
  dialogTitle.value = `新增子菜单（${row.title}）`
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
    keep_alive: row.keep_alive,
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
    const payload = { ...form.value }
    if (payload.menu_type === 'BUTTON') {
      payload.path = ''
      payload.component = ''
      payload.icon = ''
      payload.is_hidden = false
    }
    if (payload.menu_type === 'DIR') {
      payload.component = ''
      payload.permission = ''
    }
    if (isEdit.value) {
      await updateMenu(currentId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createMenu(payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    await fetchData()
    await fetchTree()
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除菜单 "${row.title}" 吗？若存在子菜单将一并删除。`, '提示', { type: 'warning' }).then(async () => {
    await deleteMenu(row.id)
    ElMessage.success('删除成功')
    await fetchData()
    await fetchTree()
  })
}

const selectIcon = (icon) => {
  form.value.icon = icon
  iconDialogVisible.value = false
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
.icon-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
}
.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 4px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}
.icon-item:hover {
  border-color: #409eff;
  color: #409eff;
}
.icon-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
  color: #409eff;
}
.icon-name {
  font-size: 12px;
  margin-top: 6px;
  text-align: center;
  word-break: break-all;
  line-height: 1.2;
}
</style>
