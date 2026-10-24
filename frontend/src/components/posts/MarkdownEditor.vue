<script setup lang="ts">
import { Eye } from 'lucide-vue-next'
import { ref } from 'vue'

import AppButton from '@/components/common/AppButton.vue'
import PreviewModal from '@/components/common/PreviewModal.vue'

const model = defineModel<string>({ required: true })

defineProps<{
  id: string
  describedBy?: string
  invalid?: boolean
}>()

const previewOpen = ref(false)

const GUIDE = [
  { label: 'Bold', syntax: '**bold text**' },
  { label: 'Italic', syntax: '*italic*' },
  { label: 'Heading', syntax: '# Title  ·  ## Section' },
  { label: 'Bullet list', syntax: '- item' },
  { label: 'Numbered list', syntax: '1. item' },
  { label: 'Inline code', syntax: '`code`' },
  { label: 'Code block', syntax: '```\ncode\n```' },
  { label: 'Link', syntax: '[text](https://example.com)' },
] as const

const inputClasses =
  'min-h-80 w-full resize-y rounded-lg border border-edge bg-black/30 px-3 py-2 font-mono text-[0.9rem] leading-relaxed text-white placeholder:text-ink-muted focus:border-emerald-400/50 focus:outline-none aria-[invalid=true]:border-rose-500/60'
</script>

<template>
  <div>
    <details class="rounded-lg border border-edge bg-black/20 px-3 py-2">
      <summary class="cursor-pointer text-sm font-medium text-white">Formatting help</summary>
      <p class="mt-2 text-xs text-ink-muted">
        Type these marks in the editor. They become styled text when you preview or publish.
      </p>
      <ul class="mt-3 grid gap-2 sm:grid-cols-2">
        <li v-for="item in GUIDE" :key="item.label" class="rounded-md border border-edge bg-surface/60 px-2.5 py-2">
          <p class="text-xs font-medium text-emerald-200">{{ item.label }}</p>
          <code class="mt-1 block font-mono text-[0.75rem] whitespace-pre-wrap text-ink-muted">{{ item.syntax }}</code>
        </li>
      </ul>
    </details>

    <div class="mt-3 flex justify-end">
      <AppButton variant="secondary" size="sm" type="button" @click="previewOpen = true">
        <Eye class="h-3.5 w-3.5" aria-hidden="true" />
        Preview
      </AppButton>
    </div>

    <textarea
      :id="id"
      v-model="model"
      rows="16"
      :aria-invalid="invalid || undefined"
      :aria-describedby="describedBy"
      :class="[inputClasses, 'mt-3']"
      placeholder="Write your article in Markdown..."
    />

    <PreviewModal :open="previewOpen" :source="model" @close="previewOpen = false" />
  </div>
</template>
