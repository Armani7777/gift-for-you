export function parseSpotifyTrackId(url: string): string | null {
  const value = url.trim()
  if (!value) return null
  const uri = value.match(/spotify:track:([a-zA-Z0-9]+)/i)
  if (uri) return uri[1]
  try {
    const parsed = new URL(value)
    const path = parsed.pathname.match(/track\/([a-zA-Z0-9]+)/)
    return path?.[1] ?? null
  } catch {
    const loose = value.match(/track[/:]([a-zA-Z0-9]+)/i)
    return loose?.[1] ?? null
  }
}

export function parseClockToSeconds(value: string): number {
  const trimmed = value.trim()
  if (!trimmed) return 0
  if (/^\d+$/.test(trimmed)) return Number(trimmed)
  const parts = trimmed.split(':').map((part) => Number(part))
  if (parts.some((part) => Number.isNaN(part))) return 0
  if (parts.length === 2) return parts[0] * 60 + parts[1]
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2]
  return 0
}

export function formatSeconds(total: number): string {
  const safe = Math.max(0, Math.floor(total))
  const minutes = Math.floor(safe / 60)
  const seconds = safe % 60
  return `${minutes}:${String(seconds).padStart(2, '0')}`
}

export function spotifyEmbedUrl(trackId: string): string {
  return `https://open.spotify.com/embed/track/${trackId}?utm_source=generator&theme=0`
}
