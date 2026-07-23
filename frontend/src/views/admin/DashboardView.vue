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
        backgroundColor: ['#317e6c', '#d97706', '#c45c3e', '#0284c7'],
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
        backgroundColor: '#317e6c',
      },
      {
        label: 'Pendiente / deuda',
        data: stats.value.monthly_collection.map(
          (m) => Number(m.pending) + Number(m.overdue) + Number(m.submitted),
        ),
        backgroundColor: '#c45c3e',
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
        backgroundColor: '#4a9a86',
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' as const } },
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="page-title">Dashboard</h1>
      <p class="mt-1 text-sm text-brand-700">Resumen de recaudación, deudas y operación del residencial.</p>
    </div>

    <p v-if="loading" class="text-sm text-brand-700">Cargando…</p>
    <p v-else-if="error" class="text-sm text-coral">{{ error }}</p>

    <template v-else-if="stats">
      <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div class="card">
          <p class="text-xs font-semibold uppercase tracking-wide text-brand-600">Tasa de cobro</p>
          <p class="mt-2 font-display text-3xl">{{ stats.collection_rate }}%</p>
        </div>
        <div class="card">
          <p class="text-xs font-semibold uppercase tracking-wide text-brand-600">Recaudado</p>
          <p class="mt-2 font-display text-3xl text-brand-700">{{ money(stats.paid_amount) }}</p>
        </div>
        <div class="card">
          <p class="text-xs font-semibold uppercase tracking-wide text-brand-600">Por cobrar</p>
          <p class="mt-2 font-display text-3xl text-coral">
            {{ money(Number(stats.pending_amount) + Number(stats.overdue_amount) + Number(stats.submitted_amount)) }}
          </p>
        </div>
        <div class="card">
          <p class="text-xs font-semibold uppercase tracking-wide text-brand-600">Reportes abiertos</p>
          <p class="mt-2 font-display text-3xl">{{ stats.open_reports }}</p>
          <p class="mt-1 text-xs text-brand-600">{{ stats.pending_payment_reviews }} pagos por revisar</p>
        </div>
      </div>

      <div class="grid gap-4 lg:grid-cols-2">
        <div class="card">
          <h2 class="font-display text-xl">Pagado vs deuda (periodo actual)</h2>
          <div class="mt-4 h-64">
            <Doughnut :data="doughnutData" :options="chartOptions" />
          </div>
        </div>
        <div class="card">
          <h2 class="font-display text-xl">Recaudación mensual</h2>
          <div class="mt-4 h-64">
            <Bar :data="barData" :options="chartOptions" />
          </div>
        </div>
      </div>

      <div class="grid gap-4 lg:grid-cols-2">
        <div class="card">
          <h2 class="mb-3 font-display text-xl">Quienes ya pagaron</h2>
          <div class="max-h-80 space-y-2 overflow-y-auto">
            <div
              v-for="row in stats.paid_units"
              :key="'p-' + row.unit_id"
              class="flex items-center justify-between rounded-xl bg-brand-50 px-3 py-2 text-sm"
            >
              <div>
                <p class="font-semibold">{{ row.unit_code }}</p>
                <p class="text-xs text-brand-700">{{ row.resident_name || 'Sin residente' }}</p>
              </div>
              <div class="text-right">
                <p class="font-semibold">{{ money(row.amount) }}</p>
                <StatusBadge status="paid" />
              </div>
            </div>
            <p v-if="!stats.paid_units.length" class="text-sm text-brand-600">Nadie ha pagado aún.</p>
          </div>
        </div>

        <div class="card">
          <h2 class="mb-3 font-display text-xl">Quienes faltan por pagar</h2>
          <div class="max-h-80 space-y-2 overflow-y-auto">
            <div
              v-for="row in stats.unpaid_units"
              :key="'u-' + row.unit_id"
              class="flex items-center justify-between rounded-xl bg-sand px-3 py-2 text-sm ring-1 ring-brand-100"
            >
              <div>
                <p class="font-semibold">{{ row.unit_code }}</p>
                <p class="text-xs text-brand-700">{{ row.resident_name || 'Sin residente' }}</p>
              </div>
              <div class="text-right">
                <p class="font-semibold">{{ money(row.amount) }}</p>
                <StatusBadge :status="row.status" />
              </div>
            </div>
            <p v-if="!stats.unpaid_units.length" class="text-sm text-brand-600">Todas las viviendas al día.</p>
          </div>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-3">
        <div class="card sm:col-span-1">
          <p class="text-sm text-brand-700">Viviendas</p>
          <p class="font-display text-3xl">{{ stats.total_units }}</p>
        </div>
        <div class="card sm:col-span-1">
          <p class="text-sm text-brand-700">Vecinos</p>
          <p class="font-display text-3xl">{{ stats.total_residents }}</p>
        </div>
        <div class="card sm:col-span-1">
          <p class="text-sm text-brand-700">Personal</p>
          <p class="font-display text-3xl">{{ stats.total_staff }}</p>
        </div>
      </div>

      <div class="card">
        <h2 class="font-display text-xl">Reportes por estado</h2>
        <div class="mt-4 h-56">
          <Bar :data="reportsBar" :options="chartOptions" />
        </div>
      </div>
    </template>
  </div>
</template>
