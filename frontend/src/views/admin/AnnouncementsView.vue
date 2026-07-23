<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import api from '../../api/client'
import type { Announcement } from '../../types'

const items = ref<Announcement[]>([])
const form = reactive({ title: '', body: '', priority: 'normal' })
const message = ref('')

async function load() {
  const { data } = await api.get<Announcement[]>('/announcements')
  items.value = data
}

async function create() {
  await api.post('/announcements', form)
  form.title = ''
  form.body = ''
  message.value = 'Aviso publicado'
  await load()
}

async function remove(id: number) {
  await api.delete(`/announcements/${id}`)
  await load()
}

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="page-title">Avisos</h1>
      <p class="text-sm text-brand-700">Comunicados para vecinos y personal.</p>
    </div>

    <form class="card space-y-3" @submit.prevent="create">
      <div>
        <label class="label">Título</label>
        <input v-model="form.title" class="input" required />
      </div>
      <div>
        <label class="label">Mensaje</label>
        <textarea v-model="form.body" class="input min-h-[100px]" required />
      </div>
      <div>
        <label class="label">Prioridad</label>
        <select v-model="form.priority" class="input max-w-xs">
          <option value="low">Baja</option>
          <option value="normal">Normal</option>
          <option value="high">Alta</option>
        </select>
      </div>
      <button class="btn-primary">Publicar</button>
    </form>
    <p v-if="message" class="text-sm">{{ message }}</p>

    <div class="space-y-3">
      <div v-for="a in items" :key="a.id" class="card">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="font-semibold">{{ a.title }}</p>
            <p class="mt-1 text-sm text-brand-800">{{ a.body }}</p>
            <p class="mt-2 text-xs uppercase text-brand-600">{{ a.priority }}</p>
          </div>
          <button class="btn-secondary" @click="remove(a.id)">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>
