<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/services/api'
import { formatPrettyDate, formatTime } from '@/services/share'
import type { GuestReply } from '@/types/invitation'

const replies = ref<GuestReply[]>([])
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    replies.value = await api.listReplies()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load answers.'
  } finally {
    loading.value = false
  }
})

function isVideo(reply: GuestReply) {
  return reply.finale_note_kind === 'video' && Boolean(reply.media_url)
}
</script>

<template>
  <main class="page-shell answers">
    <p class="eyebrow">Saved here</p>
    <h1 class="display">Her answers</h1>
    <p class="muted">Everything she chose is kept on this site. Audio and video notes are attached when she sends them.</p>
    <p v-if="loading">Loading…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="!replies.length" class="muted">No answers yet.</p>
    <article v-for="reply in replies" :key="reply.id" class="card">
      <p class="who">{{ reply.recipient_name || 'Guest' }} → {{ reply.sender_name || 'you' }}</p>
      <p v-if="reply.activities.length"><strong>Plan:</strong> {{ reply.activities.join(', ') }}</p>
      <p v-if="reply.selected_date">
        <strong>When:</strong>
        {{ formatPrettyDate(reply.selected_date) }}
        <template v-if="reply.selected_time"> · {{ formatTime(reply.selected_time) }}</template>
      </p>
      <p v-if="reply.finale_note"><strong>Note:</strong> {{ reply.finale_note }}</p>
      <video v-if="isVideo(reply)" class="media" :src="reply.media_url || ''" controls playsinline />
      <audio v-else-if="reply.media_url" class="media" :src="reply.media_url" controls />
    </article>
  </main>
</template>

<style scoped>
.answers {
  max-width: 560px;
  margin: 0 auto;
  display: grid;
  gap: 16px;
}
.display {
  font-size: clamp(2rem, 7vw, 3rem);
  margin: 0;
}
.card {
  padding: 20px;
  border-radius: 24px;
  background: var(--surface);
  border: 1px solid var(--line);
  display: grid;
  gap: 8px;
}
.who {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.3rem;
  margin: 0;
}
.media {
  width: 100%;
  border-radius: 16px;
  margin-top: 6px;
}
.error {
  color: var(--accent);
}
</style>
