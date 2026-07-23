<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import api from '../../api/client'
import type { ResidentContact, ServiceCategory, ServiceProvider } from '../../types'

const tab = ref<'residents' | 'services'>('residents')
const contacts = ref<ResidentContact[]>([])
const services = ref<ServiceProvider[]>([])
const categories = ref<{ value: ServiceCategory; label: string }[]>([])
const message = ref('')
const filterCategory = ref<string>('')
const query = ref('')

const editingContact = reactive({
  id: 0,
  phone: '',
  phone_secondary: '',
  whatsapp: '',
  show_in_directory: true,
})

const serviceForm = reactive({
  name: '',
  category: 'plomeria' as ServiceCategory,
  phone: '',
  phone_alt: '',
  whatsapp: '',
  description: '',
})

const categoryLabel = computed(() => {
  const map = Object.fromEntries(categories.value.map((c) => [c.value, c.label]))
  return (value: string) => map[value] || value
})

async function load() {
  const [c, s, cats] = await Promise.all([
    api.get<ResidentContact[]>('/contacts/residents'),
    api.get<ServiceProvider[]>('/services', { params: { include_inactive: true } }),
    api.get<{ value: ServiceCategory; label: string }[]>('/services/categories'),
  ])
  contacts.value = c.data
  services.value = s.data
  categories.value = cats.data
}

function startEdit(contact: ResidentContact) {
  editingContact.id = contact.id
  editingContact.phone = contact.phone || ''
  editingContact.phone_secondary = contact.phone_secondary || ''
  editingContact.whatsapp = contact.whatsapp || ''
  editingContact.show_in_directory = contact.show_in_directory
}

async function saveContact() {
  message.value = ''
  try {
    await api.patch(`/contacts/residents/${editingContact.id}`, {
      phone: editingContact.phone || null,
      phone_secondary: editingContact.phone_secondary || null,
      whatsapp: editingContact.whatsapp || null,
      show_in_directory: editingContact.show_in_directory,
    })
    editingContact.id = 0
    message.value = 'Contacto actualizado'
    await load()
  } catch (e: any) {
    message.value = e?.response?.data?.detail || 'Error al guardar contacto'
  }
}

async function createService() {
  message.value = ''
  try {
    await api.post('/services', {
      ...serviceForm,
      phone_alt: serviceForm.phone_alt || null,
      whatsapp: serviceForm.whatsapp || null,
      description: serviceForm.description || null,
    })
    serviceForm.name = ''
    serviceForm.phone = ''
    serviceForm.phone_alt = ''
    serviceForm.whatsapp = ''
    serviceForm.description = ''
    message.value = 'Proveedor agregado al directorio'
    await load()
  } catch (e: any) {
    message.value = e?.response?.data?.detail || 'Error al crear proveedor'
  }
}

async function toggleService(s: ServiceProvider) {
  await api.patch(`/services/${s.id}`, { active: !s.active })
  await load()
}

async function removeService(id: number) {
  await api.delete(`/services/${id}`)
  await load()
}

const filteredServices = computed(() => {
  return services.value.filter((s) => {
    if (filterCategory.value && s.category !== filterCategory.value) return false
    if (query.value) {
      const q = query.value.toLowerCase()
      return (
        s.name.toLowerCase().includes(q) ||
        (s.description || '').toLowerCase().includes(q) ||
        s.phone.includes(q)
      )
    }
    return true
  })
})

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="page-title">Contactos y directorio</h1>
      <p class="text-sm text-brand-700">Teléfonos de residentes y proveedores de mantenimiento.</p>
    </div>

    <div class="flex gap-2">
      <button class="btn" :class="tab === 'residents' ? 'btn-primary' : 'btn-secondary'" @click="tab = 'residents'">
        Residentes
      </button>
      <button class="btn" :class="tab === 'services' ? 'btn-primary' : 'btn-secondary'" @click="tab = 'services'">
        Servicios
      </button>
    </div>
    <p v-if="message" class="text-sm text-brand-700">{{ message }}</p>

    <template v-if="tab === 'residents'">
      <div class="space-y-3">
        <div v-for="c in contacts" :key="c.id" class="card space-y-2">
          <div class="flex flex-wrap items-start justify-between gap-2">
            <div>
              <p class="font-semibold">{{ c.name }}</p>
              <p class="text-xs text-brand-700">
                {{ c.unit_codes.join(', ') || 'Sin vivienda' }}
                · {{ c.show_in_directory ? 'Visible en directorio' : 'Oculto' }}
              </p>
              <p class="mt-1 text-sm">Tel: {{ c.phone || '—' }} · WA: {{ c.whatsapp || '—' }}</p>
            </div>
            <button class="btn-secondary" @click="startEdit(c)">Editar</button>
          </div>
          <form
            v-if="editingContact.id === c.id"
            class="grid gap-2 border-t border-brand-50 pt-3 md:grid-cols-2"
            @submit.prevent="saveContact"
          >
            <div>
              <label class="label">Teléfono</label>
              <input v-model="editingContact.phone" class="input" />
            </div>
            <div>
              <label class="label">Tel. secundario</label>
              <input v-model="editingContact.phone_secondary" class="input" />
            </div>
            <div>
              <label class="label">WhatsApp</label>
              <input v-model="editingContact.whatsapp" class="input" />
            </div>
            <label class="flex items-end gap-2 pb-2 text-sm">
              <input v-model="editingContact.show_in_directory" type="checkbox" />
              Mostrar en directorio
            </label>
            <div class="md:col-span-2 flex gap-2">
              <button class="btn-primary">Guardar</button>
              <button type="button" class="btn-secondary" @click="editingContact.id = 0">Cancelar</button>
            </div>
          </form>
        </div>
      </div>
    </template>

    <template v-else>
      <form class="card grid gap-3 md:grid-cols-2" @submit.prevent="createService">
        <div>
          <label class="label">Nombre</label>
          <input v-model="serviceForm.name" class="input" required />
        </div>
        <div>
          <label class="label">Categoría</label>
          <select v-model="serviceForm.category" class="input">
            <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
        </div>
        <div>
          <label class="label">Teléfono</label>
          <input v-model="serviceForm.phone" class="input" required />
        </div>
        <div>
          <label class="label">WhatsApp</label>
          <input v-model="serviceForm.whatsapp" class="input" />
        </div>
        <div class="md:col-span-2">
          <label class="label">Descripción</label>
          <input v-model="serviceForm.description" class="input" placeholder="Qué servicios ofrece" />
        </div>
        <div class="md:col-span-2">
          <button class="btn-primary">Agregar al directorio</button>
        </div>
      </form>

      <div class="flex flex-wrap gap-2">
        <select v-model="filterCategory" class="input max-w-xs">
          <option value="">Todas las categorías</option>
          <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
        </select>
        <input v-model="query" class="input max-w-xs" placeholder="Buscar…" />
      </div>

      <div class="space-y-3">
        <div v-for="s in filteredServices" :key="s.id" class="card flex flex-wrap items-start justify-between gap-3">
          <div>
            <p class="font-semibold">{{ s.name }}</p>
            <p class="text-xs uppercase text-brand-600">{{ categoryLabel(s.category) }}</p>
            <p class="mt-1 text-sm">{{ s.phone }} <span v-if="s.whatsapp">· WA {{ s.whatsapp }}</span></p>
            <p v-if="s.description" class="text-sm text-brand-700">{{ s.description }}</p>
            <p class="text-xs" :class="s.active ? 'text-emerald-700' : 'text-coral'">
              {{ s.active ? 'Activo' : 'Inactivo' }}
            </p>
          </div>
          <div class="flex gap-2">
            <button class="btn-secondary" @click="toggleService(s)">
              {{ s.active ? 'Desactivar' : 'Activar' }}
            </button>
            <button class="btn-danger" @click="removeService(s.id)">Eliminar</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
