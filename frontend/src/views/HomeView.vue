<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

import AppButton from '@/components/common/AppButton.vue'
import PostList from '@/components/posts/PostList.vue'
import { usePostFeed } from '@/composables/usePostFeed'
import { postService } from '@/services/post.service'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const { posts, loading, loadingMore, error, hasMore, load, loadMore, applyLikeChange } =
  usePostFeed((page) => postService.list({ page, limit: 10 }))

onMounted(load)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl">
    <header class="mb-8">
      <h1 class="text-3xl font-semibold tracking-tight text-ink">Latest articles</h1>
      <p class="mt-1.5 text-emerald-100/70">
        Recent writing from developers about the tools they actually use.
      </p>
    </header>

    <PostList
      :posts="posts"
      :loading="loading"
      :loading-more="loadingMore"
      :error="error"
      :has-more="hasMore"
      empty-title="No posts yet."
      empty-description="Start sharing something you've learned."
      @load-more="loadMore"
      @retry="load"
      @like-change="applyLikeChange"
    >
      <template #empty-action>
        <AppButton
          v-if="auth.isAuthenticated"
          size="sm"
          @click="router.push({ name: 'write' })"
        >
          Write the first article
        </AppButton>
        <AppButton v-else size="sm" @click="router.push({ name: 'register' })">
          Create an account
        </AppButton>
      </template>
    </PostList>
  </div>
</template>
