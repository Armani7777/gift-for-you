<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  videoId: string
  playing: boolean
}>()

const emit = defineEmits<{
  playing: []
  paused: []
}>()

type YTPlayer = {
  playVideo: () => void
  pauseVideo: () => void
  mute: () => void
  unMute: () => void
  setVolume: (value: number) => void
  seekTo: (seconds: number, allowSeekAhead: boolean) => void
  getCurrentTime: () => number
  getDuration: () => number
  getPlayerState: () => number
  destroy: () => void
}

const host = ref<HTMLDivElement | null>(null)
let player: YTPlayer | null = null
let watchTimer: number | null = null
let loopEnd = 109
const PLAYING = 1
const ENDED = 0
const ready = ref(false)
let pendingPlay = false

function play() {
  pendingPlay = true
  if (!player || !ready.value) return
  player.unMute()
  player.setVolume(100)
  player.playVideo()
}

function warm() {
  if (!player || !ready.value) return
  player.mute()
  player.playVideo()
}

function onUserGesture() {
  if (pendingPlay || props.playing) play()
}

function pause() {
  pendingPlay = false
  player?.pauseVideo()
}

defineExpose({ play, pause })

function clearWatch() {
  if (watchTimer) window.clearInterval(watchTimer)
  watchTimer = null
}

function restart() {
  player?.seekTo(0, true)
  player?.playVideo()
}

function ensureLoop() {
  if (!player || !props.playing) return
  const time = player.getCurrentTime()
  if (time >= loopEnd - 0.35) restart()
}

function loadApi() {
  return new Promise<void>((resolve) => {
    const w = window as Window & {
      YT?: { Player: new (el: HTMLElement, options: object) => YTPlayer }
      onYouTubeIframeAPIReady?: () => void
    }
    let settled = false
    const done = () => {
      if (settled) return
      settled = true
      resolve()
    }
    if (w.YT?.Player) {
      done()
      return
    }
    const previous = w.onYouTubeIframeAPIReady
    w.onYouTubeIframeAPIReady = () => {
      previous?.()
      done()
    }
    if (!document.querySelector('script[src="https://www.youtube.com/iframe_api"]')) {
      const script = document.createElement('script')
      script.src = 'https://www.youtube.com/iframe_api'
      document.head.appendChild(script)
    }
    const poll = window.setInterval(() => {
      if (w.YT?.Player) {
        window.clearInterval(poll)
        done()
      }
    }, 80)
    window.setTimeout(() => window.clearInterval(poll), 15000)
  })
}

onMounted(async () => {
  window.addEventListener('pointerdown', onUserGesture, true)
  if (!host.value) return
  await loadApi()
  const w = window as unknown as Window & { YT: { Player: new (el: HTMLElement, options: object) => YTPlayer } }
  player = new w.YT.Player(host.value, {
    videoId: props.videoId,
    width: 200,
    height: 200,
    playerVars: {
      autoplay: 1,
      mute: 1,
      controls: 0,
      disablekb: 1,
      fs: 0,
      modestbranding: 1,
      rel: 0,
      playsinline: 1,
      origin: window.location.origin,
    },
    events: {
      onReady: () => {
        ready.value = true
        const duration = player?.getDuration() || 0
        loopEnd = duration > 0 && duration <= 130 ? duration - 0.4 : 109
        if (pendingPlay || props.playing) play()
        else warm()
      },
      onStateChange: (event: { data: number }) => {
        if (event.data === ENDED) {
          restart()
          emit('playing')
          return
        }
        if (event.data === PLAYING) {
          emit('playing')
          clearWatch()
          watchTimer = window.setInterval(ensureLoop, 250)
          return
        }
        emit('paused')
        clearWatch()
      },
    },
  })
})

watch(
  () => props.playing,
  (next) => {
    if (next) play()
    else pause()
  },
)

onBeforeUnmount(() => {
  window.removeEventListener('pointerdown', onUserGesture, true)
  clearWatch()
  player?.destroy()
  player = null
})
</script>

<template>
  <div class="yt">
    <div ref="host" />
  </div>
</template>

<style scoped>
.yt {
  position: fixed;
  left: 8px;
  bottom: calc(8px + env(safe-area-inset-bottom));
  width: 54px;
  height: 54px;
  overflow: hidden;
  opacity: 0.02;
  pointer-events: none;
  z-index: 11;
}
</style>
