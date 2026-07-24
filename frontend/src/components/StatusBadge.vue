<script setup lang="ts">
import { statusClass, statusLabel } from '../utils/format'

defineProps<{ status: string }>()
</script>

<template>
  <span
    class="inline-flex rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.12em]"
    :class="statusClass(status)"
  >
    {{ statusLabel(status) }}
  </span>
</template>
