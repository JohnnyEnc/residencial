<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()

const links = [
  { to: '/admin', label: 'Dashboard', exact: true },
  { to: '/admin/units', label: 'Viviendas' },
  { to: '/admin/users', label: 'Usuarios' },
  { to: '/admin/payments', label: 'Cuotas' },
  { to: '/admin/reports', label: 'Reportes' },
  { to: '/admin/announcements', label: 'Avisos' },
]

const active = computed(() => route.path)
</script>

<template>
  <div class="mx-auto flex min-h-screen max-w-7xl flex-col md:flex-row">
    <aside class="border-b border-brand-200/70 bg-brand-800 text-white md:w-64 md:border-b-0 md:border-r md:border-brand-700">
      <div class="flex items-center justify-between px-5 py-4">
        <div>
          <p class="font-display text-xl tracking-tight">Residencial</p>
          <p class="text-xs text-brand-200">Junta de vecinos</p>
        </div>
        <button class="text-sm text-brand-200 underline md:hidden" @click="auth.logout(); $router.push('/login')">Salir</button>
      </div>
      <nav class="flex gap-1 overflow-x-auto px-3 pb-3 md:flex-col md:overflow-visible md:px-3 md:pb-6">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="whitespace-nowrap rounded-xl px-3 py-2 text-sm font-semibold text-brand-100 hover:bg-brand-700"
          :class="{
            'bg-brand-600 text-white': link.exact ? active === link.to : active.startsWith(link.to),
          }"
        >
          {{ link.label }}
        </RouterLink>
      </nav>
      <div class="mt-auto hidden border-t border-brand-700 px-5 py-4 md:block">
        <p class="text-sm font-semibold">{{ auth.user?.name }}</p>
        <p class="text-xs text-brand-200">{{ auth.user?.email }}</p>
        <button class="mt-3 text-sm text-brand-100 underline" @click="auth.logout(); $router.push('/login')">
          Cerrar sesión
        </button>
      </div>
    </aside>
    <main class="flex-1 px-4 py-5 md:px-8 md:py-8">
      <RouterView />
    </main>
  </div>
</template>
