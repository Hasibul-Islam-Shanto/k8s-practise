<script setup lang="ts">
import { useWindowScroll } from '@vueuse/core'
import { Compass, Home, LogOut, Menu, PenLine, Search, User, X } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import UserAvatar from '@/components/common/UserAvatar.vue'
import AppLogo from '@/components/layout/AppLogo.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const mobileOpen = ref(false)
const search = ref('')
const { y } = useWindowScroll()
const scrolled = computed(() => y.value > 24)

watch(() => route.fullPath, () => (mobileOpen.value = false))

function submitSearch(): void {
  const query = search.value.trim()
  router.push({ name: 'explore', query: query ? { q: query } : {} })
}

function logout(): void {
  auth.logout()
  router.push({ name: 'home' })
}

const NAV_LINKS = [
  { name: 'home', label: 'Home', icon: Home },
  { name: 'explore', label: 'Explore', icon: Compass },
] as const

const linkClasses =
  'inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-ink-muted transition-colors hover:bg-emerald-500/10 hover:text-white'
const activeLinkClasses = 'bg-emerald-500/15 text-white'
</script>

<template>
  <header class="pointer-events-none fixed inset-x-0 top-3 z-50 px-4 sm:top-4">
    <div
      class="pointer-events-auto relative mx-auto max-w-6xl overflow-hidden rounded-2xl border border-edge bg-surface/70 shadow-xl shadow-black/30 ring-1 ring-emerald-500/20 backdrop-blur-xl transition-all duration-300 motion-safe:animate-header-glow"
      :class="scrolled ? 'scale-[0.98] shadow-2xl shadow-emerald-950/40' : ''"
    >
      <div
        class="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-400/70 to-transparent"
        aria-hidden="true"
      ></div>

      <div
        class="flex items-center gap-4 px-4 transition-all duration-300 sm:px-5"
        :class="scrolled ? 'h-14' : 'h-16'"
      >
        <RouterLink :to="{ name: 'home' }" class="group shrink-0" aria-label="TechBlog home">
          <AppLogo />
        </RouterLink>

        <nav class="hidden items-center gap-1 md:flex" aria-label="Main">
          <RouterLink
            v-for="link in NAV_LINKS"
            :key="link.name"
            :to="{ name: link.name }"
            :class="[linkClasses, route.name === link.name && activeLinkClasses]"
          >
            <component :is="link.icon" class="h-4 w-4" aria-hidden="true" />
            {{ link.label }}
          </RouterLink>
        </nav>

        <form class="ml-auto hidden max-w-xs flex-1 lg:block" role="search" @submit.prevent="submitSearch">
          <label for="header-search" class="sr-only">Search articles</label>
          <div class="relative">
            <Search
              class="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-ink-muted"
              aria-hidden="true"
            />
            <input
              id="header-search"
              v-model="search"
              type="search"
              placeholder="Search..."
              class="w-full rounded-lg border border-edge bg-black/30 py-2 pr-3 pl-9 text-sm text-white placeholder:text-ink-muted focus:border-emerald-400/50 focus:outline-none"
            />
          </div>
        </form>

        <div class="ml-auto flex items-center gap-2 lg:ml-0">
          <template v-if="auth.isAuthenticated">
            <RouterLink :to="{ name: 'write' }" :class="[linkClasses, 'hidden md:inline-flex']">
              <PenLine class="h-4 w-4" aria-hidden="true" />
              Write
            </RouterLink>
            <RouterLink
              :to="{ name: 'profile' }"
              class="hidden items-center gap-2 rounded-lg px-2 py-1.5 transition-colors hover:bg-emerald-500/10 md:inline-flex"
            >
              <UserAvatar
                :full-name="auth.user!.full_name"
                :username="auth.user!.username"
                :avatar-url="auth.user!.avatar_url"
                size="sm"
              />
              <span class="text-sm font-medium text-white">Profile</span>
            </RouterLink>
            <button
              type="button"
              :class="[linkClasses, 'hidden md:inline-flex']"
              aria-label="Log out"
              @click="logout"
            >
              <LogOut class="h-4 w-4" aria-hidden="true" />
            </button>
          </template>

          <template v-else>
            <RouterLink :to="{ name: 'login' }" :class="[linkClasses, 'hidden md:inline-flex']">
              Login
            </RouterLink>
            <RouterLink
              :to="{ name: 'register' }"
              class="gradient-accent hidden rounded-lg px-3 py-2 text-sm font-medium transition-opacity hover:opacity-90 md:inline-flex"
            >
              Create Account
            </RouterLink>
          </template>

          <button
            type="button"
            class="rounded-lg p-2 text-ink-muted transition-colors hover:bg-emerald-500/10 hover:text-white md:hidden"
            :aria-expanded="mobileOpen"
            aria-controls="mobile-nav"
            :aria-label="mobileOpen ? 'Close menu' : 'Open menu'"
            @click="mobileOpen = !mobileOpen"
          >
            <X v-if="mobileOpen" class="h-5 w-5" aria-hidden="true" />
            <Menu v-else class="h-5 w-5" aria-hidden="true" />
          </button>
        </div>
      </div>

      <nav
        v-if="mobileOpen"
        id="mobile-nav"
        class="border-t border-edge bg-black/30 px-4 pb-4 md:hidden"
        aria-label="Mobile"
      >
        <form class="py-3" role="search" @submit.prevent="submitSearch">
          <label for="mobile-search" class="sr-only">Search articles</label>
          <input
            id="mobile-search"
            v-model="search"
            type="search"
            placeholder="Search articles..."
            class="w-full rounded-lg border border-edge bg-black/30 px-3 py-2 text-sm text-white placeholder:text-ink-muted focus:border-emerald-400/50 focus:outline-none"
          />
        </form>

        <ul class="space-y-1">
          <li v-for="link in NAV_LINKS" :key="link.name">
            <RouterLink :to="{ name: link.name }" :class="[linkClasses, 'w-full']">
              <component :is="link.icon" class="h-4 w-4" aria-hidden="true" />
              {{ link.label }}
            </RouterLink>
          </li>

          <template v-if="auth.isAuthenticated">
            <li>
              <RouterLink :to="{ name: 'write' }" :class="[linkClasses, 'w-full']">
                <PenLine class="h-4 w-4" aria-hidden="true" />
                Write
              </RouterLink>
            </li>
            <li>
              <RouterLink :to="{ name: 'profile' }" :class="[linkClasses, 'w-full']">
                <User class="h-4 w-4" aria-hidden="true" />
                Profile
              </RouterLink>
            </li>
            <li>
              <button type="button" :class="[linkClasses, 'w-full']" @click="logout">
                <LogOut class="h-4 w-4" aria-hidden="true" />
                Log out
              </button>
            </li>
          </template>

          <template v-else>
            <li>
              <RouterLink :to="{ name: 'login' }" :class="[linkClasses, 'w-full']">Login</RouterLink>
            </li>
            <li>
              <RouterLink
                :to="{ name: 'register' }"
                class="gradient-accent mt-1 block rounded-lg px-3 py-2 text-center text-sm font-medium"
              >
                Create Account
              </RouterLink>
            </li>
          </template>
        </ul>
      </nav>
    </div>
  </header>
</template>
