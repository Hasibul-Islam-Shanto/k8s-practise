<script setup lang="ts">
import { CircleAlert } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import StateMessage from '@/components/common/StateMessage.vue'
import PostForm from '@/components/posts/PostForm.vue'
import { errorMessage, fieldErrors } from '@/services/api'
import { postService } from '@/services/post.service'
import { useAuthStore } from '@/stores/auth'
import type { PostPayload } from '@/types/post'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const postId = route.params.id as string
const initial = ref<PostPayload | null>(null)
const loading = ref(true)
const loadError = ref('')
const submitting = ref(false)
const serverError = ref('')
const formFieldErrors = ref<Record<string, string>>({})

onMounted(async () => {
  try {
    const post = await postService.get(postId)
    // The API rejects a non-owner's update regardless; this just avoids showing
    // a form that could never be saved.
    if (post.author.id !== auth.user?.id) {
      await router.replace({ name: 'post', params: { id: postId } })
      return
    }
    initial.value = {
      title: post.title,
      excerpt: post.excerpt,
      content: post.content,
      tags: post.tags.map((tag) => tag.name),
    }
  } catch (err) {
    loadError.value = errorMessage(err, 'Please try again.')
  } finally {
    loading.value = false
  }
})

async function save(payload: PostPayload): Promise<void> {
  submitting.value = true
  serverError.value = ''
  formFieldErrors.value = {}
  try {
    await postService.update(postId, payload)
    await router.push({ name: 'post', params: { id: postId } })
  } catch (err) {
    formFieldErrors.value = fieldErrors(err)
    if (Object.keys(formFieldErrors.value).length === 0) {
      serverError.value = errorMessage(err, 'Unable to save your changes. Please try again.')
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl">
    <header class="mb-6">
      <h1 class="text-2xl font-semibold tracking-tight text-ink">Edit article</h1>
      <p class="mt-1.5 text-sm text-ink-muted">Update the title, description, tags or content.</p>
    </header>

    <div v-if="loading" class="card space-y-5 p-6" aria-hidden="true">
      <div class="skeleton h-4 w-16"></div>
      <div class="skeleton h-10 w-full"></div>
      <div class="skeleton h-4 w-24"></div>
      <div class="skeleton h-20 w-full"></div>
      <div class="skeleton h-4 w-16"></div>
      <div class="skeleton h-64 w-full"></div>
    </div>

    <StateMessage
      v-else-if="loadError"
      tone="error"
      title="Unable to load this article."
      :description="loadError"
    >
      <template #icon><CircleAlert class="h-5 w-5" aria-hidden="true" /></template>
    </StateMessage>

    <PostForm
      v-else-if="initial"
      :initial="initial"
      submit-label="Save changes"
      :submitting="submitting"
      :server-error="serverError"
      :field-errors="formFieldErrors"
      @submit="save"
      @cancel="router.push({ name: 'post', params: { id: postId } })"
    />
  </div>
</template>
