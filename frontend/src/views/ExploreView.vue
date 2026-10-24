<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import { Search, X } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import PostList from '@/components/posts/PostList.vue'
import { usePostFeed } from '@/composables/usePostFeed'
import { postService } from '@/services/post.service'
import { SUGGESTED_TAGS, tagSlug } from '@/utils/tags'

const route = useRoute()
const router = useRouter()

const search = ref(typeof route.query.q === 'string' ? route.query.q : '')
const activeTag = ref(typeof route.query.tag === 'string' ? route.query.tag : '')

const debouncedSearch = refDebounced(search, 350)

const { posts, loading, loadingMore, error, total, hasMore, load, loadMore, applyLikeChange } =
  usePostFeed((page) =>
    postService.list({
      page,
      limit: 10,
      search: debouncedSearch.value.trim() || undefined,
      tag: activeTag.value || undefined,
    }),
  )

const emptyTitle = computed(() => {
  if (debouncedSearch.value.trim()) return `No articles found for "${debouncedSearch.value.trim()}".`
  if (activeTag.value) return 'No articles with this tag yet.'
  return 'No posts yet.'
})

function toggleTag(slug: string): void {
  activeTag.value = activeTag.value === slug ? '' : slug
}

function clearFilters(): void {
  search.value = ''
  activeTag.value = ''
}

watch([debouncedSearch, activeTag], ([query, tag]) => {
  const next: Record<string, string> = {}
  if (query.trim()) next.q = query.trim()
  if (tag) next.tag = tag
  router.replace({ name: 'explore', query: next })
  load()
})

watch(
  () => route.query,
  (query) => {
    const nextSearch = typeof query.q === 'string' ? query.q : ''
    const nextTag = typeof query.tag === 'string' ? query.tag : ''
    if (nextSearch !== search.value) search.value = nextSearch
    if (nextTag !== activeTag.value) activeTag.value = nextTag
  },
)

const hasFilters = computed(() => Boolean(search.value.trim() || activeTag.value))

onMounted(load)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl">
    <header class="mb-6">
      <h1 class="text-3xl font-semibold tracking-tight text-ink">Explore</h1>
      <p class="mt-1.5 text-emerald-100/70">Search by title, author or technology tag.</p>
    </header>

    <div role="search" class="relative">
      <label for="explore-search" class="sr-only">Search articles</label>
      <Search
        class="pointer-events-none absolute top-1/2 left-3.5 h-4 w-4 -translate-y-1/2 text-ink-muted"
        aria-hidden="true"
      />
      <input
        id="explore-search"
        v-model="search"
        type="search"
        placeholder="Search articles, authors or tags..."
        class="w-full rounded-lg border border-edge bg-surface py-2.5 pr-3 pl-10 text-sm text-ink placeholder:text-ink-muted focus:border-accent/50 focus:outline-none"
      />
    </div>

    <ul class="mt-4 flex flex-wrap gap-2" aria-label="Filter by tag">
      <li v-for="tag in SUGGESTED_TAGS" :key="tag">
        <button
          type="button"
          :aria-pressed="activeTag === tagSlug(tag)"
          :class="
            activeTag === tagSlug(tag)
              ? 'border-accent/60 bg-accent/15 text-ink'
              : 'border-edge bg-surface text-ink-muted hover:border-accent/40 hover:text-ink'
          "
          class="rounded-md border px-2.5 py-1 text-xs font-medium transition-colors"
          @click="toggleTag(tagSlug(tag))"
        >
          {{ tag }}
        </button>
      </li>
    </ul>

    <div class="mt-5 mb-6 flex items-center justify-between gap-3 text-sm text-ink-muted">
      <p v-if="!loading" role="status">
        {{ total }} {{ total === 1 ? 'article' : 'articles' }}
      </p>
      <span v-else></span>
      <button
        v-if="hasFilters"
        type="button"
        class="inline-flex items-center gap-1.5 rounded-lg px-2 py-1 transition-colors hover:bg-surface hover:text-ink"
        @click="clearFilters"
      >
        <X class="h-3.5 w-3.5" aria-hidden="true" />
        Clear filters
      </button>
    </div>

    <PostList
      two-columns
      :posts="posts"
      :loading="loading"
      :loading-more="loadingMore"
      :error="error"
      :has-more="hasMore"
      :empty-title="emptyTitle"
      empty-description="Try a different search term or tag."
      @load-more="loadMore"
      @retry="load"
      @like-change="applyLikeChange"
    />
  </div>
</template>
