<script setup lang="ts">
import { Pencil, ThumbsUp, Trash2 } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import AppButton from '@/components/common/AppButton.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { errorMessage } from '@/services/api'
import { commentService } from '@/services/comment.service'
import { useAuthStore } from '@/stores/auth'
import type { Comment } from '@/types/comment'
import { formatCount, relativeTime } from '@/utils/format'

const props = defineProps<{ postId: number }>()

const PAGE_SIZE = 20
const inputClasses =
  'w-full rounded-lg border border-edge bg-surface-muted px-3 py-2 text-sm text-ink placeholder:text-ink-muted focus:border-accent/50 focus:outline-none'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const comments = ref<Comment[]>([])
const page = ref(0)
const totalPages = ref(0)
const total = ref(0)
const loading = ref(true)
const loadingMore = ref(false)
const loadError = ref('')

const draft = ref('')
const submitting = ref(false)
const formError = ref('')

const editingId = ref<number | null>(null)
const editDraft = ref('')
const savingEdit = ref(false)
const editError = ref('')

const deleteTarget = ref<Comment | null>(null)
const deleting = ref(false)
const deleteError = ref('')
const pendingLikes = ref<Record<number, boolean>>({})

const loginTo = computed(() => ({ name: 'login' as const, query: { redirect: route.fullPath } }))
const hasMore = computed(() => page.value < totalPages.value)

function isOwner(comment: Comment): boolean {
  return comment.author.id === auth.user?.id
}

async function loadFirst(): Promise<void> {
  loading.value = true
  loadError.value = ''
  editingId.value = null
  try {
    const result = await commentService.list(props.postId, { page: 1, limit: PAGE_SIZE })
    comments.value = result.items
    page.value = result.page
    totalPages.value = result.total_pages
    total.value = result.total
  } catch (err) {
    comments.value = []
    loadError.value = errorMessage(err, 'Unable to load comments.')
  } finally {
    loading.value = false
  }
}

async function loadMore(): Promise<boolean> {
  if (loadingMore.value || page.value >= totalPages.value) return false
  loadingMore.value = true
  try {
    const result = await commentService.list(props.postId, {
      page: page.value + 1,
      limit: PAGE_SIZE,
    })
    const known = new Set(comments.value.map((item) => item.id))
    comments.value.push(...result.items.filter((item) => !known.has(item.id)))
    page.value = result.page
    totalPages.value = result.total_pages
    total.value = result.total
    return true
  } catch (err) {
    loadError.value = errorMessage(err, 'Unable to load more comments.')
    return false
  } finally {
    loadingMore.value = false
  }
}

async function submit(): Promise<void> {
  const body = draft.value.trim()
  if (!body || submitting.value) return
  submitting.value = true
  formError.value = ''
  try {
    const created = await commentService.create(props.postId, body)
    draft.value = ''
    total.value += 1
    totalPages.value = Math.max(1, Math.ceil(total.value / PAGE_SIZE))
    while (page.value < totalPages.value) {
      const loaded = await loadMore()
      if (!loaded) break
    }
    if (!comments.value.some((item) => item.id === created.id)) comments.value.push(created)
  } catch (err) {
    formError.value = errorMessage(err, 'Unable to post this comment.')
  } finally {
    submitting.value = false
  }
}

function startEdit(comment: Comment): void {
  editingId.value = comment.id
  editDraft.value = comment.body
  editError.value = ''
}

async function saveEdit(comment: Comment): Promise<void> {
  const body = editDraft.value.trim()
  if (!body || savingEdit.value) return
  savingEdit.value = true
  editError.value = ''
  try {
    const updated = await commentService.update(props.postId, comment.id, body)
    const index = comments.value.findIndex((item) => item.id === comment.id)
    if (index !== -1) comments.value[index] = updated
    editingId.value = null
  } catch (err) {
    editError.value = errorMessage(err, 'Unable to update this comment.')
  } finally {
    savingEdit.value = false
  }
}

async function confirmDelete(): Promise<void> {
  const target = deleteTarget.value
  if (!target) return
  deleting.value = true
  deleteError.value = ''
  try {
    await commentService.remove(props.postId, target.id)
    comments.value = comments.value.filter((item) => item.id !== target.id)
    total.value = Math.max(0, total.value - 1)
    totalPages.value = total.value === 0 ? 0 : Math.ceil(total.value / PAGE_SIZE)
    if (page.value > totalPages.value) page.value = totalPages.value
    deleteTarget.value = null
  } catch (err) {
    deleteError.value = errorMessage(err, 'Unable to delete this comment.')
    deleteTarget.value = null
  } finally {
    deleting.value = false
  }
}

async function toggleLike(comment: Comment): Promise<void> {
  if (!auth.isAuthenticated) {
    router.push(loginTo.value)
    return
  }
  if (pendingLikes.value[comment.id]) return

  const previous = { liked: comment.liked_by_current_user, count: comment.like_count }
  comment.liked_by_current_user = !previous.liked
  comment.like_count = previous.count + (previous.liked ? -1 : 1)
  pendingLikes.value = { ...pendingLikes.value, [comment.id]: true }
  try {
    const result = previous.liked
      ? await commentService.unlike(props.postId, comment.id)
      : await commentService.like(props.postId, comment.id)
    comment.liked_by_current_user = result.liked
    comment.like_count = result.like_count
  } catch {
    comment.liked_by_current_user = previous.liked
    comment.like_count = previous.count
  } finally {
    const next = { ...pendingLikes.value }
    delete next[comment.id]
    pendingLikes.value = next
  }
}

watch(() => props.postId, loadFirst, { immediate: true })
watch(() => auth.isAuthenticated, () => {
  loadFirst()
})
</script>

<template>
  <section class="mt-10 border-t border-edge pt-8" aria-labelledby="comments-heading">
    <h2 id="comments-heading" class="text-lg font-semibold text-ink">
      Comments
      <span class="font-normal text-ink-muted">({{ total }})</span>
    </h2>

    <p v-if="loading" class="mt-4 text-sm text-ink-muted" role="status">Loading comments</p>
    <p v-else-if="loadError" role="alert" class="mt-4 text-sm text-rose-300">{{ loadError }}</p>
    <p v-else-if="comments.length === 0" class="mt-4 text-sm text-ink-muted">No comments yet.</p>

    <ul v-else class="mt-6 space-y-6">
      <li v-for="comment in comments" :key="comment.id" class="flex gap-3">
        <RouterLink :to="{ name: 'user', params: { username: comment.author.username } }">
          <UserAvatar
            :full-name="comment.author.full_name"
            :username="comment.author.username"
            :avatar-url="comment.author.avatar_url"
            size="sm"
          />
        </RouterLink>
        <div class="min-w-0 flex-1">
          <div class="flex flex-wrap items-baseline gap-x-2">
            <RouterLink
              :to="{ name: 'user', params: { username: comment.author.username } }"
              class="text-sm font-medium text-ink hover:text-accent"
            >
              {{ comment.author.full_name }}
            </RouterLink>
            <time class="text-xs text-ink-muted" :datetime="comment.created_at">
              {{ relativeTime(comment.created_at) }}
            </time>
          </div>

          <form v-if="editingId === comment.id" class="mt-2 space-y-2" @submit.prevent="saveEdit(comment)">
            <textarea
              v-model="editDraft"
              rows="3"
              maxlength="2000"
              class="resize-y"
              :class="inputClasses"
              :aria-label="`Edit comment by ${comment.author.full_name}`"
            />
            <p v-if="editError" role="alert" class="text-sm text-rose-300">{{ editError }}</p>
            <div class="flex gap-2">
              <AppButton type="submit" size="sm" :loading="savingEdit">Save</AppButton>
              <AppButton variant="ghost" size="sm" @click="editingId = null">Cancel</AppButton>
            </div>
          </form>
          <p v-else class="mt-1 text-sm whitespace-pre-wrap text-ink">{{ comment.body }}</p>

          <div class="mt-2 flex flex-wrap items-center gap-2">
            <button
              type="button"
              class="inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-medium transition-colors hover:bg-surface-muted disabled:opacity-60"
              :class="comment.liked_by_current_user ? 'text-accent' : 'text-ink-muted hover:text-ink'"
              :aria-pressed="comment.liked_by_current_user"
              :aria-label="comment.liked_by_current_user ? 'Unlike this comment' : 'Like this comment'"
              :disabled="pendingLikes[comment.id]"
              @click="toggleLike(comment)"
            >
              <ThumbsUp
                class="h-4 w-4"
                :class="comment.liked_by_current_user && 'fill-current'"
                aria-hidden="true"
              />
              <span>{{ formatCount(comment.like_count, 'like') }}</span>
            </button>
            <template v-if="isOwner(comment) && editingId !== comment.id">
              <button
                type="button"
                class="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs font-medium text-ink-muted hover:bg-surface-muted hover:text-ink"
                @click="startEdit(comment)"
              >
                <Pencil class="h-3.5 w-3.5" aria-hidden="true" />
                Edit
              </button>
              <button
                type="button"
                class="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs font-medium text-ink-muted hover:bg-surface-muted hover:text-ink"
                @click="deleteTarget = comment"
              >
                <Trash2 class="h-3.5 w-3.5" aria-hidden="true" />
                Delete
              </button>
            </template>
          </div>
        </div>
      </li>
    </ul>

    <p v-if="deleteError" role="alert" class="mt-4 text-sm text-rose-300">{{ deleteError }}</p>

    <AppButton
      v-if="hasMore"
      class="mt-6"
      variant="secondary"
      size="sm"
      :loading="loadingMore"
      @click="loadMore"
    >
      Load more comments
    </AppButton>

    <form v-if="auth.isAuthenticated" class="mt-8 space-y-3" @submit.prevent="submit">
      <label for="new-comment" class="text-sm font-medium text-ink">Write a comment</label>
      <textarea
        id="new-comment"
        v-model="draft"
        rows="3"
        maxlength="2000"
        class="resize-y"
        :class="inputClasses"
        placeholder="Share a thought about this article"
      />
      <p v-if="formError" role="alert" class="text-sm text-rose-300">{{ formError }}</p>
      <AppButton type="submit" size="sm" :loading="submitting" :disabled="!draft.trim()">
        Post comment
      </AppButton>
    </form>
    <p v-else class="mt-8 text-sm text-ink-muted">
      <RouterLink :to="loginTo" class="font-medium text-accent hover:text-accent-hover">Log in</RouterLink>
      to comment.
    </p>

    <ConfirmModal
      :open="deleteTarget !== null"
      title="Delete this comment?"
      description="This action cannot be undone."
      confirm-label="Delete"
      :loading="deleting"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </section>
</template>
