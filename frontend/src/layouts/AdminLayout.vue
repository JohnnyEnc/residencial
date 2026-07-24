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
  { to: '/admin/directory', label: 'Directorio' },
  { to: '/admin/payments', label: 'Cuotas' },
  { to: '/admin/reports', label: 'Reportes' },
  { to: '/admin/announcements', label: 'Avisos' },
]

const active = computed(() => route.path)

function isActive(link: { to: string; exact?: boolean }) {
  return link.exact ? active.value === link.to : active.value.startsWith(link.to)
}
</script>

<template>
  <div class="mx-auto flex min-h-screen max-w-[1400px] flex-col md:flex-row">
    <aside
      class="relative overflow-hidden border-b border-white/10 bg-dusk text-white md:flex md:min-h-screen md:w-[17.5rem] md:flex-col md:border-b-0"
    >
      <div
        class="pointer-events-none absolute -right-10 top-0 h-40 w-40 rounded-full bg-lime/20 blur-2xl"
      />
      <div class="relative flex items-center justify-between px-5 py-5">
        <div>
          <p class="font-display text-2xl font-extrabold tracking-tight">Residencial</p>
          <p class="mt-0.5 text-[11px] uppercase tracking-[0.2em] text-lime/80">Junta de vecinos</p>
        </div>
        <button
          class="text-xs font-semibold uppercase tracking-wider text-lagoon-100 underline decoration-lime/50 md:hidden"
          @click="auth.logout(); $router.push('/login')"
        >
          Salir
        </button>
      </div>

      <nav class="relative flex gap-1 overflow-x-auto px-3 pb-4 md:flex-1 md:flex-col md:gap-1 md:overflow-visible md:px-3 md:pb-6">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="whitespace-nowrap rounded-2xl px-3 py-2.5 text-sm font-semibold tracking-tight transition"
          :class="
            isActive(link)
              ? 'bg-lime text-ink shadow-lift'
              : 'text-lagoon-100 hover:bg-white/10'
          "
        >
          {{ link.label }}
        </RouterLink>
      </nav>

      <div class="relative mt-auto hidden border-t border-white/10 px-5 py-5 md:block">
        <p class="font-display text-sm font-bold">{{ auth.user?.name }}</p>
        <p class="truncate text-xs text-lagoon-200">{{ auth.user?.email }}</p>
        <button
          class="mt-3 text-xs font-semibold uppercase tracking-[0.14em] text-lime"
          @click="auth.logout(); $router.push('/login')"
        >
          Cerrar sesión
        </button>
      </div>
    </aside>

    <main class="flex-1 px-4 py-6 md:px-8 md:py-9">
      <RouterView />
    </main>
  </div>
</template>
