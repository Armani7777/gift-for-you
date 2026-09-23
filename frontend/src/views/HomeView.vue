<script setup lang="ts">
import { RouterLink } from 'vue-router'
import AmbientEffects from '@/components/AmbientEffects.vue'
import Button from '@/components/Button.vue'
</script>

<template>
  <main class="landing page-shell">
    <AmbientEffects />
    <header class="hero">
      <p class="eyebrow">A small, private moment</p>
      <h1 class="display">Make asking them out a little more memorable.</h1>
      <p class="lede muted">
        Create a personalized interactive invitation, share one link, and let the moment unfold.
      </p>
      <div class="cta">
        <RouterLink to="/create">
          <Button>Create your invitation</Button>
        </RouterLink>
        <RouterLink to="/demo">
          <Button variant="ghost">Try a demo</Button>
        </RouterLink>
      </div>
    </header>

    <section class="preview-card" aria-hidden="true">
      <div class="orb" />
      <p class="eyebrow">A glimpse</p>
      <h2 class="display mini">Hey, Камила</h2>
      <p class="muted">I made something for you.</p>
      <span class="pill">Open</span>
    </section>

    <section>
      <p class="eyebrow">How it works</p>
      <ol class="steps">
        <li>
          <strong>Create</strong>
          <span>Write a short story and choose a date.</span>
        </li>
        <li>
          <strong>Share</strong>
          <span>Send one private link. No account needed for them.</span>
        </li>
        <li>
          <strong>Wait for their answer</strong>
          <span>See if they said yes, and when they’re free.</span>
        </li>
      </ol>
    </section>

    <section>
      <p class="eyebrow">What you can include</p>
      <ul class="features">
        <li>Personalized story</li>
        <li>Photos</li>
        <li>Music</li>
        <li>Interactive question</li>
        <li>Date planning</li>
        <li>Shareable link</li>
        <li>Mobile-first design</li>
      </ul>
    </section>
  </main>
</template>

<style scoped>
.landing {
  max-width: 760px;
  margin: 0 auto;
  display: grid;
  gap: 48px;
  position: relative;
  z-index: 1;
}

.hero {
  padding-top: 8vh;
  display: grid;
  gap: 18px;
}

.display {
  font-size: clamp(2.4rem, 7vw, 4.6rem);
  max-width: 11ch;
}

.lede {
  max-width: 34rem;
  font-size: 1.08rem;
}

.cta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.preview-card {
  width: min(100%, 360px);
  padding: 28px 24px;
  border-radius: 28px;
  background: color-mix(in srgb, var(--surface) 80%, transparent);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(16px);
}

.orb {
  position: absolute;
  right: -40px;
  top: -50px;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(124, 49, 67, 0.35), transparent 70%);
  animation: pulse 5s ease-in-out infinite;
}

.mini {
  font-size: 2.2rem;
}

.pill {
  display: inline-flex;
  margin-top: 16px;
  min-height: 40px;
  align-items: center;
  padding: 0 18px;
  border-radius: 999px;
  background: var(--accent);
  color: #fff;
}

.steps,
.features {
  padding: 0;
  margin: 16px 0 0;
  list-style: none;
  display: grid;
  gap: 14px;
}

.steps li,
.features li {
  padding: 16px 18px;
  border-radius: 18px;
  background: color-mix(in srgb, var(--surface) 82%, transparent);
  border: 1px solid var(--line);
  backdrop-filter: blur(10px);
}

.steps li {
  display: grid;
  gap: 4px;
}

.steps span,
.features li {
  color: var(--muted);
}

.features {
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}

@keyframes pulse {
  50% {
    transform: scale(1.12);
    opacity: 0.75;
  }
}

@media (max-width: 640px) {
  .hero {
    padding-top: 4vh;
  }
}
</style>
