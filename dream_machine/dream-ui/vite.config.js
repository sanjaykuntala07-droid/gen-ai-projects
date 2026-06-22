import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',   // relative paths — required for Capacitor file:// loading
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    }
  },
  build: {
    outDir: '../www',          // output directly to capacitor www folder
    emptyOutDir: true,
  },
})
