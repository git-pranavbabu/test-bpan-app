import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    allowedHosts: [
      'spotted-trailside-reputable.ngrok-free.dev'
    ],

    proxy: {
      '/api': {
        target: 'http://bpan_api:8000',
        changeOrigin: true,
      },
    },
  },
})
