<script setup lang="ts">
import { onKeyStroke } from '@vueuse/core'
import { nextTick, ref, watch } from 'vue'

import AppButton from '@/components/common/AppButton.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    description?: string
    confirmLabel?: string
    cancelLabel?: string
    loading?: boolean
  }>(),
  { description: '', confirmLabel: 'Confirm', cancelLabel: 'Cancel', loading: false },
)

const emit = defineEmits<{ confirm: []; cancel: [] }>()

const dialog = ref<HTMLElement | null>(null)

function cancel(): void {
  if (!props.loading) emit('cancel')
}

onKeyStroke('Escape', () => {
  if (props.open) cancel()
})

// Keep Tab inside the dialog while it is open.
onKeyStroke('Tab', (event) => {
  if (!props.open || !dialog.value) return
  const focusable = dialog.value.querySelectorAll<HTMLElement>('button:not([disabled])')
  if (focusable.length === 0) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
})

watch(
  () => props.open,
  async (open) => {
    if (!open) return
    await nextTick()
    dialog.value?.querySelector<HTMLElement>('button')?.focus()
  },
)
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-150"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
        @click.self="cancel"
      >
        <div
          ref="dialog"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="'confirm-title'"
          :aria-describedby="description ? 'confirm-description' : undefined"
          class="w-full max-w-md rounded-xl border border-edge bg-surface p-6 shadow-lg"
        >
          <h2 id="confirm-title" class="text-lg font-semibold text-ink">{{ title }}</h2>
          <p v-if="description" id="confirm-description" class="mt-2 text-sm text-ink-muted">
            {{ description }}
          </p>

          <div class="mt-6 flex justify-end gap-3">
            <AppButton variant="secondary" :disabled="loading" @click="cancel">
              {{ cancelLabel }}
            </AppButton>
            <AppButton variant="danger" :loading="loading" @click="emit('confirm')">
              {{ confirmLabel }}
            </AppButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
