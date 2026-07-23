<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()

const nav = computed(() => {
  if (auth.role === 'staff') {
    return [
      { to: '/staff', label: 'Reportes', icon: '🔧' },
      { to: '/staff/profile', label: 'Perfil', icon: '👤' },
    ]
  }
  return [
    { to: '/app', label: 'Inicio', icon: '🏠' },
    { to: '/app/payments', label: 'Pagos', icon: '💳' },
    { to: '/app/reports', label: 'Reportes', icon: '📝' },
    { to: '/app/profile', label: 'Perfil', icon: '👤' },
  ]
})
</script>

<template>
  <div class="mx-auto flex min-h-screen max-w-lg flex-col pb-24">
    <header class="sticky top-0 z-10 border-b border-brand-100 bg-sand/90 px-4 py-3 backdrop-blur">
      <div class="flex items-center justify-between">
        <div>
          <p class="font-display text-lg">Residencial</p>
          <p class="text-xs text-brand-700">{{ auth.user?.name }}</p>
        </div>
        <span class="rounded-full bg-brand-100 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide text-brand-800">
          {{ auth.role }}
        </span>
      </div>
    </header>
    <main class="flex-1 px-4 py-4">
      <RouterView />
    </main>
    <nav class="fixed inset-x-0 bottom-0 z-10 border-t border-brand-100 bg-white/95 backdrop-blur">
      <div class="mx-auto flex max-w-lg justify-around px-2 py-2">
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="flex min-w-[64px] flex-col items-center rounded-xl px-2 py-1 text-[11px] font-semibold text-brand-600"
          :class="{ 'bg-brand-50 text-brand-800': route.path === item.to || (item.to !== '/app' && item.to !== '/staff' && route.path.startsWith(item.to)) }"
        >
          <span class="text-base">{{ item.icon }}</span>
          {{ item.label }}
        </RouterLink>
      </div>
    </nav>
  </div>
</template>
