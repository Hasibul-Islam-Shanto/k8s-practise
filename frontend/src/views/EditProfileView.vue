<script setup lang="ts">
import { CircleAlert } from 'lucide-vue-next'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { z } from 'zod'

import AppButton from '@/components/common/AppButton.vue'
import FormField from '@/components/common/FormField.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { errorMessage, fieldErrors } from '@/services/api'
import { userService } from '@/services/user.service'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({
  full_name: auth.user?.full_name ?? '',
  bio: auth.user?.bio ?? '',
  avatar_url: auth.user?.avatar_url ?? '',
})
const errors = reactive<Record<string, string>>({})
const formError = ref('')
const saving = ref(false)

const schema = z.object({
  full_name: z.string().trim().min(2, 'Enter your full name').max(120, 'That name is too long'),
  bio: z.string().trim().max(500, 'Keep your bio under 500 characters'),
  avatar_url: z.union([z.literal(''), z.string().trim().url('Enter a valid image URL')]),
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

  saving.value = true
  try {
    const updated = await userService.updateOwnProfile({
      full_name: parsed.data.full_name,
      bio: parsed.data.bio || null,
      avatar_url: parsed.data.avatar_url || null,
    })
    auth.setUser(updated)
    await router.push({ name: 'profile' })
  } catch (err) {
    const serverErrors = fieldErrors(err)
    for (const [field, message] of Object.entries(serverErrors)) errors[field] = message
    if (Object.keys(serverErrors).length === 0) {
      formError.value = errorMessage(err, 'Unable to save your profile. Please try again.')
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-lg">
    <header class="mb-6">
      <h1 class="text-2xl font-semibold tracking-tight text-ink">Edit profile</h1>
      <p class="mt-1.5 text-sm text-ink-muted">
        Your username and email address cannot be changed.
      </p>
    </header>

    <form class="card space-y-6 p-6" novalidate @submit.prevent="submit">
      <p
        v-if="formError"
        role="alert"
        class="flex items-start gap-2 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-300"
      >
        <CircleAlert class="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        {{ formError }}
      </p>

      <div class="flex items-center gap-4">
        <UserAvatar
          :full-name="form.full_name || auth.user!.full_name"
          :username="auth.user!.username"
          :avatar-url="form.avatar_url || null"
          size="lg"
        />
        <p class="text-sm text-ink-muted">
          Preview. Leaving the avatar URL empty shows your initials instead.
        </p>
      </div>

      <FormField label="Full name" input-id="full_name" :error="errors.full_name">
        <template #default="{ describedBy, invalid }">
          <input
            id="full_name"
            v-model="form.full_name"
            type="text"
            autocomplete="name"
            :aria-invalid="invalid"
            :aria-describedby="describedBy"
            :class="inputClasses"
          />
        </template>
      </FormField>

      <FormField
        label="Bio"
        input-id="bio"
        :error="errors.bio"
        :hint="`${form.bio.trim().length}/500`"
        optional
      >
        <template #default="{ describedBy, invalid }">
          <textarea
            id="bio"
            v-model="form.bio"
            rows="4"
            :aria-invalid="invalid"
            :aria-describedby="describedBy"
            :class="[inputClasses, 'resize-y']"
            placeholder="What do you work on?"
          />
        </template>
      </FormField>

      <FormField label="Avatar URL" input-id="avatar_url" :error="errors.avatar_url" optional>
        <template #default="{ describedBy, invalid }">
          <input
            id="avatar_url"
            v-model="form.avatar_url"
            type="url"
            :aria-invalid="invalid"
            :aria-describedby="describedBy"
            :class="inputClasses"
            placeholder="https://example.com/avatar.png"
          />
        </template>
      </FormField>

      <div class="flex flex-col-reverse gap-3 border-t border-edge pt-5 sm:flex-row sm:justify-end">
        <AppButton variant="secondary" :disabled="saving" @click="router.push({ name: 'profile' })">
          Cancel
        </AppButton>
        <AppButton type="submit" :loading="saving">Save changes</AppButton>
      </div>
    </form>
  </div>
</template>
