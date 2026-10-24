<script setup lang="ts">
import AppFooter from '@/components/layout/AppFooter.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <a
      href="#main"
      class="sr-only focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:z-50 focus:rounded-lg focus:gradient-accent focus:px-4 focus:py-2 focus:text-sm"
    >
      Skip to content
    </a>

    <AppHeader />

    <main id="main" class="mx-auto w-full max-w-6xl flex-1 px-4 pt-24 pb-8 sm:px-6 sm:pt-28">
      <!-- Views watch their own route params, so no remount key is needed here.
           Keying on the full path would remount Explore on every search keystroke. -->
      <RouterView />
    </main>

    <AppFooter />
  </div>
</template>
