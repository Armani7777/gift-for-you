import { assetUrl } from '@/services/assets'

export const giftImages = [
  'art/remember-this-day.png',
  'art/bears-hug.png',
  'art/bear-heart.png',
  'art/bear-yay.png',
]

export const giftMusic = 'music/love-story.mp3'

export function giftImageUrls() {
  return giftImages.map((path) => assetUrl(path))
}

export function giftMusicUrl() {
  return assetUrl(giftMusic)
}

function decodeImage(src: string) {
  const image = new Image()
  image.src = src
  if (image.decode) return image.decode().catch(() => undefined)
  return new Promise<void>((resolve) => {
    image.onload = () => resolve()
    image.onerror = () => resolve()
  })
}

function warmAudio(src: string) {
  const audio = new Audio()
  audio.preload = 'auto'
  audio.src = src
  return new Promise<void>((resolve) => {
    const done = () => resolve()
    audio.addEventListener('canplaythrough', done, { once: true })
    audio.addEventListener('error', done, { once: true })
    window.setTimeout(done, 8000)
    audio.load()
  })
}

export function localAssetUrls(urls: Array<string | null | undefined>) {
  return urls.filter((src): src is string => typeof src === 'string' && !/^https?:\/\//.test(src))
}

export function preloadGiftAssets(extra: Array<string | null | undefined> = []) {
  const images = [...new Set([...giftImageUrls(), ...localAssetUrls(extra)])]
  return Promise.all([...images.map(decodeImage), warmAudio(giftMusicUrl())])
}
