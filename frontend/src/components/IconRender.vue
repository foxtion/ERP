<template>
  <component :is="iconComponent" v-if="iconComponent" />
</template>

<script setup>
import { computed } from 'vue'
import {
  Avatar, Box, Calendar, Document, DocumentAdd,
  DocumentChecked, DocumentCopy, House, Menu, Money,
  OfficeBuilding, Search, Sell, Setting, ShoppingCart,
  Tools, User, UserFilled, Wallet, HomeFilled, Fold, ArrowDown,
} from '@element-plus/icons-vue'

const props = defineProps({
  icon: {
    type: String,
    default: '',
  },
})

const iconMap = {
  Avatar,
  Box,
  Calendar,
  Document,
  DocumentAdd,
  DocumentChecked,
  DocumentCopy,
  House,
  Menu,
  Money,
  OfficeBuilding,
  Search,
  Sell,
  Setting,
  ShoppingCart,
  Tools,
  User,
  UserFilled,
  Wallet,
  HomeFilled,
  Fold,
  ArrowDown,
}

const iconComponent = computed(() => {
  return iconMap[props.icon] || null
})
</script>
