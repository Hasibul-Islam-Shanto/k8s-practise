<script setup lang="ts">
import { BookOpen } from 'lucide-vue-next'
</script>

<template>
  <span class="inline-flex items-center gap-2.5">
    <span
      class="gradient-accent flex h-8 w-8 items-center justify-center rounded-lg shadow-md shadow-emerald-900/40 motion-safe:animate-logo-shimmer motion-reduce:animate-none"
    >
      <BookOpen
        class="h-4 w-4 text-white transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-6"
        aria-hidden="true"
      />
    </span>
    <span class="text-lg font-semibold tracking-tight">
      <span class="text-white">Tech</span><span class="bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">Blog</span>
    </span>
  </span>
</template>
