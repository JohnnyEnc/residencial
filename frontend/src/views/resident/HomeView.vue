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
  <div class="space-y-6">
    <header class="reveal">
      <p class="eyebrow">Residencial</p>
      <h1 class="page-title mt-2">
        Hola, {{ auth.user?.name?.split(' ')[0] }}
      </h1>
      <p class="mt-2 text-sm text-lagoon-800/80">
        Vivienda
        <span v-for="u in auth.user?.units" :key="u.id" class="font-semibold text-ink"> {{ u.code }}</span>
      </p>
    </header>

    <div class="reveal-2 grid grid-cols-2 gap-3">
      <div class="stat-tile">
        <p class="relative z-10 text-[11px] font-semibold uppercase tracking-[0.16em] text-lime/90">Pendientes</p>
        <p class="relative z-10 mt-2 font-display text-4xl font-extrabold">{{ pending().length }}</p>
      </div>
      <div class="rounded-[1.35rem] bg-white/75 px-4 py-4 shadow-insetline backdrop-blur">
        <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-lagoon-600">Al día</p>
        <p class="mt-2 font-display text-4xl font-extrabold text-ink">
          {{ charges.filter((c) => c.status === 'paid').length }}
        </p>
      </div>
    </div>

    <section class="reveal-3 space-y-3">
      <h2 class="section-title">Avisos</h2>
      <button
        v-for="a in announcements.slice(0, 4)"
        :key="a.id"
        type="button"
        class="w-full rounded-[1.25rem] px-4 py-3.5 text-left transition"
        :class="a.read ? 'bg-white/60 shadow-insetline' : 'bg-dusk text-white shadow-lift'"
        @click="markRead(a.id)"
      >
        <p class="font-display text-base font-bold tracking-tight">{{ a.title }}</p>
        <p class="mt-1 text-sm" :class="a.read ? 'text-lagoon-800' : 'text-lagoon-100/85'">{{ a.body }}</p>
      </button>
    </section>

    <section class="reveal-4 space-y-3">
      <div class="flex items-end justify-between gap-3">
        <h2 class="section-title">Cuotas</h2>
        <RouterLink to="/app/payments" class="text-xs font-semibold uppercase tracking-[0.14em] text-lagoon-700">
          Ver todas
        </RouterLink>
      </div>
      <div
        v-for="c in charges.slice(0, 3)"
        :key="c.id"
        class="flex items-center justify-between gap-3 border-b border-lagoon-900/8 py-3 last:border-0"
      >
        <div>
          <p class="font-display font-semibold tracking-tight">{{ c.period_label }}</p>
          <p class="text-sm text-lagoon-700">{{ money(c.amount) }}</p>
        </div>
        <StatusBadge :status="c.status" />
      </div>
    </section>

    <RouterLink to="/app/reports/new" class="btn-primary w-full py-3">Reportar incidencia</RouterLink>
  </div>
</template>
