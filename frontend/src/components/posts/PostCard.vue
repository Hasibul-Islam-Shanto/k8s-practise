<script setup lang="ts">
import { Clock } from 'lucide-vue-next'
import { computed } from 'vue'

import TagPill from '@/components/common/TagPill.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import LikeButton from '@/components/posts/LikeButton.vue'
import type { Post } from '@/types/post'
import { readingTime, relativeTime } from '@/utils/format'

const props = defineProps<{ post: Post }>()
const emit = defineEmits<{ likeChange: [{ liked: boolean; likeCount: number }] }>()

const minutes = computed(() => readingTime(props.post.content))
</script>

<template>
  <article
    class="card group relative flex h-full flex-col overflow-hidden p-5 transition-all duration-300 ease-out hover:-translate-y-1 hover:border-emerald-500/30 hover:shadow-xl hover:shadow-emerald-900/20 focus-within:border-emerald-500/30 sm:p-6"
  >
    <div
      class="pointer-events-none absolute inset-x-0 top-0 h-px origin-left scale-x-0 bg-gradient-to-r from-emerald-400 via-teal-300 to-transparent transition-transform duration-300 group-hover:scale-x-100"
      aria-hidden="true"
    ></div>
    <div class="flex items-center gap-3">
      <RouterLink
        :to="{ name: 'user', params: { username: post.author.username } }"
        class="shrink-0"
        :aria-label="`View ${post.author.full_name}'s profile`"
      >
        <UserAvatar
          :full-name="post.author.full_name"
          :username="post.author.username"
          :avatar-url="post.author.avatar_url"
        />
      </RouterLink>

      <div class="min-w-0 text-sm">
        <RouterLink
          :to="{ name: 'user', params: { username: post.author.username } }"
          class="font-medium text-ink hover:text-accent-hover"
        >
          {{ post.author.full_name }}
        </RouterLink>
        <p class="truncate text-ink-muted">
          @{{ post.author.username }} ·
          <time :datetime="post.created_at">{{ relativeTime(post.created_at) }}</time>
        </p>
      </div>
    </div>

    <h2 class="mt-4 line-clamp-2 text-lg font-semibold tracking-tight text-ink sm:text-xl">
      <RouterLink
        :to="{ name: 'post', params: { id: post.id } }"
        class="transition-colors hover:text-accent-hover"
      >
        {{ post.title }}
      </RouterLink>
    </h2>

    <p class="mt-2 line-clamp-3 flex-1 text-[0.9375rem] leading-relaxed text-ink-muted">
      {{ post.excerpt }}
    </p>

    <ul v-if="post.tags.length" class="mt-4 flex flex-wrap gap-2">
      <li v-for="tag in post.tags" :key="tag.id">
        <TagPill :name="tag.name" :to="`/explore?tag=${encodeURIComponent(tag.slug)}`" />
      </li>
    </ul>

    <div class="mt-auto flex items-center justify-between border-t border-edge pt-4">
      <LikeButton
        :post-id="post.id"
        :liked="post.liked_by_current_user"
        :like-count="post.like_count"
        @change="emit('likeChange', $event)"
      />
      <span class="inline-flex items-center gap-1.5 text-xs text-ink-muted">
        <Clock class="h-3.5 w-3.5" aria-hidden="true" />
        {{ minutes }} min read
      </span>
    </div>
  </article>
</template>
