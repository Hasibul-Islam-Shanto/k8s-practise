<script setup lang="ts">
import { CircleAlert, UserX } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppButton from '@/components/common/AppButton.vue'
import StateMessage from '@/components/common/StateMessage.vue'
import PostList from '@/components/posts/PostList.vue'
import ProfileHeader from '@/components/profile/ProfileHeader.vue'
import ProfileSkeleton from '@/components/profile/ProfileSkeleton.vue'
import { usePostFeed } from '@/composables/usePostFeed'
import { errorMessage } from '@/services/api'
import { userService } from '@/services/user.service'
import { useAuthStore } from '@/stores/auth'
import type { UserProfile } from '@/types/user'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

/** This view backs both `/profile` and `/users/:username`. */
const username = computed(() =>
  route.name === 'profile' ? (auth.user?.username ?? '') : (route.params.username as string),
)
const isOwnProfile = computed(
  () => Boolean(auth.user) && auth.user!.username === username.value.toLowerCase(),
)

const profile = ref<UserProfile | null>(null)
const loading = ref(true)
const loadError = ref('')
const notFound = ref(false)

const { posts, loading: postsLoading, loadingMore, error: postsError, hasMore, load: loadPosts, loadMore, applyLikeChange } =
  usePostFeed((page) => userService.posts(username.value, page, 10))

async function loadProfile(): Promise<void> {
  if (!username.value) return
  loading.value = true
  loadError.value = ''
  notFound.value = false
  try {
    profile.value = await userService.profile(username.value)
    document.title = `${profile.value.full_name} (@${profile.value.username}) — TechBlog`
  } catch (err) {
    profile.value = null
    const status = (err as { response?: { status?: number } }).response?.status
    if (status === 404) notFound.value = true
    else loadError.value = errorMessage(err, 'Please try again.')
  } finally {
    loading.value = false
  }
}

async function loadAll(): Promise<void> {
  await loadProfile()
  if (profile.value) await loadPosts()
}

onMounted(loadAll)
watch(username, loadAll)

const emptyTitle = computed(() =>
  isOwnProfile.value ? "You haven't published anything yet." : "This user hasn't published anything yet.",
)
const emptyDescription = computed(() =>
  isOwnProfile.value ? 'Write your first article to see it here.' : '',
)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl">
    <ProfileSkeleton v-if="loading" />

    <StateMessage
      v-else-if="notFound"
      title="This user doesn't exist."
      description="Check the username and try again."
    >
      <template #icon><UserX class="h-5 w-5" aria-hidden="true" /></template>
      <template #action>
        <AppButton variant="secondary" size="sm" @click="router.push({ name: 'home' })">
          Back to the feed
        </AppButton>
      </template>
    </StateMessage>

    <StateMessage
      v-else-if="loadError"
      tone="error"
      title="Unable to load this profile."
      :description="loadError"
    >
      <template #icon><CircleAlert class="h-5 w-5" aria-hidden="true" /></template>
      <template #action>
        <AppButton variant="secondary" size="sm" @click="loadAll">Try again</AppButton>
      </template>
    </StateMessage>

    <template v-else-if="profile">
      <ProfileHeader
        :profile="profile"
        :is-own-profile="isOwnProfile"
        @edit="router.push({ name: 'profile-edit' })"
      />

      <hr class="my-10 border-edge" />

      <h2 class="mb-5 text-lg font-semibold tracking-tight text-ink">Posts</h2>

      <PostList
        :posts="posts"
        :loading="postsLoading"
        :loading-more="loadingMore"
        :error="postsError"
        :has-more="hasMore"
        :empty-title="emptyTitle"
        :empty-description="emptyDescription"
        :skeleton-count="2"
        @load-more="loadMore"
        @retry="loadPosts"
        @like-change="applyLikeChange"
      >
        <template #empty-action>
          <AppButton v-if="isOwnProfile" size="sm" @click="router.push({ name: 'write' })">
            Write an article
          </AppButton>
        </template>
      </PostList>
    </template>
  </div>
</template>
