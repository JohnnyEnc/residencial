<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '../../api/client'
import type { ResidentContact, ServiceCategory, ServiceProvider } from '../../types'

const tab = ref<'services' | 'residents'>('services')
const contacts = ref<ResidentContact[]>([])
const services = ref<ServiceProvider[]>([])
const categories = ref<{ value: ServiceCategory; label: string }[]>([])
const filterCategory = ref('')
const query = ref('')

const labels = computed(() => Object.fromEntries(categories.value.map((c) => [c.value, c.label])))

const filteredServices = computed(() =>
  services.value.filter((s) => {
    if (filterCategory.value && s.category !== filterCategory.value) return false
    if (!query.value) return true
    const q = query.value.toLowerCase()
    return (
      s.name.toLowerCase().includes(q) ||
      (s.description || '').toLowerCase().includes(q) ||
      s.phone.includes(q)
    )
  }),
)

function telLink(phone: string | null | undefined) {
  if (!phone) return null
  return `tel:${phone.replace(/[^\d+]/g, '')}`
}

function waLink(phone: string | null | undefined) {
  if (!phone) return null
  let digits = phone.replace(/\D/g, '')
  if (digits.length === 10) digits = `1${digits}`
  return `https://wa.me/${digits}`
}

onMounted(async () => {
  const [c, s, cats] = await Promise.all([
    api.get<ResidentContact[]>('/contacts/residents'),
    api.get<ServiceProvider[]>('/services'),
    api.get<{ value: ServiceCategory; label: string }[]>('/services/categories'),
  ])
  contacts.value = c.data
  services.value = s.data
  categories.value = cats.data
})
</script>

<template>
  <div class="space-y-4">
    <div>
      <h1 class="page-title">Directorio</h1>
      <p class="text-sm text-brand-700">Servicios de mantenimiento y contactos del residencial.</p>
    </div>

    <div class="flex gap-2">
      <button class="btn flex-1" :class="tab === 'services' ? 'btn-primary' : 'btn-secondary'" @click="tab = 'services'">
        Servicios
      </button>
      <button class="btn flex-1" :class="tab === 'residents' ? 'btn-primary' : 'btn-secondary'" @click="tab = 'residents'">
        Vecinos
      </button>
    </div>

    <template v-if="tab === 'services'">
      <div class="space-y-2">
        <select v-model="filterCategory" class="input">
          <option value="">Todas las categorías</option>
          <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
        </select>
        <input v-model="query" class="input" placeholder="Buscar plomería, mecánica…" />
      </div>

      <div class="space-y-3">
        <div v-for="s in filteredServices" :key="s.id" class="card space-y-2">
          <div>
            <p class="font-semibold">{{ s.name }}</p>
            <p class="text-xs font-bold uppercase tracking-wide text-brand-600">
              {{ labels[s.category] || s.category }}
            </p>
            <p v-if="s.description" class="mt-1 text-sm text-brand-800">{{ s.description }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <a v-if="telLink(s.phone)" :href="telLink(s.phone)!" class="btn-primary">Llamar {{ s.phone }}</a>
            <a
              v-if="waLink(s.whatsapp || s.phone)"
              :href="waLink(s.whatsapp || s.phone)!"
              target="_blank"
              rel="noopener"
              class="btn-secondary"
            >
              WhatsApp
            </a>
          </div>
        </div>
        <p v-if="!filteredServices.length" class="text-sm text-brand-600">No hay proveedores para ese filtro.</p>
      </div>
    </template>

    <template v-else>
      <div class="space-y-3">
        <div v-for="c in contacts" :key="c.id" class="card space-y-2">
          <div>
            <p class="font-semibold">{{ c.name }}</p>
            <p class="text-xs text-brand-700">{{ c.unit_codes.join(', ') || 'Sin vivienda' }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <a v-if="telLink(c.phone)" :href="telLink(c.phone)!" class="btn-primary">{{ c.phone }}</a>
            <a
              v-if="c.whatsapp && waLink(c.whatsapp)"
              :href="waLink(c.whatsapp)!"
              target="_blank"
              rel="noopener"
              class="btn-secondary"
            >
              WhatsApp
            </a>
          </div>
        </div>
        <p v-if="!contacts.length" class="text-sm text-brand-600">
          Aún no hay vecinos visibles en el directorio.
        </p>
      </div>
    </template>
  </div>
</template>
