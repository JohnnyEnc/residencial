<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/client'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const error = ref('')
const form = reactive({
  category: 'Mantenimiento',
  title: '',
  description: '',
  location: '',
  unit_id: auth.user?.units[0]?.id ?? null as number | null,
})

async function submit() {
  error.value = ''
  try {
    await api.post('/reports/json', form)
    router.push('/app/reports')
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'No se pudo crear el reporte'
  }
}
</script>

<template>
  <div class="space-y-4">
    <h1 class="page-title">Nuevo reporte</h1>
    <form class="card space-y-3" @submit.prevent="submit">
      <div>
        <label class="label">Categoría</label>
        <select v-model="form.category" class="input">
          <option>Mantenimiento</option>
          <option>Seguridad</option>
          <option>Ruido</option>
          <option>Áreas comunes</option>
          <option>Otro</option>
        </select>
      </div>
      <div>
        <label class="label">Título</label>
        <input v-model="form.title" class="input" required />
      </div>
      <div>
        <label class="label">Descripción</label>
        <textarea v-model="form.description" class="input min-h-[120px]" required />
      </div>
      <div>
        <label class="label">Ubicación</label>
        <input v-model="form.location" class="input" placeholder="Lobby, parqueadero…" />
      </div>
      <p v-if="error" class="text-sm text-coral">{{ error }}</p>
      <button class="btn-primary w-full">Enviar reporte</button>
    </form>
  </div>
</template>
