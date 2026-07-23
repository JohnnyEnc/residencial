<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const email = ref('admin@example.com')
const password = ref('admin123')
const error = ref('')
const auth = useAuthStore()
const router = useRouter()

async function onSubmit() {
  error.value = ''
  try {
    await auth.login(email.value, password.value)
    await router.replace(auth.homePath())
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    if (Array.isArray(detail)) {
      error.value = detail.map((x: any) => x.msg || JSON.stringify(x)).join(' · ')
    } else if (typeof detail === 'string') {
      error.value = detail
    } else if (e?.message === 'Network Error') {
      error.value = 'No hay conexión con el servidor. Si acabas de abrir la app en Render, espera ~30s y reintenta.'
    } else {
      error.value = 'No se pudo iniciar sesión'
    }
  }
}
</script>

<template>
  <div class="mx-auto flex min-h-screen max-w-md flex-col justify-center px-5 py-10">
    <div class="mb-8">
      <p class="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">Residencial</p>
      <h1 class="mt-2 font-display text-4xl leading-tight text-ink">Gestión del condominio</h1>
      <p class="mt-3 text-brand-800/80">Administración, vecinos y personal en un solo lugar.</p>
    </div>

    <form class="card space-y-4" @submit.prevent="onSubmit">
      <div>
        <label class="label">Correo</label>
        <input v-model="email" type="email" class="input" required />
      </div>
      <div>
        <label class="label">Contraseña</label>
        <input v-model="password" type="password" class="input" required />
      </div>
      <p v-if="error" class="text-sm text-coral">{{ error }}</p>
      <button class="btn-primary w-full" :disabled="auth.loading">
        {{ auth.loading ? 'Entrando…' : 'Entrar' }}
      </button>
    </form>

    <div class="mt-6 space-y-2 text-sm text-brand-800/80">
      <p class="font-semibold text-brand-900">Cuentas demo</p>
      <p>Admin: admin@example.com / admin123</p>
      <p>Vecino: ana@example.com / vecino123</p>
      <p>Staff: staff@example.com / staff123</p>
    </div>
  </div>
</template>
