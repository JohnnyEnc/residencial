<script setup lang="ts">
import { statusClass, statusLabel } from '../utils/format'

defineProps<{ status: string }>()
</script>

<template>
  <span
    class="inline-flex rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wide"
    :class="statusClass(status)"
  >
    {{ statusLabel(status) }}
  </span>
</template>
