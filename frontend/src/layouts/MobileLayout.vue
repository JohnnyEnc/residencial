<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()

const nav = computed(() => {
  if (auth.role === 'staff') {
    return [
      { to: '/staff', label: 'Reportes', icon: 'grid' },
      { to: '/staff/profile', label: 'Perfil', icon: 'user' },
    ]
  }
  return [
    { to: '/app', label: 'Inicio', icon: 'home' },
    { to: '/app/directory', label: 'Directorio', icon: 'book' },
    { to: '/app/payments', label: 'Pagos', icon: 'card' },
    { to: '/app/reports', label: 'Reportes', icon: 'note' },
    { to: '/app/profile', label: 'Perfil', icon: 'user' },
  ]
})

function isActive(to: string) {
  if (to === '/app' || to === '/staff') return route.path === to
  return route.path === to || route.path.startsWith(to + '/')
}

const roleLabel: Record<string, string> = {
  admin: 'Admin',
  resident: 'Vecino',
  staff: 'Personal',
}
</script>

<template>
  <div class="mx-auto flex min-h-screen max-w-lg flex-col pb-28">
    <header class="sticky top-0 z-10 border-b border-lagoon-900/5 bg-paper/85 px-4 py-3.5 backdrop-blur-xl">
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="font-display text-xl font-extrabold tracking-tight text-ink">Residencial</p>
          <p class="text-xs text-lagoon-700">{{ auth.user?.name }}</p>
        </div>
        <span
          class="rounded-full bg-lagoon-900 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.16em] text-lime"
        >
          {{ roleLabel[auth.role || ''] || auth.role }}
        </span>
      </div>
    </header>

    <main class="flex-1 px-4 py-5">
      <RouterView />
    </main>

    <nav class="fixed inset-x-0 bottom-0 z-10 px-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
      <div
        class="mx-auto flex max-w-lg justify-around rounded-[1.6rem] bg-dusk/95 px-1 py-2 text-white shadow-lift backdrop-blur-xl"
      >
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="flex min-w-[58px] flex-col items-center gap-0.5 rounded-2xl px-2 py-1.5 text-[10px] font-semibold tracking-wide transition"
          :class="isActive(item.to) ? 'bg-lime text-ink' : 'text-lagoon-100/80'"
        >
          <svg v-if="item.icon === 'home'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 10.5 12 3l9 7.5V21a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1v-10.5Z" />
          </svg>
          <svg v-else-if="item.icon === 'book'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5V5.5Z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 18.5A2.5 2.5 0 0 1 6.5 16H20" />
          </svg>
          <svg v-else-if="item.icon === 'card'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <rect x="3" y="6" width="18" height="12" rx="2" />
            <path stroke-linecap="round" d="M3 10h18" />
          </svg>
          <svg v-else-if="item.icon === 'note'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 4h7l4 4v11a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Z" />
            <path stroke-linecap="round" d="M15 4v4h4M9 12h6M9 16h4" />
          </svg>
          <svg v-else-if="item.icon === 'grid'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h10M4 18h14" />
          </svg>
          <svg v-else class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <circle cx="12" cy="8" r="3.5" />
            <path stroke-linecap="round" d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" />
          </svg>
          {{ item.label }}
        </RouterLink>
      </div>
    </nav>
  </div>
</template>
