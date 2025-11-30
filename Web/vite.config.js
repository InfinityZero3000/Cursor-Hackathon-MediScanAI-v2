import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    port: 3000,
    host: '0.0.0.0', // Cho phép truy cập từ mạng local (mobile)
    open: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})

