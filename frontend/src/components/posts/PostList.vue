<script setup lang="ts">
import { CircleAlert, FileText } from 'lucide-vue-next'

import { computed } from 'vue'

import AppButton from '@/components/common/AppButton.vue'
import StateMessage from '@/components/common/StateMessage.vue'
import PostCard from '@/components/posts/PostCard.vue'
import PostCardSkeleton from '@/components/posts/PostCardSkeleton.vue'
import type { Post } from '@/types/post'

const props = withDefaults(
  defineProps<{
    posts: Post[]
    loading: boolean
    loadingMore?: boolean
    error?: string
    hasMore?: boolean
    emptyTitle?: string
    emptyDescription?: string
    skeletonCount?: number
    twoColumns?: boolean
  }>(),
  {
    loadingMore: false,
    error: '',
    hasMore: false,
    emptyTitle: 'No posts yet.',
    emptyDescription: "Start sharing something you've learned.",
    skeletonCount: 4,
    twoColumns: false,
  },
)

const gridClass = computed(() =>
  props.twoColumns
    ? 'grid grid-cols-2 items-stretch gap-4 sm:gap-5'
    : 'grid grid-cols-1 items-stretch gap-4 sm:grid-cols-2 sm:gap-5',
)

const emit = defineEmits<{ loadMore: []; retry: []; likeChange: [number, { liked: boolean; likeCount: number }] }>()
</script>

<template>
  <div>
    <div v-if="loading">
      <span class="sr-only" role="status">Loading posts</span>
      <div :class="gridClass">
        <PostCardSkeleton v-for="index in skeletonCount" :key="index" class="min-w-0" />
      </div>
    </div>

    <StateMessage
      v-else-if="error"
      tone="error"
      title="Unable to load posts."
      :description="error"
    >
      <template #icon><CircleAlert class="h-5 w-5" aria-hidden="true" /></template>
      <template #action>
        <AppButton variant="secondary" size="sm" @click="emit('retry')">Try again</AppButton>
      </template>
    </StateMessage>

    <StateMessage
      v-else-if="posts.length === 0"
      :title="emptyTitle"
      :description="emptyDescription"
    >
      <template #icon><FileText class="h-5 w-5" aria-hidden="true" /></template>
      <template #action><slot name="empty-action" /></template>
    </StateMessage>

    <template v-else>
      <div :class="gridClass">
        <PostCard
          v-for="(post, index) in posts"
          :key="post.id"
          :post="post"
          class="h-full min-w-0 motion-safe:animate-fade-in-up motion-reduce:opacity-100"
          :style="{ animationDelay: `${index * 60}ms` }"
          @like-change="emit('likeChange', post.id, $event)"
        />
      </div>

      <div v-if="hasMore" class="mt-8 flex justify-center">
        <AppButton variant="secondary" :loading="loadingMore" @click="emit('loadMore')">
          Load more
        </AppButton>
      </div>
    </template>
  </div>
</template>
