<script setup lang="ts">
import { CircleAlert } from 'lucide-vue-next'
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { z } from 'zod'

import AppButton from '@/components/common/AppButton.vue'
import FormField from '@/components/common/FormField.vue'
import { errorMessage } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const form = reactive({ identifier: '', password: '' })
const errors = reactive<Record<string, string>>({})
const formError = ref('')

const schema = z.object({
  identifier: z.string().trim().min(1, 'Enter your email or username'),
  password: z.string().min(1, 'Enter your password'),
})

const inputClasses =
  'w-full rounded-lg border border-edge bg-surface-muted px-3 py-2 text-sm text-ink placeholder:text-ink-muted focus:border-accent/50 focus:outline-none aria-[invalid=true]:border-rose-500/60'

async function submit(): Promise<void> {
  formError.value = ''
  for (const key of Object.keys(errors)) delete errors[key]

  const parsed = schema.safeParse(form)
  if (!parsed.success) {
    for (const issue of parsed.error.issues) {
      const field = String(issue.path[0])
      if (!errors[field]) errors[field] = issue.message
    }
    return
  }

  try {
    await auth.login(parsed.data)
    const redirect = route.query.redirect
    await router.push(typeof redirect === 'string' ? redirect : { name: 'home' })
  } catch (err) {
    formError.value = errorMessage(err, 'Unable to log in. Please try again.')
  }
}
</script>

<template>
  <div class="mx-auto max-w-md py-6">
    <h1 class="text-2xl font-semibold tracking-tight text-ink">Welcome back</h1>
    <p class="mt-1.5 text-sm text-ink-muted">Log in to write and like articles.</p>

    <form class="card mt-6 space-y-5 p-6" novalidate @submit.prevent="submit">
      <p
        v-if="formError"
        role="alert"
        class="flex items-start gap-2 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-300"
      >
        <CircleAlert class="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        {{ formError }}
      </p>

      <FormField label="Email or Username" input-id="identifier" :error="errors.identifier">
        <template #default="{ describedBy, invalid }">
          <input
            id="identifier"
            v-model="form.identifier"
            type="text"
            autocomplete="username"
            :aria-invalid="invalid"
            :aria-describedby="describedBy"
            :class="inputClasses"
            placeholder="you@example.com"
          />
        </template>
      </FormField>

      <FormField label="Password" input-id="password" :error="errors.password">
        <template #default="{ describedBy, invalid }">
          <input
            id="password"
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            :aria-invalid="invalid"
            :aria-describedby="describedBy"
            :class="inputClasses"
            placeholder="••••••••"
          />
        </template>
      </FormField>

      <AppButton type="submit" block :loading="auth.loading">Log in</AppButton>
    </form>

    <p class="mt-5 text-center text-sm text-ink-muted">
      Don't have an account?
      <RouterLink :to="{ name: 'register' }" class="font-medium text-accent hover:text-accent-hover">
        Create one
      </RouterLink>
    </p>
  </div>
</template>
