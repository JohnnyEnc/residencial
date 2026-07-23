<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/client'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const message = ref('')
const form = reactive({
  phone: auth.user?.phone || '',
  phone_secondary: auth.user?.phone_secondary || '',
  whatsapp: auth.user?.whatsapp || '',
  show_in_directory: auth.user?.show_in_directory ?? true,
})

onMounted(() => {
  form.phone = auth.user?.phone || ''
  form.phone_secondary = auth.user?.phone_secondary || ''
  form.whatsapp = auth.user?.whatsapp || ''
  form.show_in_directory = auth.user?.show_in_directory ?? true
})

async function save() {
  message.value = ''
  try {
    const { data } = await api.patch('/contacts/me', {
      phone: form.phone || null,
      phone_secondary: form.phone_secondary || null,
      whatsapp: form.whatsapp || null,
      show_in_directory: form.show_in_directory,
    })
    auth.user = data
    message.value = 'Contacto actualizado'
  } catch (e: any) {
    message.value = e?.response?.data?.detail || 'No se pudo guardar'
  }
}

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

    <form v-if="auth.role === 'resident' || auth.role === 'staff'" class="card space-y-3" @submit.prevent="save">
      <h2 class="font-semibold">Mis números de contacto</h2>
      <div>
        <label class="label">Teléfono</label>
        <input v-model="form.phone" class="input" placeholder="809-000-0000" />
      </div>
      <div>
        <label class="label">Teléfono secundario</label>
        <input v-model="form.phone_secondary" class="input" />
      </div>
      <div>
        <label class="label">WhatsApp</label>
        <input v-model="form.whatsapp" class="input" />
      </div>
      <label v-if="auth.role === 'resident'" class="flex items-center gap-2 text-sm">
        <input v-model="form.show_in_directory" type="checkbox" />
        Mostrar mis datos en el directorio de vecinos
      </label>
      <p v-if="message" class="text-sm text-brand-700">{{ message }}</p>
      <button class="btn-primary w-full">Guardar contactos</button>
    </form>

    <button class="btn-danger w-full" @click="logout">Cerrar sesión</button>
  </div>
</template>
