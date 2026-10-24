<script setup lang="ts">
import { LoaderCircle } from 'lucide-vue-next'
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
    size?: 'sm' | 'md'
    loading?: boolean
    disabled?: boolean
    type?: 'button' | 'submit'
    block?: boolean
  }>(),
  { variant: 'primary', size: 'md', loading: false, disabled: false, type: 'button', block: false },
)

const VARIANTS = {
  primary: 'gradient-accent hover:opacity-90',
  secondary: 'border border-edge bg-surface text-ink hover:border-accent/40 hover:bg-surface-muted',
  ghost: 'text-ink-muted hover:bg-surface hover:text-ink',
  danger: 'bg-rose-600 text-white hover:bg-rose-500',
} as const

const SIZES = { sm: 'px-3 py-1.5 text-sm', md: 'px-4 py-2 text-sm' } as const

const isInactive = computed(() => props.disabled || props.loading)
</script>

<template>
  <button
    :type="type"
    :disabled="isInactive"
    :aria-busy="loading"
    :class="[VARIANTS[variant], SIZES[size], block && 'w-full']"
    class="inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50"
  >
    <LoaderCircle v-if="loading" class="h-4 w-4 animate-spin" aria-hidden="true" />
    <slot />
  </button>
</template>
