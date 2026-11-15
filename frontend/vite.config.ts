import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // In development, forward /api calls to the FastAPI server.
  server: { proxy: { '/api': 'http://localhost:8000' } },
})
