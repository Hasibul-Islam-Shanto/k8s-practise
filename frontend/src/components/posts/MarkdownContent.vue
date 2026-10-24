<script setup lang="ts">
import { computed } from 'vue'

import { renderMarkdown } from '@/utils/markdown'

const props = defineProps<{ source: string }>()

const html = computed(() => renderMarkdown(props.source))
</script>

<template>
  <div v-if="source.trim()" class="article-body" v-html="html"></div>
  <p v-else class="text-sm text-ink-muted">Nothing to preview yet.</p>
</template>
