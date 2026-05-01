<template>
  <div class="card-item" @click="$emit('click', item)">
    <div class="card-header">
      <span class="title">{{ title }}</span>
      <slot name="tag" />
    </div>
    <div class="card-body">
      <slot name="body" />
    </div>
    <div class="card-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  item: { type: Object, default: () => ({}) },
  title: { type: String, default: '' },
})
defineEmits(['click'])
</script>

<style scoped>
.card-item {
  margin: 8px 12px;
  background-color: #fff;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}
.card-body {
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
  flex-wrap: wrap;
}
</style>
