<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import api from '../../api/client'
import type { FeePeriod, Payment, UnitCharge } from '../../types'
import StatusBadge from '../../components/StatusBadge.vue'
import { money } from '../../utils/format'

const periods = ref<FeePeriod[]>([])
const charges = ref<UnitCharge[]>([])
const payments = ref<Payment[]>([])
const selectedPeriod = ref<number | null>(null)
const message = ref('')
const form = reactive({
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  amount_default: 3500,
  due_date: '',
  label: '',
})

async function load() {
  const [p, pay] = await Promise.all([
    api.get<FeePeriod[]>('/fee-periods'),
    api.get<Payment[]>('/payments'),
  ])
  periods.value = p.data
  payments.value = pay.data
  if (!selectedPeriod.value && periods.value.length) {
    selectedPeriod.value = periods.value[0].id
  }
  await loadCharges()
}

async function loadCharges() {
  const params = selectedPeriod.value ? { period_id: selectedPeriod.value } : {}
  const { data } = await api.get<UnitCharge[]>('/charges', { params })
  charges.value = data
}

async function createPeriod() {
  message.value = ''
  try {
    await api.post('/fee-periods', form)
    message.value = 'Periodo creado'
    await load()
  } catch (e: any) {
    message.value = e?.response?.data?.detail || 'Error'
  }
}

async function generate() {
  if (!selectedPeriod.value) return
  await api.post(`/fee-periods/${selectedPeriod.value}/generate-charges`)
  message.value = 'Cargos generados'
  await loadCharges()
}

async function review(id: number, status: 'approved' | 'rejected') {
  await api.patch(`/payments/${id}/review`, { status })
  message.value = status === 'approved' ? 'Pago aprobado' : 'Pago rechazado'
  await load()
}

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="page-title">Cuotas y pagos</h1>
      <p class="text-sm text-brand-700">Genera periodos, cargos y concilia comprobantes.</p>
    </div>

    <form class="card grid gap-3 md:grid-cols-5" @submit.prevent="createPeriod">
      <div>
        <label class="label">Año</label>
        <input v-model.number="form.year" type="number" class="input" required />
      </div>
      <div>
        <label class="label">Mes</label>
        <input v-model.number="form.month" type="number" min="1" max="12" class="input" required />
      </div>
      <div>
        <label class="label">Monto</label>
        <input v-model.number="form.amount_default" type="number" class="input" required />
      </div>
      <div>
        <label class="label">Vence</label>
        <input v-model="form.due_date" type="date" class="input" required />
      </div>
      <div class="flex items-end">
        <button class="btn-primary w-full">Crear periodo</button>
      </div>
    </form>

    <div class="card flex flex-wrap items-end gap-3">
      <div class="min-w-[200px] flex-1">
        <label class="label">Periodo</label>
        <select v-model.number="selectedPeriod" class="input" @change="loadCharges">
          <option v-for="p in periods" :key="p.id" :value="p.id">
            {{ p.label || `${p.month}/${p.year}` }}
          </option>
        </select>
      </div>
      <button class="btn-secondary" @click="generate">Generar cargos</button>
    </div>
    <p v-if="message" class="text-sm text-brand-700">{{ message }}</p>

    <div class="card overflow-x-auto">
      <h2 class="mb-3 font-display text-xl">Cargos</h2>
      <table class="w-full min-w-[520px] text-sm">
        <thead class="text-xs uppercase text-brand-600">
          <tr>
            <th class="pb-2 text-left">Vivienda</th>
            <th class="pb-2 text-left">Periodo</th>
            <th class="pb-2 text-left">Monto</th>
            <th class="pb-2 text-left">Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in charges" :key="c.id" class="border-t border-brand-50">
            <td class="py-2 font-semibold">{{ c.unit_code }}</td>
            <td>{{ c.period_label }}</td>
            <td>{{ money(c.amount) }}</td>
            <td><StatusBadge :status="c.status" /></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="card space-y-3">
      <h2 class="font-display text-xl">Comprobantes por revisar</h2>
      <div
        v-for="p in payments.filter((x) => x.status === 'submitted')"
        :key="p.id"
        class="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-sand px-3 py-3 ring-1 ring-brand-100"
      >
        <div>
          <p class="font-semibold">Pago #{{ p.id }} · cargo {{ p.charge_id }}</p>
          <p class="text-sm text-brand-700">{{ money(p.amount) }} · {{ p.method || 'método n/d' }}</p>
        </div>
        <div class="flex gap-2">
          <button class="btn-primary" @click="review(p.id, 'approved')">Aprobar</button>
          <button class="btn-danger" @click="review(p.id, 'rejected')">Rechazar</button>
        </div>
      </div>
      <p v-if="!payments.some((x) => x.status === 'submitted')" class="text-sm text-brand-600">
        No hay comprobantes pendientes.
      </p>
    </div>
  </div>
</template>
