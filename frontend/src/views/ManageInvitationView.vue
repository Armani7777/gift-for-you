<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import Button from '@/components/Button.vue'
import { api, ApiError } from '@/services/api'
import { copyText, formatPrettyDate, formatTime, invitationUrl, shareLink } from '@/services/share'
import type { InvitationManage } from '@/types/invitation'

const route = useRoute()
const invitation = ref<InvitationManage | null>(null)
const error = ref('')
const notice = ref('')
const loading = ref(true)
const fresh = computed(() => route.query.fresh === '1')
const publicLink = computed(() => (invitation.value ? invitationUrl(invitation.value.public_token) : ''))

const statusLabel = computed(() => {
  const map: Record<string, string> = {
    created: 'Created',
    opened: 'Opened',
    accepted: 'Accepted',
    declined: 'Declined',
    planning: 'Planning completed',
    confirmed: 'Confirmed',
  }
  return invitation.value ? map[invitation.value.status] : ''
})

onMounted(async () => {
  try {
    invitation.value = await api.getManaged(String(route.params.token), String(route.params.managementToken))
    notice.value = fresh.value ? 'Your invitation is ready' : ''
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'You do not have access to this invitation.'
  } finally {
    loading.value = false
  }
})

async function copy() {
  if (!publicLink.value) return
  notice.value = (await copyText(publicLink.value)) ? 'Link copied' : 'Could not copy the link'
}

async function share() {
  if (!invitation.value) return
  const result = await shareLink(`Invitation for ${invitation.value.recipient_name}`, publicLink.value)
  if (result === 'copied') notice.value = 'Link copied'
}
</script>

<template>
  <main class="manage page-shell">
    <div v-if="loading">Loading invitation…</div>
    <div v-else-if="error" class="stack">
      <h1 class="display">This invitation is no longer available.</h1>
      <p class="muted">{{ error }}</p>
    </div>
    <section v-else-if="invitation" class="stack">
      <p class="eyebrow">{{ fresh ? 'Ready to share' : 'Invitation' }}</p>
      <h1 class="display">{{ invitation.recipient_name }}</h1>
      <p v-if="notice" class="notice">{{ notice }}</p>

      <div class="card">
        <p class="muted">Share link</p>
        <p class="link">{{ publicLink }}</p>
        <div class="actions">
          <Button @click="copy">Copy link</Button>
          <Button variant="secondary" @click="share">Share</Button>
          <RouterLink :to="`/i/${invitation.public_token}`">
            <Button variant="ghost">Open invitation</Button>
          </RouterLink>
        </div>
      </div>

      <div class="card">
        <p><strong>Status:</strong> {{ statusLabel }}</p>
        <p v-if="invitation.response?.selected_activities?.length">
          <strong>Activity:</strong>
          {{ invitation.response.selected_activities.map((item) => item.name).join(', ') }}
        </p>
        <p v-if="invitation.response?.selected_date">
          <strong>Date:</strong> {{ formatPrettyDate(invitation.response.selected_date) }}
        </p>
        <p v-if="invitation.response?.selected_time">
          <strong>Time:</strong> {{ formatTime(invitation.response.selected_time) }}
        </p>
        <p v-if="invitation.response?.finale_note">
          <strong>Letter:</strong> {{ invitation.response.finale_note }}
        </p>
        <video
          v-if="invitation.response?.finale_note_kind === 'video' && invitation.response.finale_note_media_url"
          class="media"
          :src="invitation.response.finale_note_media_url"
          controls
          playsinline
        />
        <audio
          v-else-if="invitation.response?.finale_note_media_url"
          class="media"
          :src="invitation.response.finale_note_media_url"
          controls
        />
        <p v-if="invitation.response?.answer === 'declined'" class="muted">
          They chose not this time.
          <template v-if="invitation.response.decline_reason">
            Reason: {{ invitation.response.decline_reason }}
          </template>
        </p>
      </div>
    </section>
  </main>
</template>

<style scoped>
.manage {
  max-width: 560px;
  margin: 0 auto;
}

.display {
  font-size: clamp(2rem, 7vw, 3rem);
}

.card {
  padding: 20px;
  border-radius: 24px;
  background: var(--surface);
  border: 1px solid var(--line);
  display: grid;
  gap: 10px;
}

.link {
  word-break: break-all;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.notice {
  color: var(--accent);
}

.media {
  width: 100%;
  border-radius: 16px;
}
</style>
