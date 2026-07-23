<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import api from '../../api/client'
import type { UnitCharge } from '../../types'
import StatusBadge from '../../components/StatusBadge.vue'
import { money } from '../../utils/format'

const charges = ref<UnitCharge[]>([])
const message = ref('')
const form = reactive({ charge_id: 0, amount: 0, method: 'transferencia', note: '' })

async function load() {
  const { data } = await api.get<UnitCharge[]>('/charges')
  charges.value = data
}

async function submitPayment(c: UnitCharge) {
  message.value = ''
  try {
    await api.post('/payments/json', {
      charge_id: c.id,
      amount: Number(c.amount),
      method: form.method,
      note: form.note || undefined,
    })
    message.value = 'Comprobante enviado. Pendiente de aprobación.'
    await load()
  } catch (e: any) {
    message.value = e?.response?.data?.detail || 'Error al enviar pago'
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <h1 class="page-title">Mis pagos</h1>
    <p v-if="message" class="text-sm text-brand-700">{{ message }}</p>

    <div v-for="c in charges" :key="c.id" class="card space-y-3">
      <div class="flex items-start justify-between gap-2">
        <div>
          <p class="font-semibold">{{ c.period_label }}</p>
          <p class="text-sm text-brand-700">{{ c.unit_code }} · {{ money(c.amount) }}</p>
        </div>
        <StatusBadge :status="c.status" />
      </div>
      <button
        v-if="c.status === 'pending' || c.status === 'overdue'"
        class="btn-primary w-full"
        @click="submitPayment(c)"
      >
        Enviar comprobante
      </button>
    </div>
  </div>
</template>
