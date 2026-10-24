<script setup lang="ts">
import { onKeyStroke } from '@vueuse/core'
import { nextTick, ref, watch } from 'vue'

import AppButton from '@/components/common/AppButton.vue'
import MarkdownContent from '@/components/posts/MarkdownContent.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title?: string
    source: string
  }>(),
  { title: 'Article preview' },
)

const emit = defineEmits<{ close: [] }>()

const dialog = ref<HTMLElement | null>(null)

onKeyStroke('Escape', () => {
  if (props.open) emit('close')
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
        @click.self="emit('close')"
      >
        <div
          ref="dialog"
          role="dialog"
          aria-modal="true"
          aria-labelledby="preview-title"
          class="flex max-h-[85vh] w-full max-w-3xl flex-col rounded-xl border border-edge bg-surface shadow-lg"
        >
          <div class="flex items-center justify-between gap-3 border-b border-edge px-6 py-4">
            <h2 id="preview-title" class="text-lg font-semibold text-ink">{{ title }}</h2>
            <AppButton variant="secondary" size="sm" @click="emit('close')">Close</AppButton>
          </div>
          <div class="overflow-y-auto px-6 py-5">
            <MarkdownContent :source="source" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
