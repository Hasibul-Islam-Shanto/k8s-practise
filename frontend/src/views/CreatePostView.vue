<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import PostForm from '@/components/posts/PostForm.vue'
import { errorMessage, fieldErrors } from '@/services/api'
import { postService } from '@/services/post.service'
import type { PostPayload } from '@/types/post'

const router = useRouter()

const submitting = ref(false)
const serverError = ref('')
const formFieldErrors = ref<Record<string, string>>({})

async function publish(payload: PostPayload): Promise<void> {
  submitting.value = true
  serverError.value = ''
  formFieldErrors.value = {}
  try {
    const post = await postService.create(payload)
    await router.push({ name: 'post', params: { id: post.id } })
  } catch (err) {
    formFieldErrors.value = fieldErrors(err)
    if (Object.keys(formFieldErrors.value).length === 0) {
      serverError.value = errorMessage(err, 'Unable to publish your article. Please try again.')
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl">
    <header class="mb-6">
      <h1 class="text-2xl font-semibold tracking-tight text-ink">Write an article</h1>
      <p class="mt-1.5 text-sm text-ink-muted">Share something you have learned recently.</p>
    </header>

    <PostForm
      submit-label="Publish Post"
      :submitting="submitting"
      :server-error="serverError"
      :field-errors="formFieldErrors"
      @submit="publish"
      @cancel="router.back()"
    />
  </div>
</template>
