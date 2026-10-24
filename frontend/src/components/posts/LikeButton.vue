<script setup lang="ts">
import { ThumbsUp } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { postService } from '@/services/post.service'
import { useAuthStore } from '@/stores/auth'
import { formatCount } from '@/utils/format'

const props = withDefaults(
  defineProps<{
    postId: number
    liked: boolean
    likeCount: number
    size?: 'sm' | 'md'
    showLabel?: boolean
  }>(),
  { size: 'sm', showLabel: true },
)

const emit = defineEmits<{ change: [{ liked: boolean; likeCount: number }] }>()

const auth = useAuthStore()
const router = useRouter()
const pending = ref(false)

const label = computed(() =>
  props.showLabel ? formatCount(props.likeCount, 'like') : String(props.likeCount),
)

async function toggle(): Promise<void> {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }
  if (pending.value) return

  const previous = { liked: props.liked, likeCount: props.likeCount }
  // Update immediately, then reconcile with the count the server reports.
  emit('change', { liked: !previous.liked, likeCount: previous.likeCount + (previous.liked ? -1 : 1) })

  pending.value = true
  try {
    const result = previous.liked
      ? await postService.unlike(props.postId)
      : await postService.like(props.postId)
    emit('change', { liked: result.liked, likeCount: result.like_count })
  } catch {
    emit('change', previous)
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <button
    type="button"
    :class="[
      size === 'md' ? 'px-3 py-2 text-sm' : 'px-2 py-1 text-xs',
      liked ? 'text-accent' : 'text-ink-muted hover:text-ink',
    ]"
    class="inline-flex items-center gap-1.5 rounded-lg font-medium transition-colors hover:bg-surface-muted disabled:opacity-60"
    :aria-pressed="liked"
    :aria-label="liked ? 'Unlike this post' : 'Like this post'"
    :disabled="pending"
    @click.stop.prevent="toggle"
  >
    <ThumbsUp
      :class="[size === 'md' ? 'h-5 w-5' : 'h-4 w-4', liked && 'fill-current']"
      aria-hidden="true"
    />
    <span>{{ label }}</span>
  </button>
</template>
