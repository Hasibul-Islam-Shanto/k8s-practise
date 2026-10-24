<script setup lang="ts">
defineProps<{
  label: string
  inputId: string
  error?: string
  hint?: string
  optional?: boolean
}>()
</script>

<template>
  <div>
    <div class="mb-1.5 flex items-baseline justify-between gap-2">
      <label :for="inputId" class="text-sm font-medium text-ink">
        {{ label }}
        <span v-if="optional" class="ml-1 text-xs font-normal text-ink-muted">(optional)</span>
      </label>
      <span v-if="hint" class="text-xs text-ink-muted">{{ hint }}</span>
    </div>

    <slot :described-by="error ? `${inputId}-error` : undefined" :invalid="Boolean(error)" />

    <p v-if="error" :id="`${inputId}-error`" class="mt-1.5 text-sm text-rose-400">
      {{ error }}
    </p>
  </div>
</template>
