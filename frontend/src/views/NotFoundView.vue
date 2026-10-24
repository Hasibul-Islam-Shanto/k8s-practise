<script setup lang="ts">
import { Compass } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

import AppButton from '@/components/common/AppButton.vue'
import StateMessage from '@/components/common/StateMessage.vue'

const router = useRouter()
</script>

<template>
  <div class="mx-auto max-w-lg py-10">
    <StateMessage
      title="Page not found."
      description="The page you were looking for doesn't exist."
    >
      <template #icon><Compass class="h-5 w-5" aria-hidden="true" /></template>
      <template #action>
        <AppButton variant="secondary" size="sm" @click="router.push({ name: 'home' })">
          Back to the feed
        </AppButton>
      </template>
    </StateMessage>
  </div>
</template>
