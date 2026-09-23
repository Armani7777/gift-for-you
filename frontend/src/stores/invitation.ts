import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { InvitationPublic } from '@/types/invitation'

export const useInvitationStore = defineStore('invitation', () => {
  const current = ref<InvitationPublic | null>(null)

  function setInvitation(invitation: InvitationPublic | null) {
    current.value = invitation
  }

  return { current, setInvitation }
})
