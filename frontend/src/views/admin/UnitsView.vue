<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import api from '../../api/client'
import type { Unit } from '../../types'

const units = ref<Unit[]>([])
const loading = ref(true)
const form = reactive({ code: '', block: '', number: '', floor: '' })
const message = ref('')

async function load() {
  loading.value = true
  const { data } = await api.get<Unit[]>('/units')
  units.value = data
  loading.value = false
}

async function createUnit() {
  message.value = ''
  try {
    await api.post('/units', form)
    form.code = ''
    form.block = ''
    form.number = ''
    form.floor = ''
    message.value = 'Vivienda creada'
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
      <h1 class="page-title">Viviendas</h1>
      <p class="text-sm text-brand-700">Catálogo de unidades del residencial.</p>
    </div>

    <form class="card grid gap-3 md:grid-cols-5" @submit.prevent="createUnit">
      <div>
        <label class="label">Código</label>
        <input v-model="form.code" class="input" placeholder="A-103" required />
      </div>
      <div>
        <label class="label">Bloque</label>
        <input v-model="form.block" class="input" placeholder="A" />
      </div>
      <div>
        <label class="label">Número</label>
        <input v-model="form.number" class="input" placeholder="103" required />
      </div>
      <div>
        <label class="label">Piso</label>
        <input v-model="form.floor" class="input" placeholder="1" />
      </div>
      <div class="flex items-end">
        <button class="btn-primary w-full">Agregar</button>
      </div>
    </form>
    <p v-if="message" class="text-sm text-brand-700">{{ message }}</p>

    <div class="card overflow-x-auto">
      <table class="w-full min-w-[560px] text-left text-sm">
        <thead class="text-xs uppercase text-brand-600">
          <tr>
            <th class="pb-2">Código</th>
            <th class="pb-2">Bloque</th>
            <th class="pb-2">Número</th>
            <th class="pb-2">Piso</th>
            <th class="pb-2">Residentes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in units" :key="u.id" class="border-t border-brand-50">
            <td class="py-3 font-semibold">{{ u.code }}</td>
            <td>{{ u.block }}</td>
            <td>{{ u.number }}</td>
            <td>{{ u.floor }}</td>
            <td>
              <span v-for="m in u.members" :key="m.id" class="mr-2 inline-block text-xs">
                {{ m.user_name }} ({{ m.relation }})
              </span>
              <span v-if="!u.members.length" class="text-brand-500">—</span>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="loading" class="py-4 text-sm text-brand-600">Cargando…</p>
    </div>
  </div>
</template>
