<script setup lang="ts">
import { Calendar, CircleAlert, Clock, Pencil, Trash2 } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppButton from '@/components/common/AppButton.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import StateMessage from '@/components/common/StateMessage.vue'
import TagPill from '@/components/common/TagPill.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import LikeButton from '@/components/posts/LikeButton.vue'
import CommentSection from '@/components/comments/CommentSection.vue'
import MarkdownContent from '@/components/posts/MarkdownContent.vue'
import { errorMessage } from '@/services/api'
import { postService } from '@/services/post.service'
import { useAuthStore } from '@/stores/auth'
import type { Post } from '@/types/post'
import { formatDate, readingTime } from '@/utils/format'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const post = ref<Post | null>(null)
const loading = ref(true)
const loadError = ref('')
const notFound = ref(false)

const confirmOpen = ref(false)
const deleting = ref(false)
const deleteError = ref('')

const isOwner = computed(() => Boolean(post.value && post.value.author.id === auth.user?.id))
const minutes = computed(() => (post.value ? readingTime(post.value.content) : 0))

async function load(): Promise<void> {
  loading.value = true
  loadError.value = ''
  notFound.value = false
  try {
    post.value = await postService.get(route.params.id as string)
    document.title = `${post.value.title} — TechBlog`
  } catch (err) {
    post.value = null
    const status = (err as { response?: { status?: number } }).response?.status
    if (status === 404) notFound.value = true
    else loadError.value = errorMessage(err, 'Please try again.')
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => route.params.id, load)

function applyLikeChange(change: { liked: boolean; likeCount: number }): void {
  if (!post.value) return
  post.value.liked_by_current_user = change.liked
  post.value.like_count = change.likeCount
}

async function confirmDelete(): Promise<void> {
  if (!post.value) return
  deleting.value = true
  deleteError.value = ''
  try {
    await postService.remove(post.value.id)
    await router.push({ name: 'profile' })
  } catch (err) {
    deleteError.value = errorMessage(err, 'Unable to delete this article. Please try again.')
    confirmOpen.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl">
    <div v-if="loading" class="space-y-6" aria-hidden="true">
      <span class="sr-only" role="status">Loading article</span>
      <div class="skeleton h-10 w-11/12"></div>
      <div class="skeleton h-10 w-2/3"></div>
      <div class="flex items-center gap-3 pt-2">
        <div class="skeleton h-10 w-10 rounded-full"></div>
        <div class="space-y-2">
          <div class="skeleton h-3.5 w-32"></div>
          <div class="skeleton h-3 w-48"></div>
        </div>
      </div>
      <div class="space-y-3 pt-6">
        <div v-for="index in 8" :key="index" class="skeleton h-4" :class="index % 3 === 0 ? 'w-10/12' : 'w-full'"></div>
      </div>
    </div>

    <StateMessage
      v-else-if="notFound"
      title="This article doesn't exist."
      description="It may have been deleted by its author."
    >
      <template #icon><CircleAlert class="h-5 w-5" aria-hidden="true" /></template>
      <template #action>
        <AppButton variant="secondary" size="sm" @click="router.push({ name: 'home' })">
          Back to the feed
        </AppButton>
      </template>
    </StateMessage>

    <StateMessage
      v-else-if="loadError"
      tone="error"
      title="Unable to load this article."
      :description="loadError"
    >
      <template #icon><CircleAlert class="h-5 w-5" aria-hidden="true" /></template>
      <template #action>
        <AppButton variant="secondary" size="sm" @click="load">Try again</AppButton>
      </template>
    </StateMessage>

    <article v-else-if="post">
      <h1 class="text-3xl leading-tight font-semibold tracking-tight text-ink sm:text-4xl">
        {{ post.title }}
      </h1>

      <div class="mt-6 flex flex-wrap items-center gap-x-4 gap-y-3">
        <RouterLink
          :to="{ name: 'user', params: { username: post.author.username } }"
          class="flex items-center gap-3"
        >
          <UserAvatar
            :full-name="post.author.full_name"
            :username="post.author.username"
            :avatar-url="post.author.avatar_url"
          />
          <span class="text-sm">
            <span class="block font-medium text-ink">{{ post.author.full_name }}</span>
            <span class="block text-ink-muted">@{{ post.author.username }}</span>
          </span>
        </RouterLink>

        <span class="flex items-center gap-4 text-xs text-ink-muted">
          <span class="inline-flex items-center gap-1.5">
            <Calendar class="h-3.5 w-3.5" aria-hidden="true" />
            <time :datetime="post.created_at">{{ formatDate(post.created_at) }}</time>
          </span>
          <span class="inline-flex items-center gap-1.5">
            <Clock class="h-3.5 w-3.5" aria-hidden="true" />
            {{ minutes }} min read
          </span>
        </span>

        <div v-if="isOwner" class="ml-auto flex gap-2">
          <AppButton
            variant="secondary"
            size="sm"
            @click="router.push({ name: 'post-edit', params: { id: post.id } })"
          >
            <Pencil class="h-3.5 w-3.5" aria-hidden="true" />
            Edit
          </AppButton>
          <AppButton variant="secondary" size="sm" @click="confirmOpen = true">
            <Trash2 class="h-3.5 w-3.5" aria-hidden="true" />
            Delete
          </AppButton>
        </div>
      </div>

      <ul v-if="post.tags.length" class="mt-6 flex flex-wrap gap-2">
        <li v-for="tag in post.tags" :key="tag.id">
          <TagPill :name="tag.name" :to="`/explore?tag=${encodeURIComponent(tag.slug)}`" />
        </li>
      </ul>

      <p
        v-if="deleteError"
        role="alert"
        class="mt-6 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-300"
      >
        {{ deleteError }}
      </p>

      <hr class="mt-8 border-edge" />

      <MarkdownContent class="mt-8" :source="post.content" />

      <div class="mt-10 flex items-center gap-3 border-t border-edge pt-6">
        <LikeButton
          :post-id="post.id"
          :liked="post.liked_by_current_user"
          :like-count="post.like_count"
          size="md"
          @change="applyLikeChange"
        />
      </div>

      <CommentSection :post-id="post.id" />

      <aside class="card mt-8 flex flex-col gap-4 p-6 sm:flex-row sm:items-center">
        <UserAvatar
          :full-name="post.author.full_name"
          :username="post.author.username"
          :avatar-url="post.author.avatar_url"
          size="lg"
        />
        <div class="min-w-0 flex-1">
          <h2 class="text-base font-semibold text-ink">{{ post.author.full_name }}</h2>
          <p class="text-sm text-ink-muted">@{{ post.author.username }}</p>
        </div>
        <AppButton
          variant="secondary"
          size="sm"
          @click="router.push({ name: 'user', params: { username: post.author.username } })"
        >
          View profile
        </AppButton>
      </aside>
    </article>

    <ConfirmModal
      :open="confirmOpen"
      title="Delete this article?"
      description="This action cannot be undone."
      confirm-label="Delete"
      :loading="deleting"
      @confirm="confirmDelete"
      @cancel="confirmOpen = false"
    />
  </div>
</template>
