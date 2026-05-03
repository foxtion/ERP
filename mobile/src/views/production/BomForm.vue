<template>
  <div class="form-page">
    <van-form @submit="onSubmit" class="form-content">
      <van-cell-group inset>
        <van-field
          v-model="form.product_name"
          name="product_name"
          label="产品名称"
          placeholder="请输入产品名称"
          :rules="[{ required: true, message: '请输入产品名称' }]"
        />
        <van-field
          v-model="form.product_code"
          name="product_code"
          label="产品编码"
          placeholder="请输入产品编码"
          :rules="[{ required: true, message: '请输入产品编码' }]"
        />
        <van-field
          v-model="form.version"
          name="version"
          label="版本"
          placeholder="请输入版本"
        />
        <van-field name="is_active" label="是否启用">
          <template #input>
            <van-switch v-model="form.is_active" size="20" />
          </template>
        </van-field>
        <van-field
          v-model="form.remark"
          name="remark"
          label="备注"
          type="textarea"
          rows="2"
          placeholder="请输入备注（可选）"
        />
      </van-cell-group>

      <div class="section-title">
        <span>BOM明细</span>
        <van-button size="small" type="primary" plain @click="addItem">+ 添加明细</van-button>
      </div>

      <div v-for="(item, index) in form.items" :key="index" class="item-card">
        <div class="item-header">
          <span class="item-index">明细 {{ index + 1 }}</span>
          <van-button size="mini" type="danger" plain @click="removeItem(index)">删除</van-button>
        </div>
        <van-field
          v-model="item.material_name"
          label="物料名称"
          placeholder="请输入物料名称"
          :rules="[{ required: true, message: '请输入物料名称' }]"
        />
        <van-field
          v-model="item.spec"
          label="规格型号"
          placeholder="请输入规格型号"
        />
        <van-field
          v-model="item.quantity"
          label="用量"
          type="number"
          placeholder="请输入用量"
        />
        <van-field
          v-model="item.unit"
          label="单位"
          placeholder="请输入单位"
        />
        <van-field
          v-model="item.unit_price"
          label="单价"
          type="number"
          placeholder="请输入单价"
        />
        <van-field
          v-model="item.remark"
          label="备注"
          type="textarea"
          rows="1"
          placeholder="请输入备注"
        />
      </div>

      <div v-if="form.items.length === 0" class="empty-tip">暂无明细，请点击上方按钮添加</div>

      <div class="form-actions">
        <van-button round block type="primary" native-type="submit" :loading="submitting">
          {{ isEdit ? '保存' : '提交' }}
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createBom, updateBom, getBomDetail } from '@/api/production'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const submitting = ref(false)

const form = ref({
  product_name: '',
  product_code: '',
  version: 'V1.0',
  is_active: true,
  remark: '',
  items: [],
})

const addItem = () => {
  form.value.items.push({
    material_name: '',
    spec: '',
    quantity: '1',
    unit: '件',
    unit_price: '0',
    remark: '',
  })
}

const removeItem = (index) => {
  form.value.items.splice(index, 1)
}

const onSubmit = async () => {
  if (form.value.items.length === 0) {
    showToast('请至少添加一条BOM明细')
    return
  }
  submitting.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })
  try {
    const data = {
      product_name: form.value.product_name,
      product_code: form.value.product_code,
      version: form.value.version || 'V1.0',
      is_active: form.value.is_active,
      remark: form.value.remark || null,
      items: form.value.items.map(item => ({
        material_name: item.material_name,
        spec: item.spec || null,
        quantity: item.quantity !== '' ? parseFloat(item.quantity) : 1,
        unit: item.unit || '件',
        unit_price: item.unit_price !== '' ? parseFloat(item.unit_price) : 0,
        remark: item.remark || null,
      })),
    }
    if (isEdit.value) {
      await updateBom(route.params.id, data)
    } else {
      await createBom(data)
    }
    closeToast()
    showToast(isEdit.value ? '保存成功' : '新增成功')
    router.back()
  } catch (e) {
    closeToast()
    showToast(e?.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  if (route.params.id) {
    isEdit.value = true
    try {
      const res = await getBomDetail(route.params.id)
      const item = res.data
      form.value.product_name = item.product_name || ''
      form.value.product_code = item.product_code || ''
      form.value.version = item.version || 'V1.0'
      form.value.is_active = item.is_active !== false
      form.value.remark = item.remark || ''
      form.value.items = (item.items || []).map(i => ({
        material_name: i.material_name || '',
        spec: i.spec || '',
        quantity: i.quantity != null ? String(i.quantity) : '1',
        unit: i.unit || '件',
        unit_price: i.unit_price != null ? String(i.unit_price) : '0',
        remark: i.remark || '',
      }))
    } catch (e) {
      showToast('加载数据失败')
    }
  }
})
</script>

<style scoped>
.form-page {
  min-height: 100vh;
  background: #f7f8fa;
}
.form-content {
  padding-top: 12px;
}
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: bold;
  color: #666;
  padding: 16px 12px 8px;
}
.item-card {
  margin: 0 12px 10px;
  background: #fff;
  border-radius: 8px;
  padding: 12px;
}
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.item-index {
  font-size: 14px;
  font-weight: 600;
  color: #323233;
}
.empty-tip {
  text-align: center;
  font-size: 13px;
  color: #969799;
  padding: 20px;
}
.form-actions {
  margin: 20px 16px 40px;
}
</style>
