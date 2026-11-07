import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// /api ile başlayan istekler backend konteynerine yönlendirilir.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    watch: { usePolling: true }, // Windows + Docker'da dosya değişikliğini algılamak için
    proxy: {
      '/api': process.env.VITE_API_HEDEF || 'http://localhost:8000',
    },
  },
})
