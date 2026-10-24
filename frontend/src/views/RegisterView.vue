<script setup lang="ts">
import { CircleAlert } from 'lucide-vue-next'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { z } from 'zod'

import AppButton from '@/components/common/AppButton.vue'
import FormField from '@/components/common/FormField.vue'
import { errorMessage, fieldErrors } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({
  full_name: '',
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  bio: '',
})
const errors = reactive<Record<string, string>>({})
const formError = ref('')

const schema = z
  .object({
    full_name: z.string().trim().min(2, 'Enter your full name').max(120, 'That name is too long'),
    username: z
      .string()
      .trim()
      .min(3, 'Usernames must be at least 3 characters')
      .max(50, 'That username is too long')
      .regex(/^[a-zA-Z0-9_]+$/, 'Use only letters, numbers and underscores'),
    email: z.string().trim().email('Enter a valid email address'),
    // 72 bytes is bcrypt's limit, which the API enforces too.
    password: z
      .string()
      .min(8, 'Passwords must be at least 8 characters')
      .max(72, 'Passwords must be 72 characters or fewer'),
    confirm_password: z.string(),
    bio: z.string().trim().max(500, 'Keep your bio under 500 characters'),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
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
    await auth.register({
      ...parsed.data,
      username: parsed.data.username.toLowerCase(),
      bio: parsed.data.bio || null,
    })
    await router.push({ name: 'home' })
  } catch (err) {
    // A duplicate email or username is only detectable server-side.
    const serverErrors = fieldErrors(err)
    for (const [field, message] of Object.entries(serverErrors)) errors[field] = message
    if (Object.keys(serverErrors).length === 0) {
      formError.value = errorMessage(err, 'Unable to create your account. Please try again.')
    }
  }
}
</script>

<template>
  <div class="mx-auto max-w-md py-6">
    <h1 class="text-2xl font-semibold tracking-tight text-ink">Create your account</h1>
    <p class="mt-1.5 text-sm text-ink-muted">Join and start publishing what you know.</p>

    <form class="card mt-6 space-y-5 p-6" novalidate @submit.prevent="submit">
      <p
        v-if="formError"
        role="alert"
        class="flex items-start gap-2 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-300"
      >
        <CircleAlert class="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        {{ formError }}
      </p>

      <FormField label="Full Name" input-id="full_name" :error="errors.full_name">
        <template #default="{ describedBy, invalid }">
          <input
            id="full_name"
            v-model="form.full_name"
            type="text"
            autocomplete="name"
            :aria-invalid="invalid"
            :aria-describedby="describedBy"
            :class="inputClasses"
            placeholder="Ada Lovelace"
          />
        </template>
      </FormField>

      <FormField label="Username" input-id="username" :error="errors.username">
        <template #default="{ describedBy, invalid }">
          <input
            id="username"
            v-model="form.username"
            type="text"
            autocomplete="username"
            :aria-invalid="invalid"
            :aria-describedby="describedBy"
            :class="inputClasses"
            placeholder="adalovelace"
          />
        </template>
      </FormField>

      <FormField label="Email" input-id="email" :error="errors.email">
        <template #default="{ describedBy, invalid }">
          <input
            id="email"
            v-model="form.email"
            type="email"
            autocomplete="email"
            :aria-invalid="invalid"
            :aria-describedby="describedBy"
            :class="inputClasses"
            placeholder="you@example.com"
          />
        </template>
      </FormField>

      <FormField
        label="Password"
        input-id="password"
        :error="errors.password"
        hint="At least 8 characters"
      >
        <template #default="{ describedBy, invalid }">
          <input
            id="password"
            v-model="form.password"
            type="password"
            autocomplete="new-password"
            :aria-invalid="invalid"
            :aria-describedby="describedBy"
            :class="inputClasses"
            placeholder="••••••••"
          />
        </template>
      </FormField>

      <FormField label="Confirm Password" input-id="confirm_password" :error="errors.confirm_password">
        <template #default="{ describedBy, invalid }">
          <input
            id="confirm_password"
            v-model="form.confirm_password"
            type="password"
            autocomplete="new-password"
            :aria-invalid="invalid"
            :aria-describedby="describedBy"
            :class="inputClasses"
            placeholder="••••••••"
          />
        </template>
      </FormField>

      <FormField label="Short bio" input-id="bio" :error="errors.bio" optional>
        <template #default="{ describedBy, invalid }">
          <textarea
            id="bio"
            v-model="form.bio"
            rows="3"
            :aria-invalid="invalid"
            :aria-describedby="describedBy"
            :class="[inputClasses, 'resize-y']"
            placeholder="What do you work on?"
          />
        </template>
      </FormField>

      <AppButton type="submit" block :loading="auth.loading">Create account</AppButton>
    </form>

    <p class="mt-5 text-center text-sm text-ink-muted">
      Already have an account?
      <RouterLink :to="{ name: 'login' }" class="font-medium text-accent hover:text-accent-hover">
        Log in
      </RouterLink>
    </p>
  </div>
</template>
