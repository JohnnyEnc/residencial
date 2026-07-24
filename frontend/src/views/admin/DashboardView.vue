<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Doughnut, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'
import api from '../../api/client'
import type { DashboardStats } from '../../types'
import { money } from '../../utils/format'
import StatusBadge from '../../components/StatusBadge.vue'

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const stats = ref<DashboardStats | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get<DashboardStats>('/dashboard/stats')
    stats.value = data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Error al cargar dashboard'
  } finally {
    loading.value = false
  }
})

const doughnutData = computed(() => {
  if (!stats.value) return { labels: [], datasets: [] }
  return {
    labels: ['Pagado', 'Pendiente', 'Vencido', 'En revisión'],
    datasets: [
      {
        data: [
          Number(stats.value.paid_amount),
          Number(stats.value.pending_amount),
          Number(stats.value.overdue_amount),
          Number(stats.value.submitted_amount),
        ],
        backgroundColor: ['#1a6c59', '#d97706', '#e4572e', '#3ea388'],
        borderWidth: 0,
      },
    ],
  }
})

const barData = computed(() => {
  if (!stats.value) return { labels: [], datasets: [] }
  return {
    labels: stats.value.monthly_collection.map((m) => m.label),
    datasets: [
      {
        label: 'Pagado',
        data: stats.value.monthly_collection.map((m) => Number(m.paid)),
        backgroundColor: '#1a6c59',
      },
      {
        label: 'Pendiente / deuda',
        data: stats.value.monthly_collection.map(
          (m) => Number(m.pending) + Number(m.overdue) + Number(m.submitted),
        ),
        backgroundColor: '#e4572e',
      },
    ],
  }
})

const reportsBar = computed(() => {
  if (!stats.value) return { labels: [], datasets: [] }
  return {
    labels: stats.value.reports_by_status.map((r) => r.status),
    datasets: [
      {
        label: 'Reportes',
        data: stats.value.reports_by_status.map((r) => r.count),
        backgroundColor: '#c6f04d',
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { usePointStyle: true, boxWidth: 8, font: { family: 'Syne' } },
    },
  },
}
</script>

<template>
  <div class="space-y-7">
    <div class="reveal">
      <p class="eyebrow">Operación</p>
      <h1 class="page-title mt-2">Dashboard</h1>
      <p class="mt-2 max-w-xl text-sm text-lagoon-800/80">
        Recaudación, deudas y pulso del residencial en un vistazo.
      </p>
    </div>

    <p v-if="loading" class="text-sm text-lagoon-700">Cargando…</p>
    <p v-else-if="error" class="text-sm text-ember">{{ error }}</p>

    <template v-else-if="stats">
      <div class="reveal-2 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div class="stat-tile">
          <p class="relative z-10 text-[11px] font-semibold uppercase tracking-[0.16em] text-lime/90">Tasa de cobro</p>
          <p class="relative z-10 mt-2 font-display text-4xl font-extrabold">{{ stats.collection_rate }}%</p>
        </div>
        <div class="panel">
          <p class="eyebrow">Recaudado</p>
          <p class="mt-2 font-display text-3xl font-extrabold text-lagoon-800">{{ money(stats.paid_amount) }}</p>
        </div>
        <div class="panel">
          <p class="eyebrow">Por cobrar</p>
          <p class="mt-2 font-display text-3xl font-extrabold text-ember">
            {{ money(Number(stats.pending_amount) + Number(stats.overdue_amount) + Number(stats.submitted_amount)) }}
          </p>
        </div>
        <div class="panel">
          <p class="eyebrow">Reportes abiertos</p>
          <p class="mt-2 font-display text-3xl font-extrabold">{{ stats.open_reports }}</p>
          <p class="mt-1 text-xs text-lagoon-600">{{ stats.pending_payment_reviews }} pagos por revisar</p>
        </div>
      </div>

      <div class="reveal-3 grid gap-4 lg:grid-cols-2">
        <div class="panel">
          <h2 class="section-title">Pagado vs deuda</h2>
          <div class="mt-4 h-64">
            <Doughnut :data="doughnutData" :options="chartOptions" />
          </div>
        </div>
        <div class="panel">
          <h2 class="section-title">Recaudación mensual</h2>
          <div class="mt-4 h-64">
            <Bar :data="barData" :options="chartOptions" />
          </div>
        </div>
      </div>

      <div class="reveal-4 grid gap-4 lg:grid-cols-2">
        <div class="panel">
          <h2 class="section-title mb-3">Quienes ya pagaron</h2>
          <div class="max-h-80 space-y-1 overflow-y-auto">
            <div
              v-for="row in stats.paid_units"
              :key="'p-' + row.unit_id"
              class="flex items-center justify-between gap-3 border-b border-lagoon-900/6 py-2.5 text-sm last:border-0"
            >
              <div>
                <p class="font-display font-semibold">{{ row.unit_code }}</p>
                <p class="text-xs text-lagoon-700">{{ row.resident_name || 'Sin residente' }}</p>
              </div>
              <div class="text-right">
                <p class="font-semibold">{{ money(row.amount) }}</p>
                <StatusBadge status="paid" />
              </div>
            </div>
            <p v-if="!stats.paid_units.length" class="text-sm text-lagoon-600">Nadie ha pagado aún.</p>
          </div>
        </div>

        <div class="panel">
          <h2 class="section-title mb-3">Quienes faltan por pagar</h2>
          <div class="max-h-80 space-y-1 overflow-y-auto">
            <div
              v-for="row in stats.unpaid_units"
              :key="'u-' + row.unit_id"
              class="flex items-center justify-between gap-3 border-b border-lagoon-900/6 py-2.5 text-sm last:border-0"
            >
              <div>
                <p class="font-display font-semibold">{{ row.unit_code }}</p>
                <p class="text-xs text-lagoon-700">{{ row.resident_name || 'Sin residente' }}</p>
              </div>
              <div class="text-right">
                <p class="font-semibold">{{ money(row.amount) }}</p>
                <StatusBadge :status="row.status" />
              </div>
            </div>
            <p v-if="!stats.unpaid_units.length" class="text-sm text-lagoon-600">Todas las viviendas al día.</p>
          </div>
        </div>
      </div>

      <div class="grid gap-3 sm:grid-cols-3">
        <div class="rounded-[1.25rem] bg-dusk px-4 py-4 text-white">
          <p class="text-xs uppercase tracking-[0.14em] text-lime/80">Viviendas</p>
          <p class="mt-1 font-display text-3xl font-extrabold">{{ stats.total_units }}</p>
        </div>
        <div class="rounded-[1.25rem] bg-dusk px-4 py-4 text-white">
          <p class="text-xs uppercase tracking-[0.14em] text-lime/80">Vecinos</p>
          <p class="mt-1 font-display text-3xl font-extrabold">{{ stats.total_residents }}</p>
        </div>
        <div class="rounded-[1.25rem] bg-dusk px-4 py-4 text-white">
          <p class="text-xs uppercase tracking-[0.14em] text-lime/80">Personal</p>
          <p class="mt-1 font-display text-3xl font-extrabold">{{ stats.total_staff }}</p>
        </div>
      </div>

      <div class="panel">
        <h2 class="section-title">Reportes por estado</h2>
        <div class="mt-4 h-56">
          <Bar :data="reportsBar" :options="chartOptions" />
        </div>
      </div>
    </template>
  </div>
</template>
