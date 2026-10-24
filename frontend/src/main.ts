import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from '@/App.vue'
import router from '@/router'
import { setUnauthorizedHandler } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

import '@/assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// A rejected token anywhere in the app ends the session and returns to login.
const auth = useAuthStore()
setUnauthorizedHandler(() => {
  auth.logout()
  if (router.currentRoute.value.meta.requiresAuth) {
    router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
  }
})

app.mount('#app')
