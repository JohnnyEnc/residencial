<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="space-y-4">
    <h1 class="page-title">Perfil</h1>
    <div class="card space-y-2">
      <p class="font-semibold">{{ auth.user?.name }}</p>
      <p class="text-sm text-brand-700">{{ auth.user?.email }}</p>
      <p class="text-sm text-brand-700">Rol: {{ auth.user?.role }}</p>
      <p v-if="auth.user?.units?.length" class="text-sm text-brand-700">
        Viviendas:
        <span v-for="u in auth.user.units" :key="u.id">{{ u.code }} </span>
      </p>
    </div>
    <button class="btn-danger w-full" @click="logout">Cerrar sesión</button>
  </div>
</template>
