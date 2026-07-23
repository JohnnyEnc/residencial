<script setup lang="ts">
import { onMounted, ref } from 'vue'
import api from '../../api/client'
import type { Report, User } from '../../types'
import StatusBadge from '../../components/StatusBadge.vue'

const reports = ref<Report[]>([])
const staff = ref<User[]>([])
const message = ref('')

async function load() {
  const [r, s] = await Promise.all([
    api.get<Report[]>('/reports'),
    api.get<User[]>('/users', { params: { role: 'staff' } }),
  ])
  reports.value = r.data
  staff.value = s.data
}

async function assign(reportId: number, assigned_to: number) {
  await api.patch(`/reports/${reportId}/assign`, { assigned_to })
  message.value = 'Reporte asignado'
  await load()
}

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="page-title">Reportes</h1>
      <p class="text-sm text-brand-700">Incidencias de vecinos y asignación a personal.</p>
    </div>
    <p v-if="message" class="text-sm text-brand-700">{{ message }}</p>

    <div class="space-y-3">
      <div v-for="r in reports" :key="r.id" class="card space-y-3">
        <div class="flex flex-wrap items-start justify-between gap-2">
          <div>
            <p class="font-semibold">{{ r.title }}</p>
            <p class="text-xs text-brand-700">
              {{ r.category }} · {{ r.unit_code || 'Sin unidad' }} · {{ r.creator_name }}
            </p>
          </div>
          <StatusBadge :status="r.status" />
        </div>
        <p class="text-sm text-brand-800">{{ r.description }}</p>
        <div v-if="r.status === 'open' || !r.assigned_to" class="flex flex-wrap items-center gap-2">
          <select
            class="input max-w-xs"
            @change="assign(r.id, Number(($event.target as HTMLSelectElement).value))"
          >
            <option value="">Asignar a…</option>
            <option v-for="s in staff" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <p v-else class="text-xs text-brand-600">Asignado a: {{ r.assignee_name }}</p>
      </div>
    </div>
  </div>
</template>
