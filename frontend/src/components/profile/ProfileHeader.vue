<script setup lang="ts">
import { Calendar, Settings } from 'lucide-vue-next'

import AppButton from '@/components/common/AppButton.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import type { UserProfile } from '@/types/user'
import { formatMonthYear } from '@/utils/format'

defineProps<{ profile: UserProfile; isOwnProfile: boolean }>()
const emit = defineEmits<{ edit: [] }>()
</script>

<template>
  <header class="flex flex-col items-center text-center">
    <UserAvatar
      :full-name="profile.full_name"
      :username="profile.username"
      :avatar-url="profile.avatar_url"
      size="xl"
    />

    <h1 class="mt-4 text-2xl font-semibold tracking-tight text-ink">{{ profile.full_name }}</h1>
    <p class="text-ink-muted">@{{ profile.username }}</p>

    <p v-if="profile.bio" class="mt-4 max-w-xl text-[0.9375rem] leading-relaxed text-ink-muted">
      {{ profile.bio }}
    </p>

    <p class="mt-4 inline-flex items-center gap-1.5 text-xs text-ink-muted">
      <Calendar class="h-3.5 w-3.5" aria-hidden="true" />
      Joined {{ formatMonthYear(profile.created_at) }}
    </p>

    <dl class="mt-6 flex items-center gap-8">
      <div class="text-center">
        <dt class="text-xs tracking-wide text-ink-muted uppercase">Posts</dt>
        <dd class="mt-0.5 text-xl font-semibold text-ink">{{ profile.post_count }}</dd>
      </div>
      <div class="text-center">
        <dt class="text-xs tracking-wide text-ink-muted uppercase">Likes</dt>
        <dd class="mt-0.5 text-xl font-semibold text-ink">{{ profile.total_likes_received }}</dd>
      </div>
    </dl>

    <AppButton v-if="isOwnProfile" variant="secondary" size="sm" class="mt-6" @click="emit('edit')">
      <Settings class="h-3.5 w-3.5" aria-hidden="true" />
      Edit Profile
    </AppButton>
  </header>
</template>
