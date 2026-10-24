<script setup lang="ts">
import { CircleAlert } from 'lucide-vue-next'
import { computed, reactive, watch } from 'vue'
import { z } from 'zod'

import AppButton from '@/components/common/AppButton.vue'
import FormField from '@/components/common/FormField.vue'
import MarkdownEditor from '@/components/posts/MarkdownEditor.vue'
import type { PostPayload } from '@/types/post'
import { readingTime } from '@/utils/format'
import { MAX_TAGS_PER_POST, SUGGESTED_TAGS, parseTags } from '@/utils/tags'

const props = withDefaults(
  defineProps<{
    initial?: PostPayload | null
    submitLabel?: string
    submitting?: boolean
    serverError?: string
    fieldErrors?: Record<string, string>
  }>(),
  {
    initial: null,
    submitLabel: 'Publish Post',
    submitting: false,
    serverError: '',
    fieldErrors: () => ({}),
  },
)

const emit = defineEmits<{ submit: [PostPayload]; cancel: [] }>()

const form = reactive({ title: '', excerpt: '', content: '', tags: '' })
const errors = reactive<Record<string, string>>({})

// The same limits the API enforces, so the user sees the problem before submitting.
const schema = z.object({
  title: z
    .string()
    .trim()
    .min(5, 'Titles must be at least 5 characters')
    .max(200, 'Titles must be 200 characters or fewer'),
  excerpt: z
    .string()
    .trim()
    .min(10, 'Write a short description of at least 10 characters')
    .max(500, 'Descriptions must be 500 characters or fewer'),
  content: z
    .string()
    .trim()
    .min(50, 'Articles must be at least 50 characters')
    .max(50_000, 'That article is too long'),
  tags: z
    .array(z.string())
    .min(1, 'Add at least one technology tag')
    .max(MAX_TAGS_PER_POST, `Use at most ${MAX_TAGS_PER_POST} tags`),
})

const parsedTags = computed(() => parseTags(form.tags))
const minutes = computed(() => (form.content.trim() ? readingTime(form.content) : 0))

watch(
  () => props.initial,
  (initial) => {
    if (!initial) return
    form.title = initial.title
    form.excerpt = initial.excerpt
    form.content = initial.content
    form.tags = initial.tags.join(', ')
  },
  { immediate: true },
)

watch(
  () => props.fieldErrors,
  (incoming) => Object.assign(errors, incoming),
)

const inputClasses =
  'w-full rounded-lg border border-edge bg-surface-muted px-3 py-2 text-sm text-ink placeholder:text-ink-muted focus:border-accent/50 focus:outline-none aria-[invalid=true]:border-rose-500/60'

function addSuggestedTag(tag: string): void {
  const current = parsedTags.value
  if (current.some((name) => name.toLowerCase() === tag.toLowerCase())) return
  if (current.length >= MAX_TAGS_PER_POST) return
  form.tags = [...current, tag].join(', ')
}

const tagsFull = computed(() => parsedTags.value.length >= MAX_TAGS_PER_POST)

function submit(): void {
  for (const key of Object.keys(errors)) delete errors[key]

  const parsed = schema.safeParse({ ...form, tags: parsedTags.value })
  if (!parsed.success) {
    for (const issue of parsed.error.issues) {
      const field = String(issue.path[0])
      if (!errors[field]) errors[field] = issue.message
    }
    return
  }
  emit('submit', parsed.data)
}
</script>

<template>
  <form class="card space-y-6 p-6" novalidate @submit.prevent="submit">
    <p
      v-if="serverError"
      role="alert"
      class="flex items-start gap-2 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-300"
    >
      <CircleAlert class="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      {{ serverError }}
    </p>

    <FormField label="Title" input-id="title" :error="errors.title">
      <template #default="{ describedBy, invalid }">
        <input
          id="title"
          v-model="form.title"
          type="text"
          :aria-invalid="invalid"
          :aria-describedby="describedBy"
          :class="inputClasses"
          placeholder="What's your article about?"
        />
      </template>
    </FormField>

    <FormField
      label="Description"
      input-id="excerpt"
      :error="errors.excerpt"
      :hint="`${form.excerpt.trim().length}/500`"
    >
      <template #default="{ describedBy, invalid }">
        <textarea
          id="excerpt"
          v-model="form.excerpt"
          rows="2"
          :aria-invalid="invalid"
          :aria-describedby="describedBy"
          :class="[inputClasses, 'resize-y']"
          placeholder="Write a short summary..."
        />
      </template>
    </FormField>

    <FormField
      label="Tags"
      input-id="tags"
      :error="errors.tags"
      :hint="`${parsedTags.length}/${MAX_TAGS_PER_POST}`"
    >
      <template #default="{ describedBy, invalid }">
        <input
          id="tags"
          v-model="form.tags"
          type="text"
          :aria-invalid="invalid"
          :aria-describedby="describedBy ?? 'tags-help'"
          :class="inputClasses"
          placeholder="Vue, FastAPI, MySQL"
        />
      </template>
    </FormField>

    <div>
      <p id="tags-help" class="text-xs text-ink-muted">
        Separate tags with commas, or pick from the suggestions below.
      </p>
      <ul class="mt-2 flex flex-wrap gap-2">
        <li v-for="tag in SUGGESTED_TAGS" :key="tag">
          <button
            type="button"
            :disabled="tagsFull"
            class="rounded-md border border-edge bg-surface px-2 py-0.5 text-xs text-ink-muted transition-colors hover:border-accent/40 hover:text-ink disabled:cursor-not-allowed disabled:opacity-40"
            @click="addSuggestedTag(tag)"
          >
            {{ tag }}
          </button>
        </li>
      </ul>
    </div>

    <FormField
      label="Content"
      input-id="content"
      :error="errors.content"
      :hint="minutes ? `${minutes} min read` : undefined"
    >
      <template #default="{ describedBy, invalid }">
        <MarkdownEditor
          id="content"
          v-model="form.content"
          :invalid="invalid"
          :described-by="describedBy"
        />
      </template>
    </FormField>

    <div class="flex flex-col-reverse gap-3 border-t border-edge pt-5 sm:flex-row sm:justify-end">
      <AppButton variant="secondary" :disabled="submitting" @click="emit('cancel')">
        Cancel
      </AppButton>
      <AppButton type="submit" :loading="submitting">{{ submitLabel }}</AppButton>
    </div>
  </form>
</template>
