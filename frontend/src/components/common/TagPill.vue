<script setup lang="ts">
withDefaults(defineProps<{ name: string; to?: string | null }>(), { to: null })
</script>

<template>
  <RouterLink
    v-if="to"
    :to="to"
    class="inline-flex items-center rounded-md border border-edge bg-surface-muted px-2 py-0.5 text-xs font-medium text-ink-muted transition-colors hover:border-emerald-400/50 hover:text-white"
  >
    {{ name }}
  </RouterLink>
  <span
    v-else
    class="inline-flex items-center rounded-md border border-edge bg-surface-muted px-2 py-0.5 text-xs font-medium text-ink-muted"
  >
    {{ name }}
  </span>
</template>
