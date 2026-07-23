<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api/client'
import type { Report } from '../../types'
import StatusBadge from '../../components/StatusBadge.vue'

const route = useRoute()
const router = useRouter()
const report = ref<Report | null>(null)
const note = ref('')
const statusTo = ref('in_progress')

async function load() {
  const { data } = await api.get<Report>(`/reports/${route.params.id}`)
  report.value = data
}

async function addUpdate() {
  await api.post(`/reports/${route.params.id}/updates`, {
    note: note.value,
    status_to: statusTo.value,
  })
  note.value = ''
  await load()
}

onMounted(load)
</script>

<template>
  <div v-if="report" class="space-y-4">
    <button class="text-sm font-semibold text-brand-700" @click="router.back()">← Volver</button>
    <div class="card space-y-2">
      <div class="flex items-start justify-between">
        <h1 class="font-display text-2xl">{{ report.title }}</h1>
        <StatusBadge :status="report.status" />
      </div>
      <p class="text-sm">{{ report.description }}</p>
      <p class="text-xs text-brand-600">{{ report.category }} · {{ report.location }}</p>
    </div>

    <div class="card space-y-3">
      <h2 class="font-semibold">Actualizar seguimiento</h2>
      <select v-model="statusTo" class="input">
        <option value="in_progress">En proceso</option>
        <option value="resolved">Resuelto</option>
        <option value="closed">Cerrado</option>
      </select>
      <textarea v-model="note" class="input min-h-[90px]" placeholder="Nota de avance" required />
      <button class="btn-primary w-full" :disabled="!note" @click="addUpdate">Guardar</button>
    </div>

    <div class="space-y-2">
      <h2 class="font-semibold">Historial</h2>
      <div v-for="u in report.updates" :key="u.id" class="rounded-xl bg-white px-3 py-2 text-sm ring-1 ring-brand-100">
        <p>{{ u.note }}</p>
        <p class="text-xs text-brand-600">{{ u.status_to }} · {{ new Date(u.created_at).toLocaleString() }}</p>
      </div>
    </div>
  </div>
</template>
