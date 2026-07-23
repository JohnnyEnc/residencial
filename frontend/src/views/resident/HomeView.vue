<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../../api/client'
import type { Announcement, UnitCharge } from '../../types'
import StatusBadge from '../../components/StatusBadge.vue'
import { money } from '../../utils/format'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const announcements = ref<Announcement[]>([])
const charges = ref<UnitCharge[]>([])

onMounted(async () => {
  const [a, c] = await Promise.all([
    api.get<Announcement[]>('/announcements'),
    api.get<UnitCharge[]>('/charges'),
  ])
  announcements.value = a.data
  charges.value = c.data
})

async function markRead(id: number) {
  await api.post(`/announcements/${id}/read`)
  const item = announcements.value.find((x) => x.id === id)
  if (item) item.read = true
}

const pending = () => charges.value.filter((c) => c.status !== 'paid')
</script>

<template>
  <div class="space-y-5">
    <div>
      <h1 class="page-title">Hola, {{ auth.user?.name?.split(' ')[0] }}</h1>
      <p class="text-sm text-brand-700">
        Vivienda:
        <span v-for="u in auth.user?.units" :key="u.id" class="font-semibold">{{ u.code }} </span>
      </p>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div class="card">
        <p class="text-xs uppercase text-brand-600">Pendientes</p>
        <p class="font-display text-3xl">{{ pending().length }}</p>
      </div>
      <div class="card">
        <p class="text-xs uppercase text-brand-600">Al día</p>
        <p class="font-display text-3xl">{{ charges.filter((c) => c.status === 'paid').length }}</p>
      </div>
    </div>

    <section class="space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="font-display text-xl">Avisos</h2>
      </div>
      <div
        v-for="a in announcements.slice(0, 4)"
        :key="a.id"
        class="card cursor-pointer"
        :class="{ 'ring-2 ring-brand-300': !a.read }"
        @click="markRead(a.id)"
      >
        <p class="font-semibold">{{ a.title }}</p>
        <p class="mt-1 text-sm text-brand-800">{{ a.body }}</p>
      </div>
    </section>

    <section class="space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="font-display text-xl">Cuotas recientes</h2>
        <RouterLink to="/app/payments" class="text-sm font-semibold text-brand-700">Ver todas</RouterLink>
      </div>
      <div v-for="c in charges.slice(0, 3)" :key="c.id" class="card flex items-center justify-between">
        <div>
          <p class="font-semibold">{{ c.period_label }}</p>
          <p class="text-sm">{{ money(c.amount) }}</p>
        </div>
        <StatusBadge :status="c.status" />
      </div>
    </section>

    <RouterLink to="/app/reports/new" class="btn-primary w-full">Reportar incidencia</RouterLink>
  </div>
</template>
