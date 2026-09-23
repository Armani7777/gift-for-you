import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  base: process.env.VITE_BASE || '/',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true,
    port: 5174,
    strictPort: true,
    allowedHosts: ['.trycloudflare.com', '.loca.lt', 'localhost'],
    proxy: {
      '/api': 'http://127.0.0.1:8010',
      '/media': 'http://127.0.0.1:8010',
    },
  },
})
