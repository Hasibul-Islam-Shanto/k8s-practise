<script setup lang="ts">
import { computed, ref } from 'vue'

import { avatarColor, initials } from '@/utils/format'

const props = withDefaults(
  defineProps<{
    fullName: string
    username: string
    avatarUrl?: string | null
    size?: 'sm' | 'md' | 'lg' | 'xl'
  }>(),
  { avatarUrl: null, size: 'md' },
)

const SIZES = {
  sm: 'h-8 w-8 text-[0.65rem]',
  md: 'h-10 w-10 text-xs',
  lg: 'h-14 w-14 text-base',
  xl: 'h-24 w-24 text-2xl',
} as const

const imageFailed = ref(false)
const showImage = computed(() => Boolean(props.avatarUrl) && !imageFailed.value)
const fallbackClasses = computed(() => avatarColor(props.username))
</script>

<template>
  <img
    v-if="showImage"
    :src="avatarUrl!"
    :alt="`${fullName}'s avatar`"
    :class="SIZES[size]"
    class="shrink-0 rounded-full border border-edge object-cover"
    loading="lazy"
    @error="imageFailed = true"
  />
  <span
    v-else
    :class="[SIZES[size], fallbackClasses]"
    class="flex shrink-0 items-center justify-center rounded-full border border-edge font-semibold select-none"
    aria-hidden="true"
  >
    {{ initials(fullName) }}
  </span>
</template>
