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
  <div class="relative min-h-screen overflow-hidden">
    <!-- Atmospheric plane -->
    <div class="pointer-events-none absolute inset-0">
      <div
        class="absolute -left-1/4 top-[-20%] h-[70vh] w-[80vw] animate-drift rounded-full opacity-80 blur-3xl"
        style="background: radial-gradient(circle, rgba(198, 240, 77, 0.35), transparent 65%)"
      />
      <div
        class="absolute bottom-[-10%] right-[-15%] h-[55vh] w-[70vw] animate-drift rounded-full opacity-70 blur-3xl"
        style="background: radial-gradient(circle, rgba(26, 108, 89, 0.35), transparent 70%); animation-delay: -4s"
      />
      <div
        class="absolute inset-0 opacity-[0.07]"
        style="
          background-image: linear-gradient(rgba(12, 31, 27, 0.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(12, 31, 27, 0.08) 1px, transparent 1px);
          background-size: 48px 48px;
        "
      />
    </div>

    <div class="relative mx-auto grid min-h-screen max-w-6xl lg:grid-cols-[1.15fr_0.95fr]">
      <!-- Brand hero -->
      <section class="flex flex-col justify-end px-6 pb-10 pt-14 md:px-10 lg:justify-center lg:pb-16 lg:pt-16">
        <p class="eyebrow reveal text-lagoon-700">Residencial</p>
        <h1 class="reveal-2 mt-4 font-display text-[clamp(3rem,9vw,5.5rem)] font-extrabold leading-[0.92] tracking-tight text-ink">
          La junta,<br />
          en tu bolsillo.
        </h1>
        <p class="reveal-3 mt-5 max-w-md text-base leading-relaxed text-lagoon-800/85 md:text-lg">
          Pagos, reportes, avisos y directorio del condominio — pensado primero para el móvil.
        </p>
        <div class="reveal-4 mt-8 flex items-center gap-3 text-xs font-semibold uppercase tracking-[0.18em] text-lagoon-700">
          <span class="inline-block h-px w-10 bg-lagoon-500" />
          Junta de vecinos
        </div>
      </section>

      <!-- Auth -->
      <section class="flex items-end px-5 pb-10 md:px-8 lg:items-center lg:pb-0">
        <form class="reveal-3 w-full max-w-md space-y-5 rounded-[1.75rem] bg-dusk p-6 text-white shadow-lift md:p-8" @submit.prevent="onSubmit">
          <div>
            <p class="font-display text-2xl font-bold tracking-tight">Entrar</p>
            <p class="mt-1 text-sm text-lagoon-100/80">Usa tu cuenta del residencial.</p>
          </div>

          <div>
            <label class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-lime/90">Correo</label>
            <input
              v-model="email"
              type="email"
              required
              class="w-full rounded-2xl border-0 bg-white/10 px-3.5 py-3 text-sm text-white outline-none ring-1 ring-white/15 placeholder:text-white/40 focus:bg-white/15 focus:ring-2 focus:ring-lime/60"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.16em] text-lime/90">Contraseña</label>
            <input
              v-model="password"
              type="password"
              required
              class="w-full rounded-2xl border-0 bg-white/10 px-3.5 py-3 text-sm text-white outline-none ring-1 ring-white/15 focus:bg-white/15 focus:ring-2 focus:ring-lime/60"
            />
          </div>

          <p v-if="error" class="text-sm text-lime">{{ error }}</p>

          <button
            type="submit"
            class="btn-lime w-full py-3 text-base"
            :disabled="auth.loading"
          >
            {{ auth.loading ? 'Entrando…' : 'Continuar' }}
          </button>

          <div class="space-y-1 border-t border-white/10 pt-4 text-[12px] leading-relaxed text-lagoon-100/75">
            <p class="font-display text-xs font-semibold uppercase tracking-[0.14em] text-lime/80">Demo</p>
            <p>admin@example.com · admin123</p>
            <p>ana@example.com · vecino123</p>
            <p>staff@example.com · staff123</p>
          </div>
        </form>
      </section>
    </div>
  </div>
</template>
