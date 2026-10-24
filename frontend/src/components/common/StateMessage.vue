<script setup lang="ts">
withDefaults(defineProps<{ title: string; description?: string; tone?: 'neutral' | 'error' }>(), {
  description: '',
  tone: 'neutral',
})
</script>

<template>
  <div
    class="card flex flex-col items-center gap-3 px-6 py-14 text-center"
    :role="tone === 'error' ? 'alert' : undefined"
  >
    <span
      class="flex h-11 w-11 items-center justify-center rounded-full"
      :class="tone === 'error' ? 'bg-rose-500/15 text-rose-400' : 'bg-surface-muted text-ink-muted'"
    >
      <slot name="icon" />
    </span>
    <div class="space-y-1">
      <p class="font-medium text-ink">{{ title }}</p>
      <p v-if="description" class="mx-auto max-w-sm text-sm text-ink-muted">{{ description }}</p>
    </div>
    <slot name="action" />
  </div>
</template>
