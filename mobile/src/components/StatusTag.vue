<template>
  <van-tag :type="tagType" :color="tagColor" size="medium">
    {{ displayText }}
  </van-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: '' },
  options: { type: Object, default: () => ({}) },
  typeMap: { type: Object, default: () => ({}) },
})

const displayText = computed(() => props.options[props.status] || props.status)

const tagType = computed(() => props.typeMap[props.status] || 'default')

const tagColor = computed(() => {
  const colorMap = {
    primary: '#1989fa',
    success: '#07c160',
    danger: '#ee0a24',
    warning: '#ff976a',
  }
  return colorMap[props.typeMap[props.status]] || undefined
})
</script>
