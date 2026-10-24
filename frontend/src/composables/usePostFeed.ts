import { computed, ref } from 'vue'

import { errorMessage } from '@/services/api'
import type { Page, Post } from '@/types/post'

type Fetcher = (page: number) => Promise<Page<Post>>

export function usePostFeed(fetchPage: Fetcher) {
  const posts = ref<Post[]>([])
  const loading = ref(false)
  const loadingMore = ref(false)
  const error = ref('')
  const total = ref(0)
  const page = ref(1)
  const totalPages = ref(0)

  const hasMore = computed(() => page.value < totalPages.value)

  async function load(): Promise<void> {
    loading.value = true
    error.value = ''
    page.value = 1
    try {
      const result = await fetchPage(1)
      posts.value = result.items
      total.value = result.total
      totalPages.value = result.total_pages
    } catch (err) {
      error.value = errorMessage(err, 'Please try again.')
      posts.value = []
    } finally {
      loading.value = false
    }
  }

  async function loadMore(): Promise<void> {
    if (loadingMore.value || !hasMore.value) return
    loadingMore.value = true
    try {
      const next = page.value + 1
      const result = await fetchPage(next)
      posts.value = [...posts.value, ...result.items]
      page.value = next
      total.value = result.total
      totalPages.value = result.total_pages
    } catch (err) {
      error.value = errorMessage(err, 'Please try again.')
    } finally {
      loadingMore.value = false
    }
  }

  function applyLikeChange(postId: number, change: { liked: boolean; likeCount: number }): void {
    const post = posts.value.find((item) => item.id === postId)
    if (!post) return
    post.liked_by_current_user = change.liked
    post.like_count = change.likeCount
  }

  return {
    posts,
    loading,
    loadingMore,
    error,
    total,
    hasMore,
    load,
    loadMore,
    applyLikeChange,
  }
}
