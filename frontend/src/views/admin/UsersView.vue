<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import api from '../../api/client'
import type { Unit, User } from '../../types'

const users = ref<User[]>([])
const units = ref<Unit[]>([])
const message = ref('')
const selectedUnit = ref<number | null>(null)
const form = reactive({
  email: '',
  name: '',
  phone: '',
  password: 'vecino123',
  role: 'resident',
  relation: 'owner',
})

async function load() {
  const [u, un] = await Promise.all([api.get<User[]>('/users'), api.get<Unit[]>('/units')])
  users.value = u.data
  units.value = un.data
}

async function createUser() {
  message.value = ''
  try {
    await api.post('/users', {
      ...form,
      unit_ids: form.role === 'resident' && selectedUnit.value ? [selectedUnit.value] : [],
    })
    message.value = 'Usuario creado'
    form.email = ''
    form.name = ''
    form.phone = ''
    selectedUnit.value = null
    await load()
  } catch (e: any) {
    message.value = e?.response?.data?.detail || 'Error'
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="page-title">Usuarios</h1>
      <p class="text-sm text-brand-700">Admin, vecinos y personal.</p>
    </div>

    <form class="card grid gap-3 md:grid-cols-2" @submit.prevent="createUser">
      <div>
        <label class="label">Nombre</label>
        <input v-model="form.name" class="input" required />
      </div>
      <div>
        <label class="label">Email</label>
        <input v-model="form.email" type="email" class="input" required />
      </div>
      <div>
        <label class="label">Teléfono</label>
        <input v-model="form.phone" class="input" />
      </div>
      <div>
        <label class="label">Contraseña</label>
        <input v-model="form.password" class="input" required />
      </div>
      <div>
        <label class="label">Rol</label>
        <select v-model="form.role" class="input">
          <option value="admin">Admin</option>
          <option value="resident">Vecino</option>
          <option value="staff">Personal</option>
        </select>
      </div>
      <div v-if="form.role === 'resident'">
        <label class="label">Vivienda</label>
        <select v-model="selectedUnit" class="input">
          <option :value="null">Seleccionar…</option>
          <option v-for="u in units" :key="u.id" :value="u.id">{{ u.code }}</option>
        </select>
      </div>
      <div class="md:col-span-2">
        <button class="btn-primary">Crear usuario</button>
      </div>
    </form>
    <p v-if="message" class="text-sm">{{ message }}</p>

    <div class="card space-y-3">
      <div v-for="user in users" :key="user.id" class="flex flex-wrap items-center justify-between gap-2 border-b border-brand-50 pb-3 last:border-0">
        <div>
          <p class="font-semibold">{{ user.name }}</p>
          <p class="text-xs text-brand-700">{{ user.email }} · {{ user.role }}</p>
        </div>
        <div class="text-xs text-brand-700">
          <span v-for="u in user.units" :key="u.id" class="mr-2 rounded-full bg-brand-50 px-2 py-1">{{ u.code }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
