import type { CreateInvitationPayload, CreatedInvitation, GuestReply, InvitationManage, InvitationPublic, RecipientResponse } from '@/types/invitation'

class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function readError(response: Response): Promise<string> {
  try {
    const data = await response.json()
    if (data?.error) return String(data.error)
    const first = data && typeof data === 'object' ? Object.values(data)[0] : null
    if (Array.isArray(first)) return String(first[0])
    if (first) return String(first)
  } catch {
    /* ignore malformed payloads */
  }
  if (response.status === 404) return 'This invitation is no longer available.'
  return 'Something went wrong. Please try again.'
}

async function request<T>(input: string, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init)
  if (!response.ok) {
    throw new ApiError(await readError(response), response.status)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return response.json() as Promise<T>
}

export const api = {
  health() {
    return request<{ status: string }>('/api/health/')
  },
  createInvitation(payload: CreateInvitationPayload) {
    return request<CreatedInvitation>('/api/invitations/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  },
  getInvitation(token: string) {
    return request<InvitationPublic>(`/api/invitations/${token}/`)
  },
  openInvitation(token: string) {
    return request<InvitationPublic>(`/api/invitations/${token}/open/`, { method: 'POST' })
  },
  submitResponse(token: string, answer: 'accepted' | 'declined', declineReason = '') {
    return request<RecipientResponse>(`/api/invitations/${token}/response/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer, decline_reason: declineReason }),
    })
  },
  savePlan(token: string, payload: { activity_ids?: number[]; date_id?: number; date?: string; time?: string }) {
    return request<RecipientResponse>(`/api/invitations/${token}/plan/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  },
  confirm(token: string) {
    return request<RecipientResponse>(`/api/invitations/${token}/confirm/`, { method: 'POST' })
  },
  submitReply(payload: {
    session_key: string
    source?: string
    public_token?: string
    recipient_name?: string
    sender_name?: string
    answer?: string
    activities?: string[]
    selected_date?: string
    selected_time?: string
    finale_note?: string
    finale_note_kind?: string
    media?: File
  }) {
    const body = new FormData()
    body.append('session_key', payload.session_key)
    if (payload.source) body.append('source', payload.source)
    if (payload.public_token) body.append('public_token', payload.public_token)
    if (payload.recipient_name) body.append('recipient_name', payload.recipient_name)
    if (payload.sender_name) body.append('sender_name', payload.sender_name)
    if (payload.answer) body.append('answer', payload.answer)
    if (payload.activities?.length) body.append('activities', JSON.stringify(payload.activities))
    if (payload.selected_date) body.append('selected_date', payload.selected_date)
    if (payload.selected_time) body.append('selected_time', payload.selected_time)
    if (payload.finale_note) body.append('finale_note', payload.finale_note)
    if (payload.finale_note_kind) body.append('finale_note_kind', payload.finale_note_kind)
    if (payload.media) body.append('media', payload.media)
    return request<GuestReply>('/api/replies/', { method: 'POST', body })
  },
  listReplies() {
    return request<GuestReply[]>('/api/replies/')
  },
  saveNote(token: string, payload: { text?: string; kind?: string; file?: File }) {
    if (payload.file) {
      const body = new FormData()
      body.append('text', payload.text || '')
      body.append('kind', payload.kind || 'text')
      body.append('media', payload.file)
      return request<RecipientResponse>(`/api/invitations/${token}/note/`, {
        method: 'POST',
        body,
      })
    }
    return request<RecipientResponse>(`/api/invitations/${token}/note/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: payload.text || '', kind: payload.kind || 'text' }),
    })
  },
  getManaged(publicToken: string, managementToken: string) {
    return request<InvitationManage>(`/api/manage/${publicToken}/${managementToken}/`)
  },
  uploadPhoto(publicToken: string, managementToken: string, file: File, caption = '') {
    const body = new FormData()
    body.append('image', file)
    body.append('caption', caption)
    return request<InvitationManage>(`/api/manage/${publicToken}/${managementToken}/photos/`, {
      method: 'POST',
      body,
    })
  },
  uploadMemoryImage(publicToken: string, managementToken: string, memoryId: number, file: File) {
    const body = new FormData()
    body.append('memory_id', String(memoryId))
    body.append('image', file)
    return request<InvitationManage>(`/api/manage/${publicToken}/${managementToken}/memories/`, {
      method: 'POST',
      body,
    })
  },
  uploadMusic(publicToken: string, managementToken: string, file: File) {
    const body = new FormData()
    body.append('music', file)
    return request<InvitationManage>(`/api/manage/${publicToken}/${managementToken}/music/`, {
      method: 'POST',
      body,
    })
  },
}

export { ApiError }
