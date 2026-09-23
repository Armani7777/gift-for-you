<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import InvitationExperience from '@/components/InvitationExperience.vue'
import { api, ApiError } from '@/services/api'
import type { InvitationPublic } from '@/types/invitation'

const route = useRoute()
const invitation = ref<InvitationPublic | null>(null)
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    invitation.value = await api.getInvitation(String(route.params.token))
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'This invitation is no longer available.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main>
    <div v-if="loading" class="page-shell skeleton" role="status">Preparing the invitation…</div>
    <div v-else-if="error" class="page-shell missing">
      <h1 class="display">This invitation is no longer available.</h1>
      <p class="muted">{{ error }}</p>
    </div>
    <InvitationExperience v-else-if="invitation" :invitation="invitation" />
  </main>
</template>

<style scoped>
.skeleton,
.missing {
  min-height: 100dvh;
  display: grid;
  place-content: center;
  text-align: center;
  gap: 12px;
}

.display {
  font-size: 2.2rem;
}
</style>
