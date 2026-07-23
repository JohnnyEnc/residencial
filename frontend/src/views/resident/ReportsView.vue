<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../../api/client'
import type { Report } from '../../types'
import StatusBadge from '../../components/StatusBadge.vue'

const reports = ref<Report[]>([])

onMounted(async () => {
  const { data } = await api.get<Report[]>('/reports')
  reports.value = data
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="page-title">Mis reportes</h1>
      <RouterLink to="/app/reports/new" class="btn-primary">Nuevo</RouterLink>
    </div>
    <div v-for="r in reports" :key="r.id" class="card space-y-2">
      <div class="flex items-start justify-between gap-2">
        <p class="font-semibold">{{ r.title }}</p>
        <StatusBadge :status="r.status" />
      </div>
      <p class="text-sm text-brand-800">{{ r.description }}</p>
      <p class="text-xs text-brand-600">{{ r.category }} · {{ r.location || 'Sin ubicación' }}</p>
    </div>
    <p v-if="!reports.length" class="text-sm text-brand-600">Aún no has creado reportes.</p>
  </div>
</template>
